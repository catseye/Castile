TODO
----

Don't output final value.  Command-line arguments passed to `main`.  (`sysmain`?)

Name mangling for compilers (prepend with `_` most likely.)

Tests for unions of unions.

Test for equality of union values.

Tests for multiple occurrences of same type in a union.

### Implementation ###

Struct equality in Javascript, stackmac backends.

Figure out a way to do `input`, `read`, and `write` with node.js backend.

Implement `int`, `str`, `chr`, `ord` for Ruby, Javascript, stackmac.

TaggedValue -> just a tuple.

stackmac: store tagged values as two values on the stack.
and void types in unions of (void, X) should only be one value.
(structs are still boxed though)

AST nodes should have source line numbers, it would be really nice.

C backend.  Other backends (Python? Java? CIL? Scheme?)

### Design ###

Convenience:

*   Should we have automatic promotion (value tagging?)
    Since it causes an operation, I think it should be explicit, but the
    explicit syntax could be more lightweight.
*   Lua-esque `:` operator: `a:b(c)` -> `a.b(a, c)`

Type promotion with higher precedence?  So that it can be used at toplevel.

Should there be closures as well as function values?

Should there be an expression form of `if`?

Should there be an expression form of `=`?  (`:=`?)

Block scope in blocks; if the first assignment to a variable occurs inside
a block, its scope is that block.  It cannot be seen after that block closes.
(Shadowing is not possible; if the first assignment was before, that outer
variable is what gets updated.)
