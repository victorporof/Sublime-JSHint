# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import sublime, sublime_plugin
import os, subprocess, tempfile, codecs, re

try:
  import commands
except ImportError:
  pass

PLUGIN_FOLDER = os.path.dirname(os.path.realpath(__file__))
OUTPUT_VALID = b"*** JSHint output ***"
NODE_LINE = 33

class JshintCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    # Get the current text in the buffer.
    bufferText = self.view.substr(sublime.Region(0, self.view.size()))
    # ...and save it in a temporary file. This allows for scratch buffers
    # and dirty files to be linted as well.
    tempName = ".__temp__"
    tempPath = tempfile.gettempdir() + '/' + tempName
    print("Saving buffer to: " + tempPath)
    f = codecs.open(tempPath, mode='w', encoding='utf-8')
    f.write(bufferText)
    f.close()

    # Simply using `node` without specifying a path sometimes doesn't work :(
    # http://nodejs.org/#download
    # https://github.com/victorporof/Sublime-JSHint#oh-noez-command-not-found
    node = "node" if exists_in_path("node") else "/usr/local/bin/node"

    try:
      scriptPath = PLUGIN_FOLDER + "/scripts/run.js"
      filePath = self.view.file_name()
      output = get_output([node, scriptPath, tempPath, filePath or "?"])

      # Make sure the correct/expected output is available.
      if output.find(OUTPUT_VALID) == -1:
        print(output)
        raise Error()
    except:
      msg = "Node.js was not found in the default path. Please specify the location."
      if sublime.ok_cancel_dialog(msg):
        open_jshintpy(self.view.window())
      else:
        msg = "You won't be able to use this plugin without specifying the path to Node.js."
        sublime.error_message(msg)
      return

    # We're done with linting, remove the temporary file and rebuild the
    # regions shown in the current view.
    os.remove(tempPath)
    self.view.erase_regions("jshint_errors");

    # Remove the output identification marker (first line).
    output = output[len(OUTPUT_VALID) + 1:]
    if len(output) > 0:
      regions = []
      menuitems = []

      # For each line of jshint output (errors, warnings etc.) add a region
      # in the view and a menuitem in a quick panel.
      for line in output.decode().splitlines():
        try:
          lineNo, columnNo, description = line.split(" :: ")
          point = self.view.text_point(int(lineNo) - 1, int(columnNo))
          word = self.view.word(point)
          menuitems.append(lineNo + ":" + columnNo + " " + description)
          regions.append(word)
        except:
          pass

      self.add_regions(regions)
      self.view.window().show_quick_panel(menuitems, self.on_chosen)

  def add_regions(self, regions):
    packageName = PLUGIN_FOLDER.replace(sublime.packages_path(), "")

    if int(sublime.version()) >= 3000:
      icon = "Packages/" + packageName + "/warning.png"
      self.view.add_regions("jshint_errors", regions, "keyword", icon,
        sublime.DRAW_EMPTY |
        sublime.DRAW_NO_FILL |
        sublime.DRAW_NO_OUTLINE |
        sublime.DRAW_SQUIGGLY_UNDERLINE)
    else:
      icon = ".." + packageName + "/warning"
      self.view.add_regions("jshint_errors", regions, "keyword", icon,
        sublime.DRAW_EMPTY |
        sublime.DRAW_OUTLINED |
        sublime.HIDE_ON_MINIMAP)

  def on_chosen(self, index):
    if index == -1:
      return

    # Focus the user requested region from the quick panel.
    region = self.view.get_regions("jshint_errors")[index]
    selection = self.view.sel()
    selection.clear()
    selection.add(region)
    self.view.show(region)

class JshintSetOptionsCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    open_jshintrc(self.view.window())

class JshintSetNodePathCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    open_jshintpy(self.view.window())

class JshintClearAnnotationsCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    self.view.erase_regions("jshint_errors");

def open_jshintrc(window):
  window.open_file(PLUGIN_FOLDER + "/.jshintrc")

def open_jshintpy(window):
  window.open_file(PLUGIN_FOLDER + "/JSHint.py:" + str(NODE_LINE), sublime.ENCODED_POSITION)

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
      return subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]
  else:
    # Handle all OS in Python 3.
    run = '"' + '" "'.join(cmd) + '"'
    return subprocess.check_output(run, stderr=subprocess.STDOUT, shell=True)
