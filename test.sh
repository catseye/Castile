#!/bin/sh

if [ ! x`command -v python2` = x ]; then
    APPLIANCES="$APPLIANCES tests/appliances/castile.md"
fi

if [ ! x`command -v python3` = x ]; then
    APPLIANCES="$APPLIANCES tests/appliances/python3-castile.md"
fi

if [ ! x`command -v node` = x ]; then
    APPLIANCES="$APPLIANCES tests/appliances/castile-c-javascript.md"
fi

if [ ! x`command -v ruby` = x ]; then
    APPLIANCES="$APPLIANCES tests/appliances/castile-c-ruby.md"
fi

if [ -e bin/stackmac ]; then
    APPLIANCES="$APPLIANCES tests/appliances/castile-c-stackmac.md"
fi

if [ ! x`command -v gcc` = x ]; then
    APPLIANCES="$APPLIANCES tests/appliances/castile-c-c.md"
fi

falderal $APPLIANCES README.md
RESULT=$?
rm -f foo.* a.out
exit $RESULT
