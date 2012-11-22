#!/bin/sh

cat >test_config <<EOF
    -> Functionality "Run Castile Program" is implemented by shell command
    -> "bin/castile %(test-file)"

    -> Functionality "Run Castile Program" is implemented by shell command
    -> "bin/castile -c javascript %(test-file) > foo.js && node foo.js"

    -> Functionality "Run Castile Program" is implemented by shell command
    -> "bin/castile -c ruby %(test-file) > foo.rb && ruby foo.rb"
EOF

cat >test_config <<EOF
    -> Functionality "Run Castile Program" is implemented by shell command
    -> "bin/castile -c stackmac %(test-file) > foo.stack && bin/stackmac foo.stack"
EOF

falderal -b test_config README.markdown
rm -f test_config foo.*
