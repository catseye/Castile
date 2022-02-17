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
*   Nested structs can be tested for deep equality.
*   Values of union type can be tested for equality.

### Implementation

*   Requesting the AST be dumped, will also dump the AST with
    type assignments, if an error occurs during type checking.
*   Established an abstract base class for compiler backends.

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