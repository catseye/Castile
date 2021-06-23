#!/bin/sh

APPLIANCES="tests/appliances/castile.md"

if [ ! x`which python3` = x ]; then
    APPLIANCES="$APPLIANCES tests/appliances/python3-castile.md"
fi

if [ ! x`which node` = x ]; then
    APPLIANCES="$APPLIANCES tests/appliances/castile-c-javascript.md"
fi

if [ ! x`which ruby` = x ]; then
    APPLIANCES="$APPLIANCES tests/appliances/castile-c-ruby.md"
fi

if [ -e bin/stackmac ]; then
    APPLIANCES="$APPLIANCES tests/appliances/castile-c-stackmac.md"
fi

if [ "x$1" = "xc" ]; then
    APPLIANCES="$APPLIANCES tests/appliances/castile-c-c.md"
fi

falderal $APPLIANCES README.md
RESULT=$?
rm -f foo.* a.out
exit $RESULT
