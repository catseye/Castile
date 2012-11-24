TODO
----

Don't output final value.  Command-line arguments passed to `main`.  (`sysmain`?)

Name mangling for compilers (prepend with `_` most likely.)

Tests for struct equality, union value equality, unions of unions.

Test that order doesn't matter in unions, or in field assignments during a make.

### Implementation ###

Handle empty structs correctly on stackmac.

Figure out a way to do `input`, `read`, and `write` with node.js backend.

Implement `int`, `str`, `chr`, `ord` for Ruby, Javascript, stackmac.

TaggedValue -> just a tuple.

stackmac: store tagged values as two values on the stack.
and void types in unions of (void, X) should only be one value.
(structs are still boxed though)

AST nodes should have source line numbers, it would be really nice.

"assignable" in typechecker -- can be done more cleanly with ScopedDict?

### Design ###

Convenience:

*   Allow `var x` anywhere, and lift to front of function.
*   Allow `x = expr` to stand for `var x = expr`, if it's first.  But beware the
    Lua/Python war on "explicit local".
*   Should we have automatic promotion (value tagging?)
    Since it causes an operation, I think it should be explicit, but the
    explicit syntax could be more lightweight.

Type promotion with higher precedence?  So that it can be used at toplevel.

Should there be closures as well as function values?

Should there be an expression form of `if`?

Should there be an expression form of `=`?  (`:=`?)

Should a block be a valid statement, with block scope?  (Meaningless if
all variables must be declared at start of function, as is the case right now.)
