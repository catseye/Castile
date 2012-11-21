#!/bin/sh

cat >test_config <<EOF
    -> Functionality "Run Castile Program" is implemented by shell command
    -> "bin/castile %(test-file)"

    -> Functionality "Run Castile Program" is implemented by shell command
    -> "bin/castile -c %(test-file) > foo.js && node foo.js"
EOF

falderal -b test_config README.markdown
rm -f test_config foo.js
