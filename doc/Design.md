Castile Design Notes
====================

(These are the original notes from the original README.)

Unlike most of my programming languages, there is nothing that could really
be described as innovative or experimental or even particularly unusual
about Castile.  It is not a particularly comfortable programming experience,
often forcing the programmer to be explicit and verbose.

The reference implementation is slightly less unremarkable than the language
itself, if only for the fact that it compiles to four different target
languages: Javascript, Ruby, a hypothetical stack machine called
"stackmac" (a stackmac emulator ships with this distribution,) and (coming
soon) C.

Castile's influences might include:

*   **C**: Most of Castile's syntax follows C, but it is generally more
    permissive (semicolons are optional, types of local variables and return
    types for functions do not have to be declared, etc.)  It has a type
    system (where `struct`s are the only types with name equivalence) which
    can be applied statically.  It has function values, but not closures.

*   **Rust**: There is a union type, to which values must be explicitly
    promoted (with `as`) and extracted (with `typecase ... is`.)  This is
    like Rust's `Enum`, which is (to quote its tutorial) "much like the
    'tagged union' pattern in C, but with better static guarantees."  Along
    with structs, this provides something similar to algebraic data typing,
    as seen in languages such as Haskell, Scala, etc.

*   **Eightebed**: A few years back I realized that pointers that can
    assume a null value are really a variant type, like Haskell's `Maybe`.
    Of course, in most languages with pointers, the property of being null
    isn't captured by the type; you can go ahead and dereference a pointer
    in C or Java, whether it's valid or not.  In Castile, this is captured
    with a union type which includes `void`, and `typecase` generalizes
    Eightebed's `ifvalid`.

*   **Python**: The first time a local variable is assigned counts as its
    declaration as a local.

*   **Ruby**: The last expression in a function body is the return value
    of that function; no explicit `return` is needed there.  (But unlike
    Ruby, and more like Pascal or linted C, all *other* expressions in
    statement position within a block must have void type.)

*   **Erlang** (or any other purely functional language): There are no
    language-level pointers; sharing, if it happens at all, must be
    orchestrated by the implementation.  Global variables and function
    arguments are not mutable, and neither are the fields of structs.
    (But unlike Erlang, local variables *are* mutable.)

Some lines of research underneath all this are, if all we have is a relatively
crude language, but we make it typesafe and give it a slightly nicer type
system, does it suffice to make programming tolerable?  Do tolerable ways of
managing memory without a full garbage collector present themselves?  Does
having a simple compiler which can be target many backends provide any
advantages?

Also unlike most of my programming languages (with the exceptions of ILLGOL
and Bhuna), Castile was largely "designed by building" -- I wrote an
interpreter, and the language it happens to accept, I called Castile.
I wrote the interpreter in a very short span of time; most of it was done
within 24 hours of starting (but consider that I ripped off some of the
scanning/parsing code from ALPACA.)  A few days later, I extended the
implementation to also allow compiling to Javascript, and a few days after
that, I added a Ruby backend (why not, eh?), and over the next few days,
the stackmac backend and emulator.

This document contains what is as close as there is to a specification of
the language, in the form of a Falderal test suite.  The interpreter and all
compilers pass all the tests, but there are known shortcomings in at least
the compilers (no name mangling, etc.)

The `eg` directory contains a few example Castile programs, including a
string tokenizer.

One area where the Castile implementation is not entirely unremarkable is
that the typechecker is not required to be run.  Unchecked Castile is
technically a different language from Castile; there are Castile programs
which would result in an error, where the Unchecked Castile program would
*not* (because it never executes the part of the program with a bad type.)
However, Unchecked Castile programs should be otherwise well-behaved;
any attempt to execute code which would have resulted in a type failure,
will result in a crash.  Note, however, that this only applies to the
evaluator, not any of the compiler backends.  Compiling Unchecked Castile
will simply not work (the backend will crash when it can't see any types.)
