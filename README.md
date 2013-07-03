# JSHint Gutter for Sublime Text 2 and 3 via node.js
#### [Sublime Text 3](http://www.sublimetext.com/3)
#### [JSHint homepage](http://jshint.com/)
#### [Node.js download](http://nodejs.org/#download)

## About
This is a Sublime Text 2 and 3 plugin allowing you to check your JavaScript code for nasty errors, coding conventions and other goodies. It relies on JSHint, a fork of JSLint (developed by Douglas Crockford). The linter is itself written in JavaScript, so you'll need something (node.js) to interpret JavaScript code outside the browser.

![Screenshot](https://dl.dropboxusercontent.com/u/2388316/screenshots/sublime-jshint.png)

## Installation
First of all, be sure you have [node.js](http://nodejs.org/#download) installed in order to run JSHint (a derivative work of JSLint, used to detect errors and potential problems in JS).
Each OS has a different `Packages` folder required by Sublime Text. Open it via Preferences -> Browse Packages, and copy this repository contents to a new `Sublime-JSHint` folder there.

The shorter way of doing this is:
### Through [Sublime Package Manager](http://wbond.net/sublime_packages/package_control)

* `Ctrl+Shift+P` or `Cmd+Shift+P` in Linux/Windows/OS X
* type `install`, select `Package Control: Install Package`
* type `js gutter`, select `JSHint Gutter`

### Manually
Make sure you use the right Sublime Text folder. For example, on OS X, packages for version 2 are in `~/Library/Application\ Support/Sublime\ Text\ 2`, while version 3 is labeled `~/Library/Application\ Support/Sublime\ Text\ 3`.

These are for Sublime Text 2:

#### Mac
`git clone https://github.com/victorporof/Sublime-JSHint.git ~/Library/Application\ Support/Sublime\ Text\ 2/Packages/Sublime-JSHint`

#### Linux
`git clone https://github.com/victorporof/Sublime-JSHint.git ~/.config/sublime-text-2/Packages/Sublime-JSHint`

#### Windows
`git clone https://github.com/victorporof/Sublime-JSHint.git %APPDATA%/Sublime\ Text\ 2/Packages/Sublime-JSHint`

## Usage
Tools -> Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`) and type `jshint`.

-- or --

`Ctrl+Shift+J` (or `Cmd+Shift+J` if you're on a Mac).

-- or --

Right click in the current buffer and select "Lint code using JSHint".

-- or --

Open a JavaScript file, pop out the console in Sublime Text from View -> Show Console, and type `view.run_command("jshint")`.

Writing commands in the console is ugly. Set up your own key combo for this, by going to Preferences -> Key Bindings - User, and adding a command in that huge array: `{ "keys": ["super+shift+j"], "command": "jshint" },`. You can use any other command you want, thought most of them are already taken.

## Oh noez, command not found!
If you get an error `sh: node: command not found` or similar, you don't have `node` in the right path. Try setting the absolute path to node in `JSHint.py`.
This means from:
`node = "node" if self.exists_in_path("node") else "/usr/local/bin/node"`
change to
`node = "node" if self.exists_in_path("node") else "/your/absolute/path/to/node"`

* `Ctrl+Shift+P` or `Cmd+Shift+P` in Linux/Windows/OS X
* type `jshint`, select `Set node Path`

Simply using `node` without specifying a path sometimes doesn't work :(

For example, on Linux the path could be in `/home/<user>/.nvm/<node version>/bin/node`.

On Windows, the absolute path to node.exe *must* use forward slashes.

## Using your own jshint options
The plugin looks for a `.jshintrc` file in the same directory as the source file you're linting (or one directory above if it doesn't exist, or in your home folder if everything else fails) and uses those options instead of the default ones. [Here](https://github.com/jshint/jshint/blob/master/examples/.jshintrc)'s an example of how it can look like.

Here's how a `.jshintrc` file in your home folder could look like:
```
{
  "validthis": true,
  "globals": {
    "Components": false,
    "XPCOMUtils": false,
    "EventEmitter": true,
    "Promise": true
  }
}
```
A few persistent options are always applied, if not overwritten by your own `.jshintrc` file. Those are defined [here](https://github.com/victorporof/Sublime-JSHint/blob/master/scripts/.jshintrc). You can safely add stuff to that json file if you want.

* `Ctrl+Shift+P` or `Cmd+Shift+P` in Linux/Windows/OS X
* type `jshint`, select `Set Default Options`

Thank you!
