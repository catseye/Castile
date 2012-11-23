TODO
----

Canonical representation of values that's not Python's or Javascript's.
(And the representation issue for the typeless stack machine is its own can of worms)

Don't output final value.  Command-line arguments passed to `main`.  (`sysmain`?)

Name mangling for compilers (prepend with `_` most likely.)

Figure out a way to do `input`, `read`, and `write` with node.js backend.

Builtins: `int`, `str`, `chr`, `ord`.

### Implementation ###

AST nodes should have source line numbers, it would be really nice.

### Design ###

Should there be closures as well as function values?

Should there be an expression form of `if`?

Should there be an expression form of `=`?  (`:=`?)

Should a block be a valid statement, with block scope?

Should we have automatic promotion (value tagging?)
