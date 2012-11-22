#!/bin/sh

cat >test_config <<EOF
    -> Functionality "Run Castile Program" is implemented by shell command
    -> "bin/castile %(test-file)"

    -> Functionality "Run Castile Program" is implemented by shell command
    -> "bin/castile -c javascript %(test-file) > foo.js && node foo.js"
EOF

cat >test_config <<EOF
    -> Functionality "Run Castile Program" is implemented by shell command
    -> "bin/castile -c ruby %(test-file) > foo.rb && ruby foo.rb"
EOF

falderal -b test_config README.markdown
rm -f test_config foo.*
