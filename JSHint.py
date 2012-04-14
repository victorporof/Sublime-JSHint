import commands, re
import sublime, sublime_plugin

class JshintCommand(sublime_plugin.TextCommand):
  def run(self, edit):

    regx = re.compile(" ")
    lint = commands.getoutput("node " +
      regx.sub("\ ", sublime.packages_path()) + "/Sublime-JSHint/scripts/run.js " +
      regx.sub("\ ", self.view.file_name()) +
        " browser:\ true" +
        " v8:\ true" +
        " es5:\ true" +
        " esnext:\ true" +
        " globalstrict:\ true" +
        " strictundef:\ true" +
        " laxradix:\ true" +
        " trailing:\ true" +
        " undef:\ false" +
        " sub:\ true")

    if len(lint) > 0:
      print lint
