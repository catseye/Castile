TODO
----

Don't output final value.  Command-line arguments passed to `main`.  (`sysmain`?)

Tests for all the edge cases for function literals (closure variable return ugghness.)

Lack of `break` is annoying.

### Implementation ###

Better use of exceptions (don't use Python's SyntaxError.)

AST nodes should have source line numbers, it would be really nice.

Make evaluator independent of typechecker?  The few places the typechecker
modifies the AST -- find another way (have parser do it / find way to not need it.)

### Design ###

Actual function closures -- but optional(?) as compiling to C is easier without them.

Should there be an expression form of `if`?

Should there be an expression form of `=`?  (`:=`?)

Should a block be a valid statement, with block scope?

Should we have automatic promotion (value tagging?)

Should `make` allow / require field names to be given?
