# Sublime-JSHint: Javascript Lint for Sublime Text editor via node.js
#### [Sublime Text 2](http://www.sublimetext.com/2)
#### [JSHint homepage](http://jshint.com/)
#### [Node.js download](http://nodejs.org/#download)

## About
This is a Sublime Text 2 plugin and build system allowing you to check your JavaScript code for nasty errors, coding conventions and other goodies. It relies on JSHint, a fork of JSLint (developed by Douglas Crockford). The linter is itself written in JavaScript, so you'll need something (node.js) to interpret JavaScript code outside the browser.

## Installation
First of all, be sure you have [node.js](http://nodejs.org/#download) installed in order to run JSHint (a derivative work of JSLint, used to detect errors and potential problems in JavaScript code).

Each OS has a different `Packages` folder required by Sublime Text. Open it via Preferences -> Browse Packages, and copy the `JSHint` folder there.

## Usage
There are two ways you can use Sublime-JSHint: as a build system or a python plugin.

### Build system
Open a JavaScript file, Select JSHint from Tools -> Build System, and hit Ctrl+B (or Cmd+B if you're on a Mac).

### Python plugin
Open a JavaScript file, pop out the console in Sublime Text from View -> Show Console, and type `view.run_command("jshint")`. Should work like a charm.

Writing commands in the console is ugly. Set up your own key combo for this, by going to Preferences -> Key Bindings - Default, and adding a command in that huge array: `{ "keys": ["super+shift+j"], "command": "jshint" }`. You can use any other command you want, thought most of them are already taken.

## Customize
Both `JSHint.sublime-build` and `JSHint.py` have some predefined settings which are probably quite important when writing JavaScript code (like "es5: true"). Add some more settings and options from the TONS available (see the [JSHint docs](http://jshint.com/#docs)).

Have fun!