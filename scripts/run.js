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

/*global console, process, require, __dirname */

(function() {
  "use strict";

  var i, len, hash, key, value, raw,

    // cache the console log function and the process arguments
    log = console.log,
    argv = process.argv,

    // require path and file system utilities to load the jshint.js file
    path = require('path'),
    fs = require('fs'),
    jshint = require(path.join(__dirname, "jshint.js")).JSHINT,

    // the source file to be linted and options
    source = argv[2] || "",
    option = {};

  // continue only if the source file is specified
  if (source !== "") {

    // extra arguments with custom options could be passed, so check them now
    // and add them to the options object
    for (i = 3, len = argv.length; i < len; i++) {
      hash = argv[i].split(":");
      key = hash[0];
      value = hash[1];

      // there are two options that allow numerical values
      if (key === "maxerr" || key === "indent") {
        option[key] = +value; //store value as Number, not as String
        continue;
      }
    
      // there is one option that allows array of strings to be passed (predefined custom globals)
      if (key === "predef") {
        option[key] = eval(value);//eval is evil, but JSON.parse would require only double quotes to be used
        continue;
      }

      // options are stored in key value pairs, such as option.es5 = true
      option[key] = value === true || value.trim() === "true";
    }

    // read the source file and, when complete, lint the code
    fs.readFile(source, "utf8", function(err, data) {
      if (err) {
        return;
      }

      // lint the code and write readable error output to the console
      try {
        jshint(data, option);
      } catch(e) {}

      jshint.errors.forEach(function(e) {

        // if the error is null, then we could not continue (too many errors)
        if (e === null) {
          log("Stopping, unable to continue.");
          return;
        }

        // get the raw error data
        raw = e.raw;

        // do some formatting if the error data is available
        if ("undefined" !== typeof raw) {
          log([source, ":",
               e.line, ":",
               e.character, " ",
               raw.replace("{a}", e.a).
                   replace("{b}", e.b).
                   replace("{c}", e.c).
                   replace("{d}", e.d)].join(""));
        }
      });
    });
  }
}());