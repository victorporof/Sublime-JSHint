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
  var path = require('path');
  var fs = require('fs');
  var jshint = require("jshint/src/stable/jshint.js").JSHINT;

  // The source file to be linted and options.
  var source = argv[2] || "";
  var settings = (argv[3] || "").split(",");
  var option = {};

  // Continue only if the source file is specified.
  if (source == "" || !source.match(".jsm?" + "$")) {
    return;
  }

  // When a JSHint config file exists in the same dir as the source file or
  // one dir above, then use this configuration instead of the default one.
  var jshintrc = ".jshintrc";
  var getOptions = function(file) {
    var data = fs.readFileSync(file, "utf8");
    return JSON.parse(data);
  };

  if (fs.existsSync(jshintrc)) {
    option = getOptions(jshintrc);
  } else if (fs.existsSync("../" + jshintrc)) {
    option = getOptions("../" + jshintrc);
  } else {
    // Extra arguments with custom options could be passed, so check them now
    // and add them to the options object.
    for (var i = 0, len = settings.length; i < len; i++) {
      var hash = settings[i].split(":");
      if (hash.length != 2) {
        continue;
      }
      var key = hash[0].trim();
      var value = hash[1].trim();

      // There are two options that allow numerical values.
      if (key == "maxerr" || key == "indent") {
        // Store value as Number, not as String.
        option[key] = +value;
        continue;
      }

      // There is one option that allows array of strings to be passed
      // (predefined custom globals)
      if (key == "predef") {
        // eval is evil, but JSON.parse would require usage of only double quotes
        option[key] = eval(value);
        continue;
      }

      // Options are stored in key value pairs, such as option.es5 = true.
      option[key] = value == "true";
    }
  }

  // Read the source file and, when complete, lint the code.
  fs.readFile(source, "utf8", function(err, data) {
    if (err) {
      log("Error, unable to continue.");
      return;
    }

    // Lint the code and write readable error output to the console.
    try {
      jshint(data, option);
    } catch (e) {}

    jshint.errors.forEach(function(e) {
      // If the argument is null, then we could not continue (too many errors).
      if (!e) {
        log("Stopping, unable to continue.");
        return;
      }

      // Do some formatting if the error data is available.
      if (e.raw) {
        log([
          source.split(path.sep).pop(), ":",
          e.line, ":",
          e.character, ":",
          e.raw.replace("{a}", e.a)
          .replace("{b}", e.b)
          .replace("{c}", e.c)
          .replace("{d}", e.d)
        ].join(""));
      }
    });
  });
}());
