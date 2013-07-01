# JSHint Gutter for Sublime Text 2 via node.js
#### [Sublime Text 2](http://www.sublimetext.com/2)
#### [JSHint homepage](http://jshint.com/)
#### [Node.js download](http://nodejs.org/#download)

## About
This is a Sublime Text 2 plugin allowing you to check your JavaScript code for nasty errors, coding conventions and other goodies. It relies on JSHint, a fork of JSLint (developed by Douglas Crockford). The linter is itself written in JavaScript, so you'll need something (node.js) to interpret JavaScript code outside the browser.

![Screenshot](https://dl.dropboxusercontent.com/u/2388316/screenshots/sublime-jshint.png)

## Installation
First of all, be sure you have [node.js](http://nodejs.org/#download) installed in order to run JSHint (a derivative work of JSLint, used to detect errors and potential problems in JS).
Each OS has a different `Packages` folder required by Sublime Text. Open it via Preferences -> Browse Packages, and copy this repository contents to a new `Sublime-JSHint` folder there.

The shorter way of doing this is:
#### Linux
`git clone git://github.com/victorporof/Sublime-JSHint.git ~/.config/sublime-text-2/Packages/Sublime-JSHint`

#### Mac
`git clone git://github.com/victorporof/Sublime-JSHint.git ~/Library/Application\ Support/Sublime\ Text\ 2/Packages/Sublime-JSHint`

#### Windows
`git clone git://github.com/victorporof/Sublime-JSHint.git %APPDATA%/Sublime\ Text\ 2/Packages/Sublime-JSHint`

## Usage
Tools -> Command Palette (`Cmd+Shift+P` or `Ctrl+Shift+P`) and type `jshint`.

-- or --

`Ctrl+Shift+J` (or `Cmd+Shift+J` if you're on a Mac).

-- or --

Right click in the current buffer and select "Lint code using JSHint".

-- or --

Open a JavaScript file, pop out the console in Sublime Text from View -> Show Console, and type `view.run_command("jshint")`.

Writing commands in the console is ugly. Set up your own key combo for this, by going to Preferences -> Key Bindings - User, and adding a command in that huge array: `{ "keys": ["super+shift+j"], "command": "jshint" },`. You can use any other command you want, thought most of them are already taken.

## Oh noez, command not found!
If you get an error `sh: node: command not found` or similar, you don't have `node` in the right path. Try setting the absolute path to node in `JSHint.py` or `JSHint.sublime-build`.
This means from:
`cmd = ["/usr/local/bin/node", ...]`
change to
`cmd = ["/your/absolute/path/to/node", ...]`

On Windows, the absolute path to node.exe *must* use forward slashes.

## Using your own jshint options
The plugin looks for a `.jshintrc` file in the same directory as the source file you're linting (or one directory above if it doesn't exist, or in your home folder if everything else fails) and uses those options instead of the default ones. [Here](https://github.com/jshint/jshint/blob/master/examples/.jshintrc)'s an example of how it can look like.

A few persistent options are always applied, if not overwritten by your own `.jshintrc` file. Those are defined [here](https://github.com/victorporof/Sublime-JSHint/blob/master/scripts/.jshintrc). You can safely add stuff to that json file if you want.

Although not recommended, `JSHint.py` can also contain some predefined settings which are probably quite important when writing JavaScript code (like "moz: true"). Add some more settings and options from the TONS available (see the [JSHint docs](http://www.jshint.com/options/)).

Have fun!
