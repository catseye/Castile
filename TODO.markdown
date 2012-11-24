TODO
----

Canonical representation of values that's not Python's or Javascript's.
(And the representation issue for the typeless stack machine is its own can of worms)

Don't output final value.  Command-line arguments passed to `main`.  (`sysmain`?)

Name mangling for compilers (prepend with `_` most likely.)

Tests for empty structs.  Demo of "typed enum" (union of empty structs.)

Tests for struct equality, union value equality.

### Implementation ###

Figure out a way to do `input`, `read`, and `write` with node.js backend.

Implement `int`, `str`, `chr`, `ord` for Ruby, Javascript, stackmac.

TaggedValue -> just a tuple.

stackmac: store tagged values as two values on the stack.
and void types in unions of (void, X) should only be one value.
(structs are still boxed though)

AST nodes should have source line numbers, it would be really nice.

### Design ###

Type promotion with higher precedence?  So that it can be used at toplevel.

Should there be closures as well as function values?

Should there be an expression form of `if`?

Should there be an expression form of `=`?  (`:=`?)

Should a block be a valid statement, with block scope?

Should we have automatic promotion (value tagging?)
