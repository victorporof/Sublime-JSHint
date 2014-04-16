# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import sublime, sublime_plugin
import os, sys, subprocess, codecs, re, webbrowser
from threading import Timer

try:
  import commands
except ImportError:
  pass

PLUGIN_FOLDER = os.path.dirname(os.path.realpath(__file__))
RC_FILE = ".jshintrc"
SETTINGS_FILE = "JSHint.sublime-settings"
KEYMAP_FILE = "Default ($PLATFORM).sublime-keymap"
OUTPUT_VALID = b"*** JSHint output ***"

class JshintCommand(sublime_plugin.TextCommand):
  def run(self, edit, show_regions=True, show_panel=True):
    JshintListener.reset()

    # Make sure we're only linting javascript files.
    filePath = self.view.file_name()
    hasJsExtension = filePath != None and bool(re.search(r'\.jsm?$', filePath))
    hasJsSyntax = bool(re.search("JavaScript", self.view.settings().get("syntax"), re.I))
    hasJsonSyntax = bool(re.search("JSON", self.view.settings().get("syntax"), re.I))
    if hasJsonSyntax or (not hasJsExtension and not hasJsSyntax):
      return

    if PLUGIN_FOLDER.find(u".sublime-package") != -1:
      # Can't use this plugin if installed via the Package Manager in Sublime
      # Text 3, because it will be zipped into a .sublime-package archive.
      # Thus executing scripts *located inside this archive* via node.js
      # will, unfortunately, not be possible.
      url = "https://github.com/victorporof/Sublime-JSHint#manually"
      msg = """You won't be able to use this plugin in Sublime Text 3 when \
installed via the Package Manager.\n\nPlease remove it and install manually, \
following the instructions at:\n"""
      sublime.ok_cancel_dialog(msg + url)
      webbrowser.open(url)
      return

    # Get the current text in the buffer.
    bufferText = self.view.substr(sublime.Region(0, self.view.size()))
    # ...and save it in a temporary file. This allows for scratch buffers
    # and dirty files to be linted as well.
    namedTempFile = ".__temp__"
    tempPath = PLUGIN_FOLDER + "/" + namedTempFile
    print("Saving buffer to: " + tempPath)
    f = codecs.open(tempPath, mode='w', encoding='utf-8')
    f.write(bufferText)
    f.close()

    # Simply using `node` without specifying a path sometimes doesn't work :(
    settings = sublime.load_settings(SETTINGS_FILE)
    if exists_in_path("nodejs"):
      node = "nodejs"
    elif exists_in_path("node"):
      node = "node"
    else:
      node = settings.get("node_path")

    output = ""
    try:
      print("Plugin folder is: " + PLUGIN_FOLDER)
      scriptPath = PLUGIN_FOLDER + "/scripts/run.js"
      output = get_output([node, scriptPath, tempPath, filePath or "?"])

      # Make sure the correct/expected output is retrieved.
      if output.find(OUTPUT_VALID) == -1:
        print(output)
        cmd = node + " " + scriptPath + " " + tempPath + " " + filePath
        msg = "Command " + cmd + " created invalid output"
        raise Exception(msg)

    except:
      # Something bad happened.
      print("Unexpected error({0}): {1}".format(sys.exc_info()[0], sys.exc_info()[1]))

      # Usually, it's just node.js not being found. Try to alleviate the issue.
      msg = "Node.js was not found in the default path. Please specify the location."
      if sublime.ok_cancel_dialog(msg):
        open_jshint_sublime_settings(self.view.window())
      else:
        msg = "You won't be able to use this plugin without specifying the path to Node.js."
        sublime.error_message(msg)
      return

    # Remove the output identification marker (first line).
    output = output[len(OUTPUT_VALID) + 1:]

    # We're done with linting, rebuild the regions shown in the current view.
    self.view.erase_regions("jshint_errors")
    os.remove(tempPath)

    if len(output) > 0:
      regions = []
      menuitems = []

      # For each line of jshint output (errors, warnings etc.) add a region
      # in the view and a menuitem in a quick panel.
      for line in output.decode().splitlines():
        try:
          lineNo, columnNo, description = line.split(" :: ")
        except:
          continue

        symbolname = re.match("('[^']+')", description)

        text_point = self.view.text_point(int(lineNo) - 1, int(columnNo) - 1)
        region = self.view.word(text_point)

        if symbolname:
          region = self.view.word(text_point)
        else:
          region = self.view.line(text_point)

        menuitems.append(lineNo + ":" + columnNo + " " + description)

        regions.append(region)
        JshintListener.errors.append((region, description))

      if show_regions:
        self.add_regions(regions)
      if show_panel:
        self.view.window().show_quick_panel(menuitems, self.on_chosen)

  def add_regions(self, regions):
    packageName = (PLUGIN_FOLDER.split(os.path.sep))[-1]

    if int(sublime.version()) >= 3000:
      icon = "Packages/" + packageName + "/warning.png"
      self.view.add_regions("jshint_errors", regions, "keyword", icon,
        sublime.DRAW_EMPTY |
        sublime.DRAW_NO_FILL |
        sublime.DRAW_NO_OUTLINE |
        sublime.DRAW_SQUIGGLY_UNDERLINE |
        sublime.HIDE_ON_MINIMAP)
    else:
      icon = ".." + os.path.sep + packageName + os.path.sep + "warning"
      self.view.add_regions("jshint_errors", regions, "keyword", icon,
        sublime.DRAW_EMPTY |
        sublime.DRAW_OUTLINED |
        sublime.HIDE_ON_MINIMAP)

  def on_chosen(self, index):
    if index == -1:
      return

    # Focus the user requested region from the quick panel.
    region = JshintListener.errors[index][0]
    region_cursor = sublime.Region(region.begin(), region.begin())
    selection = self.view.sel()
    selection.clear()
    selection.add(region_cursor)
    self.view.show(region_cursor)

    if not sublime.load_settings(SETTINGS_FILE).get("highlight_selected_regions"):
      return

    self.view.erase_regions("jshint_selected")
    self.view.add_regions("jshint_selected", [region], "meta")

class JshintSetLintingPrefsCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    open_jshint_rc(self.view.window())

class JshintSetPluginOptionsCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    open_jshint_sublime_settings(self.view.window())

class JshintSetKeyboardShortcutsCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    open_jshint_sublime_keymap(self.view.window(), {
      "windows": "Windows", "linux": "Linux", "osx": "OSX"
    }.get(sublime.platform()))

class JshintSetNodePathCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    open_jshint_sublime_settings(self.view.window())

class JshintClearAnnotationsCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    JshintListener.reset()
    self.view.erase_regions("jshint_errors")
    self.view.erase_regions("jshint_selected")

class JshintListener(sublime_plugin.EventListener):
  timer = None
  errors = []

  @staticmethod
  def reset():
    self = JshintListener

    # Invalidate any previously set timer.
    if self.timer != None:
      self.timer.cancel()

    self.timer = None
    self.errors = []

  @staticmethod
  def on_modified(view):
    self = JshintListener
    plugin_settings = sublime.load_settings(SETTINGS_FILE)

    # Continue only if the plugin settings allow this to happen.
    # This is only available in Sublime 3.
    if int(sublime.version()) < 3000:
      return
    if not plugin_settings.get("lint_on_edit"):
      return

    # Re-run the jshint command after a second of inactivity after the view
    # has been modified, to avoid regions getting out of sync with the actual
    # previously linted source code.
    if self.timer != None:
      self.timer.cancel()

    timeout = plugin_settings.get("lint_on_edit_timeout")
    self.timer = Timer(timeout, lambda: view.window().run_command("jshint", { "show_panel": False }))
    self.timer.start()

  @staticmethod
  def on_post_save(view):
    # Continue only if the current plugin settings allow this to happen.
    if sublime.load_settings(SETTINGS_FILE).get("lint_on_save"):
      view.window().run_command("jshint", { "show_panel": False })

  @staticmethod
  def on_load(view):
    # Continue only if the current plugin settings allow this to happen.
    if sublime.load_settings(SETTINGS_FILE).get("lint_on_load"):
      v = view.window() if int(sublime.version()) < 3000 else view
      v.run_command("jshint", { "show_panel": False })

  @staticmethod
  def on_selection_modified(view):
    display_to_status_bar(view, JshintListener.errors)

def open_jshint_rc(window):
  window.open_file(PLUGIN_FOLDER + "/" + RC_FILE)

def open_jshint_sublime_settings(window):
  window.open_file(PLUGIN_FOLDER + "/" + SETTINGS_FILE)

def open_jshint_sublime_keymap(window, platform):
  window.open_file(PLUGIN_FOLDER + "/" + KEYMAP_FILE.replace("$PLATFORM", platform))

def exists_in_path(cmd):
  # Can't search the path if a directory is specified.
  assert not os.path.dirname(cmd)
  path = os.environ.get("PATH", "").split(os.pathsep)
  extensions = os.environ.get("PATHEXT", "").split(os.pathsep)

  # For each directory in PATH, check if it contains the specified binary.
  for directory in path:
    base = os.path.join(directory, cmd)
    options = [base] + [(base + ext) for ext in extensions]
    for filename in options:
      if os.path.exists(filename):
        return True

  return False

def get_output(cmd):
  if int(sublime.version()) < 3000:
    if sublime.platform() != "windows":
      # Handle Linux and OS X in Python 2.
      run = '"' + '" "'.join(cmd) + '"'
      return commands.getoutput(run)
    else:
      # Handle Windows in Python 2.

      # Hack to prevent console window from showing. Stolen from
      # http://stackoverflow.com/questions/1813872/running-a-process-in-pythonw-with-popen-without-a-console
      startupinfo = subprocess.STARTUPINFO()
      startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

      return subprocess.Popen(cmd, stdout=subprocess.PIPE, startupinfo=startupinfo).communicate()[0]
  else:
    # Handle all OS in Python 3.
    run = '"' + '" "'.join(cmd) + '"'
    return subprocess.check_output(run, stderr=subprocess.STDOUT, shell=True)

def display_to_status_bar(view, regions_to_descriptions):
  caret_region = view.sel()[0]

  for message_region, message_text in regions_to_descriptions:
    if message_region.intersects(caret_region):
      sublime.status_message(message_text)
      return
  else:
    sublime.status_message("")
