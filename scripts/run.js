/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

(function() {
  "use strict";

  // Cache the console log function and the process arguments.
  var log = console.log;
  var argv = process.argv;

  // Require path and file system utilities to load the jshint.js file.
  var path = require("path");
  var fs = require("fs");

  // The source file to be linted, original source's path and some options.
  var tempPath = argv[2] || "";
  var filePath = argv[3] || "";
  var options = Object.create(null);
  var globals = Object.create(null);

  // This stuff does all the magic.
  var jshint = require("jshint/src/jshint.js").JSHINT;

  // Some handy utility functions.
  function isTrue(value) {
    return value == "true" || value == true;
  }
  function getOptions(file) {
    try {
      require("jsonminify");
      return JSON.parse(JSON.minify(fs.readFileSync(file, "utf8")));
    } catch (e) {
      return Object.create(null);
    }
  }
  function setOptions(file, optionsStore, globalsStore) {
    var obj = getOptions(file);
    // Handle jshintConfig on package.json (NPM) files
    if (obj.jshintConfig) {
      obj = obj.jshintConfig;
    } else if (obj.name) { // Skip the rest if NPM without jshintConfig
      return false;
    }
    for (var key in obj) {
      var value = obj[key];
      // Globals are defined as an object, with keys as names, and a boolean
      // value to determine if they are assignable.
      if (key == "global" || key == "globals" || key == "predef") {
        if (value instanceof Array) {
          value.forEach(function(name) {
            globalsStore[name] = true;
          });
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
  }

  var jshintrc = ".jshintrc";
  var packagejson = "package.json";
  var pluginFolder = path.dirname(__dirname);
  var currentFolder = path.dirname(filePath);
  var lastCurrentFolder;
  var jshintrcPath;
  var packagejsonPath;

  // Older versions of node has `existsSync` in the path module, not fs. Meh.
  fs.existsSync = fs.existsSync || path.existsSync;
  path.sep = path.sep || "/";

  // Try and get some persistent options from the plugin folder.
  if (fs.existsSync(jshintrcPath = pluginFolder + path.sep + jshintrc)) {
    setOptions(jshintrcPath, options, globals);
  }

  // When a JSHint config file exists in the same directory as the source file,
  // or any directory above it, then use this configuration to overwrite the
  // default prefs.
  while (currentFolder !== lastCurrentFolder) {
    lastCurrentFolder = currentFolder;
    if (fs.existsSync(jshintrcPath = currentFolder + path.sep + jshintrc)) {
      setOptions(jshintrcPath, options, globals);
      break; // Stop at the first found JSHint config file.
    } else if (fs.existsSync(packagejsonPath = currentFolder + path.sep + packagejson)) {
      var success = setOptions(packagejsonPath, options, globals);
      if (success !== false) {
        break; // Stop at the first package.json with JSHint config.
      }
    }
    currentFolder = path.dirname(currentFolder);
  }

  // Read the source file and, when done, lint the code.
  fs.readFile(tempPath, "utf8", function(err, data) {
    if (err) {
      return;
    }

    // Mark the output as being from JSHint.
    log("*** JSHint output ***");

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

          log([e.line + lineOffset, e.character + charOffset, message].join(" :: "));
        }
      });
  }
}());
