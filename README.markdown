Castile
=======

This is the reference distribution for Castile, an unremarkable programming
language.

The current version of Castile is 0.2-PRE.  It is not only subject to change,
it is pretty much *guaranteed* to change.

Unlike most of my programming languages, there is nothing that could really
be described as innovative or experimental or even particularly unusual
about Castile.  It is not a particularly comfortable programming experience,
often forcing the programmer to be explicit and verbose.  It is influenced by:

*   **C**: Most of Castile's syntax follows C, but it is generally more
    permissive (semicolons are optional, types of local variables and return
    types for functions do not have to be declared, etc.)  It has a type
    system (where `struct`s are the only types with name equivalence) which
    can be applied statically.  It has function values, but not closures.

*   **Pascal**: All local variables used in a function must be declared at
    the start of the function body.

*   **Rust**: There is a union type, to which values must be explicitly
    promoted (with `as`) and extracted (with `typecase ... is`.)  This is
    like Rust's `Enum`, which is (to quote its tutorial) "much like the
    'tagged union' pattern in C, but with better static guarantees."  Along
    with structs, this provides something similar to algebraic data typing,
    as seen in languages such as Haskell, Scala, etc.

*   **Eightebed**: A few years back I realized that pointers that can
    assume a null value are really a variant type, like Haskell's `Maybe`.
    Of course, in most languages, the property of being null isn't
    captured by the type; you can dereference a pointer in C whether it's
    valid or not.  In Castile, this is captured with a union type which
    includes `void`, and `typecase` generalizes Eightebed's `ifvalid`.

*   **?**: Expressions (statements) within a block must have void type,
    except the final expression, which is returned as the result of the
    block.  Local variables are mutable, but arguments and globals
    are not, and neither are the fields of structs.  There are no pointers.
    (These features are not really original, but it's hard to say what
    languages I'm taking them from.  Many of them seem to be a result of me
    coming to some kind of C/Rust/functional language compromise.  I'll
    say more when I have a more developed idea of what type/memory safety
    in Castile should be.)

Also unlike most of my programming languages (with the exceptions of ILLGOL
and Bhuna), it was "designed by building" -- I wrote an interpreter, and
the language it happens to accept, I called Castile.

I wrote the interpreter in a very short span of time; most of it was done
within 24 hours of starting (but consider that I ripped off some of the
scanning/parsing code from ALPACA.)  A few days later, I extended the
implementation to also allow compiling to Javascript, and a few days after
that, I added a Ruby backend (why not, eh?)

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
can result in a compiled program with undefined behaviour.

Grammar
-------

The grammar is a little weird at points (especially the VarRef production,
which includes the possibility of assignment, even though that can really
only happen in a Stmt.)

    Program ::= {Defn [";"]}.
    Defn    ::= "fun" ident "(" [Arg {"," Arg}] ")" Body
              | "struct" ident "{" {ident ":" TExpr [";"]} "}"
              | ident (":" TExpr | "=" Literal).
    Arg     ::= ident [":" TExpr].
    Body    ::= "{" {VarDecl [";"]} {Stmt [";"]} "}".
    VarDecl ::= "var" ident "=" Expr0.
    Stmt    ::= "while" Expr0 Block
              | "typecase" VarRef "is" TExpr Block
              | "do" Expr0
              | "return" Expr0
              | If
              | Expr0.
    Block   ::= "{" {Stmt [";"]} "}".
    If      ::= "if" Expr0 Block ["else" (Block | If)].
    Expr0   ::= Expr1 {("and" | "or") Expr1} ["as" TExpr "in" TExpr].
    Expr1   ::= Expr2 {(">" | ">=" | "<" | "<=" | "==" | "!=") Expr2}.
    Expr2   ::= Expr3 {("+" | "-") Expr3}.
    Expr3   ::= Expr4 {("*" | "/") Expr4}.
    Expr4   ::= Expr5 {"(" [Expr0 {"," Expr0}] ")" | "." ident}.
    Expr5   ::= "make" ident "(" [ident ":" Expr0 {"," ident ":" Expr0}] ")"
              | "(" Expr0 ")"
              | "not" Expr1
              | Literal
              | VarRef.
    VarRef  ::= ident ["=" Expr0].
    Literal ::= strlit
              | ["-"] intlit
              | "true" | "false" | "null"
              | "fun" "(" [Arg {"," Arg}] ")" Body.
    TExpr   ::= "string"
              | "integer"
              | "boolean"
              | "void"
              | "function" "(" [TExpr {"," TExpr}] ")" ":" TExpr
              | "union" "(" [TExpr {"," TExpr}] ")"
              | ident.

Examples
--------

    -> Tests for functionality "Run Castile Program"

### Rudiments ###

Minimal correct program.

    | fun main() {}
    = 

A program may evaluate to a value.

    | fun main() { 160 }
    = 160

The function named `main` is the one that is evaluated when the
program is run.

    | fun foobar(a, b, c) { 100 }
    | fun main() { 120 }
    | fun f() { 140 }
    = 120

`main` should have no formal arguments.

    | fun main(a, b, c) {
    |   120
    | }
    ? type mismatch

But other functions may.

    | fun foobar(a, b) { b }
    | fun main() { foobar(100, 200) }
    = 200

Defined function names must be unique.

    | fun dup() { 1 }
    | fun dup() { 2 }
    ? duplicate

Formal argument names must be unique.

    | fun f(g, g) {}
    | fun main() { 1 }
    ? defined

Functions must be defined before they are referenced.

    | fun main() { f(7) }
    | fun f(g) { g }
    ? undefined

Either that, or forward-declared.

    | f : function(integer): integer
    | fun main() { f(7) }
    | fun f(g) { g * 2 }
    = 14

If forward-declared, types must match.

    | f : function(integer): string
    | fun main() { f(7) }
    | fun f(g) { g * 2 }
    ? type mismatch

Arguments must match...

    | fun f(g, h) { g * 2 + h * 2 }
    | fun main() { f(7) }
    ? argument mismatch

    | fun f(g, h) { g * 2 + h * 2 }
    | fun main() { f(7,8,9) }
    ? argument mismatch

### Statements ###

Statements are commands that have the type void and are executed for their
side-effects.  So, in general, statements may not be expressions.  The
exception is that the last statement in a block may be an expression; the
result of that expression is the value of the block.

    | fun main() {
    |   20 * 8
    | }
    = 160

    | fun main() {
    |   20 + 3 * 8;
    |   20 * 8
    | }
    ? type mismatch

An `if`/`else` lets you make decisions.

    | fun main() {
    |   var a = 0;
    |   if 3 > 2 {
    |     a = 70
    |   } else {
    |     a = 80
    |   }
    |   a
    | }
    = 70

An `if` need not have an `else`.

    | fun main() {
    |   var a = 60
    |   if 3 > 2 {
    |     a = 70
    |   }
    |   a
    | }
    = 70

`if` always typechecks to void, one branch or two.

    | fun main() {
    |   var a = 60
    |   if 3 > 2 {
    |     a = 70
    |   }
    | }
    = 

    | fun main() {
    |   var a = 60
    |   if 3 > 2 {
    |     a = 70
    |   } else {
    |     a = 90
    |   }
    | }
    = 

If an `if` does have an `else`, the part after `else` must be either a block
(already shown) or another `if`.

    | fun main() {
    |   if 2 > 3 {
    |     return 60
    |   } else if 4 > 5 {
    |     return 0
    |   } else {
    |     return 1
    |   }
    | }
    = 1

No dangling else problem.

    | fun main() {
    |   if 2 > 3 {
    |     return 60
    |   } else if 4 < 5 {
    |     return 99
    |   } else {
    |     return 1
    |   }
    | }
    = 99

`while` loops.

    | fun main() {
    |   var a = 0 var b = 4
    |   while b > 0 {
    |     a = a + b
    |     b = b - 1
    |   }
    |   a
    | }
    = 10

A `while` itself has void type.

    | fun main() {
    |   var a = 0; var b = 4;
    |   while b > 0 {
    |     a = a + b;
    |     b = b - 1;
    |   }
    | }
    = 

`break` may be used to prematurely exit a `while`.

    | fun main() {
    |   var a = 0; var b = 0;
    |   while true {
    |     a = a + b;
    |     b = b + 1;
    |     if (b > 4) { break; }
    |   }
    |   a
    | }
    = 10

### Expressions ###

Precedence.

    | fun main() {
    |   2 + 3 * 4  /* not 20 */
    | }
    = 14

Unary negation.

    | fun main() {
    |   -3
    | }
    = -3

    | fun main() {
    |   2+-5
    | }
    = -3

Minus sign must be right in front of a number.

    | fun main() {
    |   -(4)
    | }
    ? Expected

Unary not.

    | fun main() {
    |   not (4 > 3)
    | }
    = False

Precedence of unary not.

    | fun main() {
    |   not true or true
    | }
    = True

    | fun main() {
    |   not 3 > 4
    | }
    = True

### Local Variables ###

Local variables.

    | fun main() {
    |   var a = 6;
    |   var b = 7;
    |   a + b
    | }
    = 13

Local variable names must be unique.

    | fun main() {
    |   var a = 6;
    |   var a = 7;
    |   a + b
    | }
    ? shadows

Local variables can be assigned functions.

    | fun ancillary(x) { x * 2 }
    | fun main() {
    |   var a = ancillary;
    |   a(7)
    | }
    = 14

Local variables can be assigned.

    | fun main() {
    |   var a = 6;
    |   a = a + 12;
    |   a
    | }
    = 18

    | fun main() {
    |   var a = 6;
    |   a = 99;
    |   a
    | }
    = 99

    | fun main() {
    |   var a = 6;
    |   z = 99;
    |   a
    | }
    ? undefined

    | fun main() {
    |   var z = 6;
    |   a
    | }
    ? undefined

Assignment, though it syntactically may occur in expressions, has a type of
void, so it can only really happen at the statement level.

    | fun main() {
    |   var a = 0; var b = 0;
    |   a = b = 9;
    | }
    ? type mismatch

Variables may only be declared in a function body, not an inner block.

    | fun main() {
    |   var a = 0;
    |   if 3 > 2 {
    |     var a = 7;
    |   }
    |   a
    | }
    ? keyword

Variables must be declared at the start of a function body.

    | fun main() {
    |   print("Hi");
    |   var a = 1;
    |   if 3 > 2 {
    |     a = 7;
    |   }
    |   a
    | }
    ? keyword

Variables in upper scopes may be modified.

    | fun main() {
    |   var a = 0
    |   if 3 > 2 {
    |     a = 4;
    |   }
    |   a
    | }
    = 4

### Non-local Values ###

Literals may appear at the toplevel.    Semicolons are optional at toplevel.

    | factor = 5;
    | fun main() {
    |   6 * factor
    | }
    = 30

Toplevel literals may not be updated.

    | factor = 5
    | fun main() {
    |   factor = 7
    | }
    ? cannot assign

Toplevel literals may not be shadowed.

    | factor = 5;
    | fun main() {
    |   var factor = 7;
    |   6 * factor
    | }
    ? shadows

Toplevel literals may be function literals (the syntax we've been using is just sugar.)

    | main = fun() {
    |   7
    | }
    = 7

Truth and falsehood are builtin toplevels.

    | fun main() {
    |   true or false
    | }
    = True

    | fun main() {
    |   false and true
    | }
    = False

So is `null`, which is the single value of `void` type.

    | fun wat(x: void) { 3 }
    | fun main() {
    |   wat(null)
    | }
    = 3

### More on Functions ###

Function arguments may not be updated.

    | fun foo(x) {
    |   x = x + 14;
    |   x
    | }
    | fun main() {
    |   foo(7)
    | }
    ? cannot assign

Factorial can be computed.

    | factorial : function(integer): integer
    | fun factorial(a) {
    |   if a == 0 {
    |     return 1
    |   } else {
    |     return a * factorial(a - 1)
    |   }
    | }
    | fun main() {
    |   factorial(6)
    | }
    = 720

Literal functions.

    | fun main() {
    |   var inc = fun(x) { x + 1 };
    |   inc(7)
    | }
    = 8

    | fun main() {
    |   fun(x){ x + 1 }(9)
    | }
    = 10

    | fun main() {
    |   var a = 99;
    |   a = fun(x){ x + 1 }(9);
    |   a
    | }
    = 10

Literal functions can have local variables, loops, etc.

    | fun main() {
    |   var z = 99;
    |   z = fun(x) {
    |     var a = x;  var b = x;
    |     while a > 0 {
    |       b = b + a; a = a - 1;
    |     }
    |     return b
    |   }(9);
    |   z
    | }
    = 54

Literal functions can define other literal functions...

    | fun main() {
    |   fun(x){ fun(y){ fun(z){ z + 1 } } }(4)(4)(10)
    | }
    = 11

Literal functions can access globals.

    | oid = 19
    | fun main() {
    |   fun(x){ x + oid }(11);
    | }
    = 30

Literal functions cannot access variables declared in enclosing scopes.

    | fun main() {
    |   var oid = 19;
    |   fun(x){ x + oid }(11);
    | }
    ? undefined

Literal functions cannot access arguments declared in enclosing scopes.

    | fun main() {
    |   fun(x){ fun(y){ fun(z){ y + 1 } } }(4)(4)(10)
    | }
    ? undefined

Functions can be passed to functions and returned from functions.

    | fun double(x) { x * 2 }
    | fun triple(x) { x * 3 }
    | fun apply_and_add_one(f:function(integer):integer, x) { f(x) + 1 }
    | fun select(a) { if a > 10 { return double } else { return triple } }
    | fun main() {
    |   var t = select(5);
    |   var d = select(15);
    |   var p = t(10);
    |   apply_and_add_one(d, p)
    | }
    = 61

`return` may be used to prematurely return a value from a function.

    | fun foo(y) {
    |   var x = y
    |   while x > 0 {
    |     if x < 5 {
    |       return x;
    |     }
    |     x = x - 1;
    |   }
    |   17
    | }
    | fun main() {
    |   foo(10) + foo(0)
    | }
    = 21

Type of value returned must jibe with value of function's block.

    | fun foo(x) {
    |   return "string";
    |   17
    | }
    | fun main() {
    |   foo(10) + foo(0)
    | }
    ? type mismatch

Type of value returned must jibe with other return statements.

    | fun foo(x) {
    |   if x > 0 {
    |     return "string";
    |   } else {
    |     return 17
    |   }
    | }
    | fun main() {
    |   foo(10) + foo(0)
    | }
    ? type mismatch

### Builtins ###

The usual.

    | fun main() {
    |   print("Hello, world!")
    | }
    = Hello, world!

Some standard functions are builtin and available as toplevels.

    | fun main() {
    |   var a = "hello";
    |   var b = len(a);
    |   while b > 0 {
    |     print(a);
    |     b = b - 1;
    |     a = substr(a, 1, b)
    |   }
    | }
    = hello
    = ello
    = llo
    = lo
    = o

The `+` operator is not string concatenation.  `concat` is.

    | fun main() {
    |   "hello " + "world"
    | }
    ? type mismatch

    | fun main() {
    |   concat("hello ", "world")
    | }
    = 'hello world'

The builtin toplevels are functions and functions need parens.

    | fun main() {
    |   print "hi"
    | }
    ? type mismatch

Note that the above was the motivation for requiring statements to have void
type; if non-void exprs could be used anywhere, that would just throw away
the function value `print` (b/c semicolons are optional) and return 'hi'.

### Struct Types ###

Record types.  You can define them:

    | struct person { name: string; age: integer }
    | main = fun() {}
    = 

And make them:

    | struct person { name: string; age: integer }
    | main = fun() {
    |   var j = make person(name:"Jake", age:23);
    |   j
    | }
    = {'name': 'Jake', 'age': 23}

Structs must be defined somewhere.

    | main = fun() {
    |   var j = make person(name:"Jake", age:23);
    |   j
    | }
    ? undefined

Structs need not be defined before use.

    | main = fun() {
    |   var j = make person(name:"Jake", age:23);
    |   j
    | }
    | struct person { name: string; age: integer }
    = {'name': 'Jake', 'age': 23}

Structs may contain structs which don't exist.  (Surprisingly.  Might just leave this in.)

    | struct person { name: string; age: foobar }
    | main = fun() { 333 }
    = 333

    | struct person { name: string; age: foobar }
    | main = fun() { make person(name:"Jake", age:23) }
    ? type mismatch

Types must match when making a struct.

    | struct person { name: string; age: integer }
    | main = fun() {
    |   var j = make person(name:"Jake", age:"Old enough to know better");
    |   j
    | }
    ? type mismatch

    | struct person { name: string; age: integer }
    | main = fun() {
    |   var j = make person(name:"Jake");
    |   j
    | }
    ? argument mismatch

    | struct person { name: string }
    | main = fun() {
    |   make person(name:"Jake", age:23);
    | }
    ? argument mismatch

Structs can be passed to functions.

    | struct person { name: string; age: integer }
    | fun wat(bouncer: person) { bouncer }
    | main = fun() {
    |   var j = make person(name:"Jake", age:23);
    |   wat(j)
    | }
    = {'name': 'Jake', 'age': 23}

Structs have name equivalence, not structural.

    | struct person { name: string; age: integer }
    | struct city { name: string; population: integer }
    | fun wat(hometown: city) { hometown }
    | main = fun() {
    |   var j = make person(name:"Jake", age:23);
    |   wat(j)
    | }
    ? type mismatch

Struct fields must all be unique.

    | struct person { name: string; name: string }
    | main = fun() {
    |   var j = make person(name:"Jake", name:"Smith");
    | }
    ? defined

Values can be retrieved from structs.

    | struct person { name: string; age: integer }
    | fun age(bouncer: person) { bouncer.age }
    | main = fun() {
    |   var j = make person(name:"Jake", age:23);
    |   age(j)
    | }
    = 23

    | struct person { name: string }
    | fun age(bouncer: person) { bouncer.age }
    | main = fun() {
    |   var j = make person(name:"Jake");
    |   age(j)
    | }
    ? undefined

Different structs may have the same field name in different positions.

    | struct person { name: string; age: integer }
    | struct city { population: integer; name: string }
    | main = fun() {
    |   var j = make person(name:"Jake", age:23);
    |   var w = make city(population:600000, name:"Winnipeg");
    |   print(j.name)
    |   print(w.name)
    | }
    = Jake
    = Winnipeg

Can't define the same struct multiple times.

    | struct person { name: string; age: integer }
    | struct person { name: string; age: string }
    | fun main() { 333 }
    ? duplicate

Structs may refer to themselves.

    | struct recursive {
    |   next: recursive;
    | }
    | fun main() { 333 }
    = 333

    | struct odd {
    |   next: even;
    | }
    | struct even {
    |   next: odd;
    | }
    | fun main() { 333 }
    = 333

But you can't actually make one of these infinite structs.

    | struct recursive {
    |   next: recursive;
    | }
    | fun main() { make recursive(next:make recursive(next:"nooo")) }
    ? type mismatch

### Union Types ###

Values of union type are created with the type promotion operator,
`as ... in ...`.  Type promotion has a very low precedence, and can be
applied to any expression.

The type after the `in` must be a union.

    | fun main() {
    |   var a = 20;
    |   var b = 30;
    |   a + b as integer in string
    | }
    ? bad cast

The type after the `as` must be one of the types in the union.

    | fun main() {
    |   var a = 20;
    |   var b = 30;
    |   a + b as integer in union(string, void)
    | }
    ? bad cast

The type after the `as` must be the type of the expression.

    | fun main() {
    |   var a = 20;
    |   var b = 30;
    |   a + b as integer in union(integer, string)
    | }
    = ('Type(integer:)', 50)

All good looks like this:

    | fun main() {
    |   var a = 20;
    |   var b = 30;
    |   a + b as integer in union(integer, string)
    | }
    = ('Type(integer:)', 50)

Union types.

    | fun foo(a, b: union(integer, string)) {
    |   a + 1
    | }
    | main = fun() {
    |   var a = 0;
    |   a = foo(a, 333 as integer in union(integer, string));
    |   a = foo(a, "hiya" as string in union(integer, string));
    |   a
    | }
    = 2

The `typecase` construct can operate on the "right" type of a union.

    | fun foo(a, b: union(integer, string)) {
    |   var r = a;
    |   typecase b is integer {
    |     r = r + b;
    |   };
    |   typecase b is string {
    |     r = r + len(b);
    |   };
    |   r
    | }
    | main = fun() {
    |   var a = 0;
    |   a = foo(a, 333 as integer in union(integer, string));
    |   a = foo(a, "hiya" as string in union(integer, string));
    |   a
    | }
    = 337

This is a very strange case in the language.  Thankfully, assignment
typechecks as void, without any automatic promotion to the union type...

    | fun foo(b: union(integer, void)) {
    |   var a = b;
    |   typecase a is integer {
    |     print("yes it's an integer");
    |   }
    |   typecase a = 7 as integer in union(integer, void) is void {
    |     print("yes it's void too");
    |   }
    | }
    | main = fun() {
    |   foo(7 as integer in union(integer, void))
    | }
    ? void not a union

### Struct Types + Union Types ###

Union types may be used to make fields "nullable", so that
you can actually make finite, recursive data types.

    | struct list {
    |   value: string;
    |   next: union(list, integer);
    | }
    | main = fun() {
    |   make list(value:"first", next:
    |     make list(value:"second",
    |               next:0 as integer in union(list, integer)
    |              ) as list in union(list, integer))
    | }
    = {'value': 'first', 'next': ('StructType(list:)', {'value': 'second', 'next': ('Type(integer:)', 0)})}

You may want to use helper functions to hide this ugliness.

    | struct list {
    |   value: string;
    |   next: union(list, void);
    | }
    | fun singleton(v: string) {
    |   make list(value:v, next:null as void in union(list, void))
    | }
    | fun cons(v: string, l: list) {
    |   make list(value:v, next:l as list in union(list, void))
    | }
    | main = fun() {
    |   cons("first", singleton("second"))
    | }
    = {'value': 'first', 'next': ('StructType(list:)', {'value': 'second', 'next': ('Type(void:)', None)})}
