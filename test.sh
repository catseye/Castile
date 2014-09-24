#!/bin/sh

echo -n '' > test_config

if [ "x$1" = x ]; then
  cat >>test_config <<EOF
    -> Functionality "Run Castile Program" is implemented by shell command
    -> "bin/castile %(test-body-file)"

EOF
fi

if [ ! x`which node` = x ]; then
  cat >>test_config <<EOF
    -> Functionality "Run Castile Program" is implemented by shell command
    -> "bin/castile -c javascript %(test-body-file) > foo.js && node foo.js"

EOF
fi

if [ ! x`which ruby` = x ]; then
  cat >>test_config <<EOF
    -> Functionality "Run Castile Program" is implemented by shell command
    -> "bin/castile -c ruby %(test-body-file) > foo.rb && ruby foo.rb"

EOF
fi

if [ -e bin/stackmac ]; then
  cat >>test_config <<EOF
    -> Functionality "Run Castile Program" is implemented by shell command
    -> "bin/castile -c stackmac %(test-body-file) > foo.stack && bin/stackmac foo.stack"

EOF
fi

if [ "x$1" = "xc" ]; then
  cat >>test_config <<EOF
    -> Functionality "Run Castile Program" is implemented by shell command
    -> "bin/castile -c c %(test-body-file) > foo.c && gcc foo.c && ./a.out"

EOF
fi

falderal -b test_config README.markdown
RESULT=$?
rm -f test_config foo.* a.out
exit $RESULT
