#!/bin/sh

echo -n '' > test_config

if [ "x$1" = "xeval" -o "x$1" = "xall" ]; then
  cat >>test_config <<EOF
    -> Functionality "Run Castile Program" is implemented by shell command
    -> "bin/castile %(test-file)"

EOF
fi

if [ "x$1" = "xjs" -o "x$1" = "xall" ]; then
  cat >>test_config <<EOF
    -> Functionality "Run Castile Program" is implemented by shell command
    -> "bin/castile -c javascript %(test-file) > foo.js && node foo.js"

EOF
fi

if [ "x$1" = "xruby" -o "x$1" = "xall" ]; then
  cat >>test_config <<EOF
    -> Functionality "Run Castile Program" is implemented by shell command
    -> "bin/castile -c ruby %(test-file) > foo.rb && ruby foo.rb"

EOF
fi

if [ "x$1" = "xstackmac" -o "x$1" = "xall" ]; then
  cat >>test_config <<EOF
    -> Functionality "Run Castile Program" is implemented by shell command
    -> "bin/castile -c stackmac %(test-file) > foo.stack && bin/stackmac foo.stack"

EOF
fi

if [ "x$1" = "xc" ]; then
  cat >>test_config <<EOF
    -> Functionality "Run Castile Program" is implemented by shell command
    -> "bin/castile -c c %(test-file) > foo.c && gcc foo.c && ./a.out"

EOF
fi

falderal -b test_config README.markdown
rm -f test_config foo.* a.out
