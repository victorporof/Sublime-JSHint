# Sublime-JSHint: Javascript Lint for Sublime Text editor via node.js
#### [Sublime Text 2](http://www.sublimetext.com/2)
#### [JSHint homepage](http://jshint.com/)
#### [Node.js download](http://nodejs.org/#download)

## About
This is a Sublime Text 2 plugin and build system allowing you to check your JavaScript code for nasty errors, coding conventions and other goodies. It relies on JSHint, a fork of JSLint (developed by Douglas Crockford). The linter is itself written in JavaScript, so you'll need something (node.js) to interpret JavaScript code outside the browser.

## Installation
First of all, be sure you have [node.js](http://nodejs.org/#download) installed in order to run JSHint (a derivative work of JSLint, used to detect errors and potential problems in JS).
Each OS has a different `Packages` folder required by Sublime Text. Open it via Preferences -> Browse Packages, and copy this repository contents to a new `JSHint` folder there.

The shorter way of doing this is:
#### Linux
`git clone git://github.com/victorporof/Sublime-JSHint.git ~/.config/sublime-text-2/Packages/JSHint`

#### Mac
`git clone git://github.com/victorporof/Sublime-JSHint.git ~/Library/Application\ Support/Sublime\ Text\ 2/Packages/JSHint`

#### Windows
`git clone git://github.com/victorporof/Sublime-JSHint.git %APPDATA%/Sublime\ Text\ 2/Packages/JSHint`

## Usage
There are two ways you can use Sublime-JSHint: as a build system or a python plugin.

### Build system
Open a JavaScript file, Select JSHint from Tools -> Build System, and:

- `Ctrl+B` (or `Cmd+B` if you're on a Mac) to lint
- `F4` jump to next error row/column
- `Shift`-`F4` jump to previous error row-column

### Python plugin
Open a JavaScript file, pop out the console in Sublime Text from View -> Show Console, and type `view.run_command("jshint")`.

Writing commands in the console is ugly. Set up your own key combo for this, by going to Preferences -> Key Bindings - Default, and adding a command in that huge array: `{ "keys": ["super+shift+j"], "command": "jshint" },`. You can use any other command you want, thought most of them are already taken.

### Oh noez, command not found!
If you get an error `sh: node: command not found` or similar, you don't have `node` in the right path. Try setting the absolute path to node in JSHint.py or JSHint.sublime-build!
This means from:
`lint = commands.getoutput("node " + ...`
change to
`lint = commands.getoutput("absolute/path/to/node " + ...`

## Customize
Both `JSHint.sublime-build` and `JSHint.py` have some predefined settings which are probably quite important when writing JavaScript code (like "es5: true"). Add some more settings and options from the TONS available (see the [JSHint docs](http://jshint.com/#docs)).

Have fun!