TODO
----

Don't output final value.  Command-line arguments passed to `main`.  (`sysmain`?)

Name mangling for compilers (prepend with `_` most likely.)

Tests for unions of unions.

### Implementation ###

Struct equality in Javascript, stackmac backends.

"struct size" function in stackmac backend, for structs with no fields or
void fields.

Figure out a way to do `input`, `read`, and `write` with node.js backend.

Implement `int`, `str`, `chr`, `ord` for Ruby, Javascript, stackmac.

TaggedValue -> just a tuple.

stackmac: store tagged values as two values on the stack.
and void types in unions of (void, X) should only be one value.
(structs are still boxed though)

AST nodes should have source line numbers, it would be really nice.

"assignable" in typechecker -- can be done more cleanly with ScopedDict?

Get rid of redundant struct_fields attr in checker.

### Design ###

Convenience:

*   Allow `var x` anywhere, and lift to front of function.
*   Allow `x = expr` to stand for `var x = expr`, if it's first.  But beware the
    Lua/Python war on "explicit local".
*   Should we have automatic promotion (value tagging?)
    Since it causes an operation, I think it should be explicit, but the
    explicit syntax could be more lightweight.
*   Lua-esque `:` operator: `a:b(c)` -> `a.b(a, c)`

Type promotion with higher precedence?  So that it can be used at toplevel.

Should there be closures as well as function values?

Should there be an expression form of `if`?

Should there be an expression form of `=`?  (`:=`?)

Should a block be a valid statement, with block scope?  (Meaningless if
all variables must be declared at start of function, as is the case right now.)
