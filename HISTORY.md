History of Castile
==================

Castile 0.5
-----------

### Distribution

*   Added HISTORY.md file.

### Language

*   Scoped structs can be declared with the `for (...)` clause
    after the struct.  A value of a scope struct can only be
    `make`d, and the fields of such a value can only be accessed,
    lexically inside one of the definitions named in the `for`.
*   Structs cannot be tested for equality with the `==` and `!=`
    operators.  Instead the programmer should write a function
    that compares structs for equality, if desired.
*   Values of union type can be tested for equality, but only if
    none of the types involved in the union are structs.

### Implementation

*   Lexical scanner has been split off from parser code, into
    its own module.  A performance bug (using O(n^2) space
    instead of O(n)) during scanning has also been fixed.
*   Line numbers are recorded in the AST when parsing, and
    reported on type errors when type errors occur.
*   Requesting the AST be dumped, will also dump the AST with
    type assignments, if an error occurs during type checking.
*   Established an abstract base class for compiler backends.
*   Fixed a bug where tagged values were being tagged again
    during a cast from a union type to another union type.

Castile 0.4
-----------

### Distribution

*   Re-focused project: Castile is a simple imperative language
    with union types.
*   Released under a 3-clause BSD license.

### Language

*   `struct`s cannot be compared for order, it is a static error.
*   A union type is allowed to be promoted to a bigger union type,
    or to itself.

### Implementation

*   Completed the C-generating backend of the compiler: it passes all tests now.
*   Implemented `str` builtin, equality testing of `struct`s in all backends.
*   Improved pretty-printing of code in C and Ruby backends.
*   Implemented `ne` in stackmac implementation.

Castile 0.3 revision 2021.0625
------------------------------

*   Updated implementation to run under both Python 2 and Python 3.
*   Refactored test suite, making it more idiomatic Falderal.

Castile 0.3 revision 2016.0331
------------------------------

*   Fixed generated Ruby code that worked in Ruby 1.8 but fails in Ruby 1.9.

Castile 0.3 revision 2015.0101
------------------------------

*   Stopped using deprecated Falderal variable names in test suite.

Castile 0.3
-----------

*   Treatment of local variables became more Python-like.
*   Beginnings of a C backend in compiler.

Castile 0.2
-----------

*   Heavy development of the language, with many changes.
*   Added JavaScript, Ruby, and stackmac (stack-machine) backends to compiler.

Castile 0.1
-----------

Initial release of Castile, an unremarkable language with an unremarkable
compiler/interpreter in Python.
