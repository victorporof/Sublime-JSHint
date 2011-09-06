var i, len, hash, key, value, raw,

  log = console.log,
  argv = process.argv,

  path = require('path'),
  fs = require('fs'),
  jshint = require(path.join(__dirname, "jshint.js")).JSHINT,

  source = argv[2] || "",
  option = {};

for (i = 3, len = argv.length; i < len; i++) {
  hash = argv[i].split(":");
  key = hash[0];
  value = hash[1];

  option[key] = value;
}

if (source !== "") {
  fs.readFile(source, "utf8", function(err, data) {
    if (err) {
      return;
    }

    jshint(data, option);
    jshint.errors.forEach(function(e) {
      if (e === null) {
        return;
      }
      raw = e.raw;

      if ("undefined" !== typeof raw) {
        log([e.line, ":",
             e.character, " ",
             raw.replace("{a}", e.a).
                 replace("{b}", e.b).
                 replace("{c}", e.c).
                 replace("{d}", e.d)].join(""));
      }
      else {
        log("Stopping, unable to continue.");
      }
    });
  });
}
