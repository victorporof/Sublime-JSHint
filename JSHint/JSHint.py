import commands, re
import sublime, sublime_plugin

class JshintCommand(sublime_plugin.TextCommand):
  def run(self, edit):

    regx = re.compile(" ");
    lint = commands.getoutput("node " +
      regx.sub("\ ", sublime.packages_path()) + "/JSHint/scripts/run.js " +
      regx.sub("\ ", self.view.file_name()) +
        " es5:\ true" +
        " browser:\ true" +
        " globalstrict:\ true")

    if len(lint) > 0:
      print lint
