import sublime, sublime_plugin
import os, re

try
  import commands
except ImportError:
  import subprocess

PLUGIN_FOLDER = os.path.dirname(os.path.realpath(__file__))

class JshintCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    filePath = self.view.file_name()

    # Make sure we're only linting javascript files.
    if filePath != None and not re.search(r'\.jsm?$', filePath):
      return

    packageName = PLUGIN_FOLDER.replace(sublime.packages_path(), "")
    scriptPath = PLUGIN_FOLDER + "/scripts/run.js"
    setings = ' && '.join([
      # To add persistent options that are used everywhere, edit the .jshintrc
      # file inside the scripts folder. But you can als add some options here
      # if you like. For example:
      # "browser: true",
      # "esnext: true",
      # "moz: true"
    ])

    # Get the current text in the buffer.
    bufferText = self.view.substr(sublime.Region(0, self.view.size()))

    # ...and save it in a temporary file. This allows for scratch buffers
    # and dirty files to be linted as well.
    tempName = ".__temp__"
    tempPath = PLUGIN_FOLDER + '/' + tempName
    f = open(tempPath, 'w')
    f.write(bufferText)
    f.close()

    cmd = ["/usr/local/bin/node", scriptPath, tempPath, filePath or "?", setings]
    output = ""
    if commands:
      output = commands.getoutput('"' + '" "'.join(cmd) + '"')
    else:
      output = subprocess.check_output('"' + '" "'.join(cmd) + '"', stderr=subprocess.STDOUT, shell=True)

    # We're done with linting, remove the temporary file and rebuild the
    # regions shown in the current view.
    os.remove(tempPath)
    self.view.erase_regions("jshint_errors");

    if len(output) > 0:
      regions = []
      menuitems = []

      # For each line of jshint output (errors, warnings etc.) add a region
      # in the view and a menuitem in a quick panel.
      for line in output.splitlines():
        try:
          data = line.split(":")
          line = int(data[1]) - 1
          column = int(data[2])
          point = self.view.text_point(line, column)
          word = self.view.word(point)
          menuitems.append(data[1] + ":" + data[2] + " " + data[3])
          regions.append(word)
        except:
          pass

      icon = ".." + packageName + "/warning"
      self.view.add_regions("jshint_errors", regions, "keyword", icon,
        sublime.DRAW_EMPTY |
        sublime.DRAW_OUTLINED |
        sublime.HIDE_ON_MINIMAP)

      sublime.active_window().show_quick_panel(menuitems, self.on_chosen)
      print(output)

  def on_chosen(self, index):
    if index == -1:
      return

    # Focus the user requested region from the quick panel.
    region = self.view.get_regions("jshint_errors")[index]
    selection = self.view.sel()
    selection.clear()
    selection.add(region)
    self.view.show(region)
