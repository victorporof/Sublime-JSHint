import commands
import sublime, sublime_plugin

class JshintCommand(sublime_plugin.TextCommand):
  def run(self, edit):

    scriptPath = sublime.packages_path() + "/Sublime-JSHint/scripts/run.js"
    setings = ' '.join([
      "browser:\ true",
      "v8:\ true",
      "es5:\ true",
      "esnext:\ true",
      "globalstrict:\ true",
      "strictundef:\ true",
      "laxradix:\ true",
      "trailing:\ true",
      "undef:\ false",
      "sub:\ true"
    ])
    cmd = ["node",scriptPath,self.view.file_name(),setings]

    lint = commands.getoutput('"'+'" "'.join(cmd)+'"')

    if len(lint) > 0:
      print lint
