import commands
import sublime, sublime_plugin

class JshintCommand(sublime_plugin.TextCommand):
  def run(self, edit):

    lint = commands.getoutput("node /path/to/nodelint.js " + self.view.file_name() +
    " es5:\ true" +
    " browser:\ true" +
    " globalstrict:\ true")

    print lint
