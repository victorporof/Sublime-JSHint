/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */
"use strict";

var path = require("path");
var fs = require("fs");
var jshint = require("jshint").JSHINT;
var minify = require("jsonminify");

// Older versions of node have `existsSync` in the `path` module, not `fs`. Meh.
fs.existsSync = fs.existsSync || path.existsSync;
path.sep = path.sep || "/";

var tempPath = process.argv[2] || ""; // The source file to be linted.
var filePath = process.argv[3] || ""; // The original source's path.
var pluginFolder = path.dirname(__dirname);
var sourceFolder = path.dirname(filePath);
var options = {};
var globals = {};

var jshintrcPath;
var packagejsonPath;

// Try and get some persistent options from the plugin folder.
if (fs.existsSync(jshintrcPath = pluginFolder + path.sep + ".jshintrc")) {
  setOptions(jshintrcPath, false, options, globals);
}

// When a JSHint config file exists in the same directory as the source file,
// any directory above, or the user's home folder, then use that configuration
// to overwrite the default prefs.
var sourceFolderParts = path.resolve(sourceFolder).split(path.sep);

var pathsToLook = sourceFolderParts.map(function(value, key) {
  return sourceFolderParts.slice(0, key + 1).join(path.sep);
});

// Start with the current directory first, end with the user's home folder.
pathsToLook.reverse();
pathsToLook.push(getUserHome());

pathsToLook.some(function(pathToLook) {
  if (fs.existsSync(jshintrcPath = path.join(pathToLook, ".jshintrc"))) {
    return setOptions(jshintrcPath, false, options, globals);
  }
  if (fs.existsSync(packagejsonPath = path.join(pathToLook, "package.json"))) {
    return setOptions(packagejsonPath, true, options, globals);
  }
});

// Dump some diagnostics messages, parsed out by the plugin.
console.log("Using JSHint globals: " + JSON.stringify(globals));
console.log("Using JSHint options: " + JSON.stringify(options, null, 2));

// Read the source file and, when done, lint the code.
fs.readFile(tempPath, "utf8", function(err, data) {
  if (err) {
    return;
  }

  // Mark the output as being from JSHint.
  console.log("*** JSHint output ***");

  // If this is a markup file (html, xml, xhtml etc.), then javascript
  // is maybe present in a <script> tag. Try to extract it and lint.
  if (data.match(/^\s*</)) {
    // First non whitespace character is &lt, so most definitely markup.
    var regexp = /<script[^>]*>([^]*?)<\/script\s*>/gim;
    var script;

    while (script = regexp.exec(data)) {
      // Script contents are captured at index 1.
      var text = script[1];

      // Count all the lines up to and including the script tag.
      var prevLines = data.substr(0, data.indexOf(text)).split("\n");
      var lineOffset = prevLines.length - 1;
      doLint(text, options, globals, lineOffset, 0);
    }
  } else {
    doLint(data, options, globals, 0, 0);
  }
});

// Some handy utility functions.

function isTrue(value) {
  return value == "true" || value == true;
}

function getUserHome() {
  return process.env.HOME || path.join(process.env.HOMEDRIVE, process.env.HOMEPATH) || process.env.USERPROFILE;
}

function mergeOptions(source, target) {
  for (var entry in source) {
    if (entry === "globals") {
      if (!target[entry]) target[entry] = {};
      mergeOptions(source[entry], target[entry]);
    } else {
      target[entry] = source[entry];
    }
  }
}

function parseJSON(file) {
  try {
    var options = JSON.parse(minify(fs.readFileSync(file, "utf8")));
    if (!options.extends) { return options; }
    // Get the options from base file.
    var baseFile = options.extends;
    file = path.resolve(path.dirname(file), baseFile);
    var baseOptions = parseJSON(file);
    // Overwrite base options with local options.
    delete options.extends;
    mergeOptions(options, baseOptions);
    return baseOptions;
  } catch (e) {
    console.log("Could not parse JSON at: " + file);
    return {};
  }
}

function setOptions(file, isPackageJSON, optionsStore, globalsStore) {
  var obj = parseJSON(file);

  // Handle jshintConfig on package.json (NPM) files
  if (isPackageJSON) {
    if (obj.jshintConfig) {
      obj = obj.jshintConfig;
    } else {
      return false;
    }
  }

  for (var key in obj) {
    var value = obj[key];

    // Globals are defined as either an array, or an object with keys as names,
    // and a boolean value to determine if they are assignable.
    if (key == "globals" || key == "predef") {
      if (value instanceof Array) {
        for (var i = 0; i < value.length; i++) {
          var name = value[i];
          globalsStore[name] = true;
        }
      } else {
        for (var name in value) {
          globalsStore[name] = isTrue(value[name]);
        }
      }
    } else {
      // Special case "true" and "false" pref values as actually booleans.
      // This avoids common accidents in .jshintrc json files.
      if (value == "true" || value == "false") {
        optionsStore[key] = isTrue(value);
      } else {
        optionsStore[key] = value;
      }
    }
  }

  // Options were set successfully.
  return true;
}

function doLint(data, options, globals, lineOffset, charOffset) {
  // Lint the code and write readable error output to the console.
  try {
    jshint(data, options, globals);
  } catch (e) {}

  jshint.errors
    .sort(function(first, second) {
      first = first || {};
      second = second || {};

      if (!first.line) {
        return 1;
      } else if (!second.line){
        return -1;
      } else if (first.line == second.line) {
        return +first.character < +second.character ? -1 : 1;
      } else {
        return +first.line < +second.line ? -1 : 1;
      }
    })
    .forEach(function(e) {
      // If the argument is null, then we could not continue (too many errors).
      if (!e) {
        return;
      }

      // Do some formatting if the error data is available.
      if (e.raw) {
        var message = e.raw
          .replace("{a}", e.a)
          .replace("{b}", e.b)
          .replace("{c}", e.c)
          .replace("{d}", e.d);

        console.log([e.line + lineOffset, e.character + charOffset, message].join(" :: "));
      }
    });
}
