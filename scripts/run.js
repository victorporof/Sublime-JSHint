/*
 * Copyright (c) 2011 Victor Porof
 *
 * This software is provided 'as-is', without any express or implied
 * warranty. In no event will the authors be held liable for any damages
 * arising from the use of this software.
 *
 * Permission is granted to anyone to use this software for any purpose,
 * including commercial applications, and to alter it and redistribute it
 * freely, subject to the following restrictions:
 *
 *    1. The origin of this software must not be misrepresented; you must not
 *    claim that you wrote the original software. If you use this software
 *    in a product, an acknowledgment in the product documentation would be
 *    appreciated but is not required.
 *
 *    2. Altered source versions must be plainly marked as such, and must not
 *    be misrepresented as being the original software.
 *
 *    3. This notice may not be removed or altered from any source
 *    distribution.
 */

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
  var jshint = require("jshint/src/stable/jshint.js").JSHINT;

  // Some handy utility functions.
  function isTrue(value) {
    return value == "true" || value == true;
  }
  function getUserHome() {
    return process.env.HOME || process.env.HOMEPATH || process.env.USERPROFILE;
  }
  function getOptions(file) {
    var data = fs.readFileSync(file, "utf8");
    var comments = /(?:\/\*(?:[\s\S]*?)\*\/)|(?:\/\/(?:.*)$)/gm;
    try {
      return JSON.parse(data.replace(comments, ""));
    } catch (e) {
      return Object.create(null);
    }
  }
  function setOptions(file, optionsStore, globalsStore) {
    var obj = getOptions(file);
    for (var key in obj) {
      var value = obj[key];
      // Globals are defined as an object, with keys as names, and a boolean
      // value to determine if they are assignable.
      if (key == "global" || key == "globals" || key == "predef") {
        for (var name in value) {
          globalsStore[name] = isTrue(value[name]);
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
  var pluginFolder = __dirname.split(path.sep).slice(0, -1).join(path.sep);
  var sourceFolder = filePath.split(path.sep).slice(0, -1).join(path.sep);
  var sourceParent = filePath.split(path.sep).slice(0, -2).join(path.sep);
  var jshintrcPath;

  // Try and get some persistent options from the plugin folder.
  if (fs.existsSync(jshintrcPath = pluginFolder + path.sep + jshintrc)) {
    setOptions(jshintrcPath, options, globals);
  }

  // When a JSHint config file exists in the same dir as the source file or
  // one dir above, then use this configuration to overwrite the default prefs.

  // Try and get more options from the source's folder.
  if (fs.existsSync(jshintrcPath = sourceFolder + path.sep + jshintrc)) {
    setOptions(jshintrcPath, options, globals);
  }
  // ...or the parent folder.
  else if (fs.existsSync(jshintrcPath = sourceParent + path.sep + jshintrc)) {
    setOptions(jshintrcPath, options, globals);
  }
  // ...or the user's home folder if everything else fails.
  else if (fs.existsSync(jshintrcPath = getUserHome() + path.sep + jshintrc)) {
    setOptions(jshintrcPath, options, globals);
  }

  // Read the source file and, when done, lint the code.
  fs.readFile(tempPath, "utf8", function(err, data) {
    if (err) {
      return;
    }

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
