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
    # Make sure we're only linting javascript files.
    if self.file_unsupported():
      return

    # Get the current text in the buffer and save it in a temporary file.
    # This allows for scratch buffers and dirty files to be linted as well.
    temp_file_path = self.save_buffer_to_temp_file()
    output = self.run_script_on_file(temp_file_path)
    os.remove(temp_file_path)

    # Dump any diagnostics and get the output after the identification marker.
    if PluginUtils.get_pref('print_diagnostics'):
      print(self.get_output_diagnostics(output))
    output = self.get_output_data(output)

    # We're done with linting, rebuild the regions shown in the current view.
    JshintGlobalStore.reset()
    JshintEventListeners.reset()
    self.view.erase_regions("jshint_errors")

    regions = []
    menuitems = []

    # For each line of jshint output (errors, warnings etc.) add a region
    # in the view and a menuitem in a quick panel.
    for line in output.splitlines():
      try:
        line_no, column_no, description = line.split(" :: ")
      except:
        continue

      symbol_name = re.match("('[^']+')", description)
      hint_point = self.view.text_point(int(line_no) - 1, int(column_no if column_no != "NaN" else "1") - 1)
      if symbol_name:
        hint_region = self.view.word(hint_point)
      else:
        hint_region = self.view.line(hint_point)

      regions.append(hint_region)
      menuitems.append(line_no + ":" + column_no + " " + description)
      JshintGlobalStore.errors.append((hint_region, description))

    if show_regions:
      self.add_regions(regions)
    if show_panel:
      self.view.window().show_quick_panel(menuitems, self.on_quick_panel_selection)

  def file_unsupported(self):
    file_path = self.view.file_name()
    view_settings = self.view.settings()
    has_js_or_html_extension = file_path != None and bool(re.search(r'\.(jsm?|html?)$', file_path))
    has_js_or_html_syntax = bool(re.search(r'JavaScript|HTML', view_settings.get("syntax"), re.I))
    has_json_syntax = bool(re.search("JSON", view_settings.get("syntax"), re.I))
    return has_json_syntax or (not has_js_or_html_extension and not has_js_or_html_syntax)

  def save_buffer_to_temp_file(self):
    buffer_text = self.view.substr(sublime.Region(0, self.view.size()))
    temp_file_name = ".__temp__"
    temp_file_path = PLUGIN_FOLDER + "/" + temp_file_name
    f = codecs.open(temp_file_path, mode="w", encoding="utf-8")
    f.write(buffer_text)
    f.close()
    return temp_file_path

  def run_script_on_file(self, temp_file_path):
    try:
      node_path = PluginUtils.get_node_path()
      script_path = PLUGIN_FOLDER + "/scripts/run.js"
      file_path = self.view.file_name()
      cmd = [node_path, script_path, temp_file_path, file_path or "?"]
      output = PluginUtils.get_output(cmd)

      # Make sure the correct/expected output is retrieved.
      if output.find(OUTPUT_VALID) != -1:
        return output

      msg = "Command " + '" "'.join(cmd) + " created invalid output."
      print(output)
      raise Exception(msg)

    except:
      # Something bad happened.
      print("Unexpected error({0}): {1}".format(sys.exc_info()[0], sys.exc_info()[1]))

      # Usually, it's just node.js not being found. Try to alleviate the issue.
      msg = "Node.js was not found in the default path. Please specify the location."
      if not sublime.ok_cancel_dialog(msg):
        msg = "You won't be able to use this plugin without specifying the path to node.js."
        sublime.error_message(msg)
      else:
        PluginUtils.open_sublime_settings(self.view.window())

  def get_output_diagnostics(self, output):
    index = output.find(OUTPUT_VALID)
    return output[:index].decode("utf-8")

  def get_output_data(self, output):
    index = output.find(OUTPUT_VALID)
    return output[index + len(OUTPUT_VALID) + 1:].decode("utf-8")

  def add_regions(self, regions):
    package_name = (PLUGIN_FOLDER.split(os.path.sep))[-1]

    if int(sublime.version()) >= 3000:
      icon = "Packages/" + package_name + "/warning.png"
      self.view.add_regions("jshint_errors", regions, "keyword", icon,
        sublime.DRAW_EMPTY |
        sublime.DRAW_NO_FILL |
        sublime.DRAW_NO_OUTLINE |
        sublime.DRAW_SQUIGGLY_UNDERLINE)
    else:
      icon = ".." + os.path.sep + package_name + os.path.sep + "warning"
      self.view.add_regions("jshint_errors", regions, "keyword", icon,
        sublime.DRAW_EMPTY |
        sublime.DRAW_OUTLINED)

  def on_quick_panel_selection(self, index):
    if index == -1:
      return

    # Focus the user requested region from the quick panel.
    region = JshintGlobalStore.errors[index][0]
    region_cursor = sublime.Region(region.begin(), region.begin())
    selection = self.view.sel()
    selection.clear()
    selection.add(region_cursor)
    self.view.show(region_cursor)

    if not PluginUtils.get_pref("highlight_selected_regions"):
      return

    self.view.erase_regions("jshint_selected")
    self.view.add_regions("jshint_selected", [region], "meta")

class JshintGlobalStore:
  errors = []

  @classmethod
  def reset(self):
    self.errors = []

class JshintEventListeners(sublime_plugin.EventListener):
  timer = None

  @classmethod
  def reset(self):
    # Invalidate any previously set timer.
    if self.timer != None:
      self.timer.cancel()
      self.timer = None

  @classmethod
  def on_modified(self, view):
    # Continue only if the plugin settings allow this to happen.
    # This is only available in Sublime 3.
    if int(sublime.version()) < 3000:
      return
    if not PluginUtils.get_pref("lint_on_edit"):
      return

    # Re-run the jshint command after a second of inactivity after the view
    # has been modified, to avoid regions getting out of sync with the actual
    # previously linted source code.
    self.reset()

    timeout = PluginUtils.get_pref("lint_on_edit_timeout")
    self.timer = Timer(timeout, lambda: view.window().run_command("jshint", { "show_panel": False }))
    self.timer.start()

  @staticmethod
  def on_post_save(view):
    # Continue only if the current plugin settings allow this to happen.
    if PluginUtils.get_pref("lint_on_save"):
      view.window().run_command("jshint", { "show_panel": False })

  @staticmethod
  def on_load(view):
    # Continue only if the current plugin settings allow this to happen.
    if PluginUtils.get_pref("lint_on_load"):
      v = view.window() if int(sublime.version()) < 3000 else view
      v.run_command("jshint", { "show_panel": False })

  @staticmethod
  def on_selection_modified(view):
    caret_region = view.sel()[0]

    for message_region, message_text in JshintGlobalStore.errors:
      if message_region.intersects(caret_region):
        sublime.status_message(message_text)
        return
    else:
      sublime.status_message("")

class JshintSetLintingPrefsCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    PluginUtils.open_config_rc(self.view.window())

class JshintSetPluginOptionsCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    PluginUtils.open_sublime_settings(self.view.window())

class JshintSetKeyboardShortcutsCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    PluginUtils.open_sublime_keymap(self.view.window(), {
      "windows": "Windows",
      "linux": "Linux",
      "osx": "OSX"
    }.get(sublime.platform()))

class JshintSetNodePathCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    PluginUtils.open_sublime_settings(self.view.window())

class JshintClearAnnotationsCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    JshintEventListeners.reset()
    self.view.erase_regions("jshint_errors")
    self.view.erase_regions("jshint_selected")

class PluginUtils:
  @staticmethod
  def get_pref(key):
    return sublime.load_settings(SETTINGS_FILE).get(key)

  @staticmethod
  def open_config_rc(window):
    window.open_file(PLUGIN_FOLDER + "/" + RC_FILE)

  @staticmethod
  def open_sublime_settings(window):
    window.open_file(PLUGIN_FOLDER + "/" + SETTINGS_FILE)

  @staticmethod
  def open_sublime_keymap(window, platform):
    window.open_file(PLUGIN_FOLDER + "/" + KEYMAP_FILE.replace("$PLATFORM", platform))

  @staticmethod
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

  @staticmethod
  def get_node_path():
    platform = sublime.platform()
    node = PluginUtils.get_pref("node_path").get(platform)
    print("Using node.js path on '" + platform + "': " + node)
    return node

  @staticmethod
  def get_output(cmd):
    if int(sublime.version()) < 3000:
      if sublime.platform() != "windows":
        # Handle Linux and OS X in Python 2.
        run = '"' + '" "'.join(cmd) + '"'
        return commands.getoutput(run)
      else:
        # Handle Windows in Python 2.
        # Prevent console window from showing.
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        return subprocess.Popen(cmd, \
          stdout=subprocess.PIPE, \
          startupinfo=startupinfo).communicate()[0]
    else:
      # Handle all OS in Python 3.
      run = '"' + '" "'.join(cmd) + '"'
      return subprocess.check_output(run, stderr=subprocess.STDOUT, shell=True, env=os.environ)
