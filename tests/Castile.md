Castile
=======

This is a test suite for Castile, written in [Falderal][] format.

While it cannot serve as a complete specification, it comes as
close as anything currently does to a specification for Castile.

[Falderal]: https://catseye.tc/node/Falderal

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

    | f : integer -> integer
    | fun main() { f(7) }
    | fun f(g) { g * 2 }
    = 14

If forward-declared, types must match.

    | f : integer -> string
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
    |   a = 0;
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
    |   a = 60
    |   if 3 > 2 {
    |     a = 70
    |   }
    |   a
    | }
    = 70

`if` always typechecks to void, one branch or two.

    | fun main() {
    |   a = 60
    |   if 3 > 2 {
    |     a = 70
    |   }
    | }
    = 

    | fun main() {
    |   a = 60
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
    |   a = 0 b = 4
    |   while b > 0 {
    |     a = a + b
    |     b = b - 1
    |   }
    |   a
    | }
    = 10

A `while` itself has void type.

    | fun main() {
    |   a = 0; b = 4;
    |   while b > 0 {
    |     a = a + b;
    |     b = b - 1;
    |   }
    | }
    = 

`break` may be used to prematurely exit a `while`.

    | fun main() {
    |   a = 0; b = 0;
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
    |   a = 6;
    |   b = 7;
    |   a + b
    | }
    = 13

Local variables can be assigned functions.

    | fun ancillary(x) { x * 2 }
    | fun main() {
    |   a = ancillary;
    |   a(7)
    | }
    = 14

Local variables can be assigned.

    | fun main() {
    |   a = 6;
    |   a = a + 12;
    |   a
    | }
    = 18

    | fun main() {
    |   a = 6;
    |   z = 99;
    |   a
    | }
    = 6

    | fun main() {
    |   z = 6;
    |   a
    | }
    ? undefined

Local variables cannot occur in expressions until they are defined by an
initial assignment.

    | fun main() {
    |   z = a * 10;
    |   a = 10;
    |   z
    | }
    ? undefined

A local variables may not be defined inside an `if` or `while` or `typecase`
block, as it might not be executed.

    | fun main() {
    |   if (4 > 5) {
    |     a = 10;
    |   } else {
    |     b = 11;
    |   }
    |   b
    | }
    ? within control

    | fun main() {
    |   b = false;
    |   while b {
    |     a = 10;
    |   }
    |   a
    | }
    ? within control

    | fun main() {
    |   a = 55 as integer|string;
    |   typecase a is string {
    |     b = 7
    |   }
    |   a
    | }
    ? within control

Assignment, though it syntactically may occur in expressions, has a type of
void, so it can only really happen at the statement level.

    | fun main() {
    |   a = 0; b = 0;
    |   a = b = 9;
    | }
    ? type mismatch

Variables in upper scopes may be modified.

    | fun main() {
    |   a = 0
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

Toplevel literals may not be updated.  (And thus

    | factor = 5
    | fun main() {
    |   factor = 7
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
    ? shadows

Factorial can be computed.

    | factorial : integer -> integer
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
    |   inc = fun(x) { x + 1 };
    |   inc(7)
    | }
    = 8

    | fun main() {
    |   fun(x){ x + 1 }(9)
    | }
    = 10

    | fun main() {
    |   a = 99;
    |   a = fun(x){ x + 1 }(9);
    |   a
    | }
    = 10

Literal functions can have local variables, loops, etc.

    | fun main() {
    |   z = 99;
    |   z = fun(x) {
    |     a = x;  b = x;
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
    |   oid = 19;
    |   fun(x){ x + oid }(11);
    | }
    ? undefined

Literal functions cannot access arguments declared in enclosing scopes.

    | fun main() {
    |   fun(x){ fun(y){ fun(z){ y + 1 } } }(4)(4)(10)
    | }
    ? undefined

Functions can be passed to functions and returned from functions.

    | fun doubble(x) { x * 2 }
    | fun triple(x) { x * 3 }
    | fun apply_and_add_one(f: (integer -> integer), x) { f(x) + 1 }
    | fun sellect(a) { if a > 10 { return doubble } else { return triple } }
    | fun main() {
    |   t = sellect(5);
    |   d = sellect(15);
    |   p = t(10);
    |   apply_and_add_one(d, p)
    | }
    = 61

To overcome the syntactic ambiguity with commas, function types
in function definitions must be in parens.

    | fun add(x, y) { x + y }
    | fun mul(x, y) { x * y }
    | fun do_it(f: (integer, integer -> integer), g) {
    |   f(3, g)
    | }
    | fun main() {
    |   do_it(mul, 4) - do_it(add, 4)
    | }
    = 5

`return` may be used to prematurely return a value from a function.

    | fun foo(y) {
    |   x = y
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

### Equality ###

Equality, inequality, boolean operators.

    | fun main() {
    |   if 15 == 15 and ((15 != 14) or false) {
    |     print("struth")
    |   }
    | }
    = struth

    | fun main() {
    |   if "five" == "five" and (("six" != "seven") or false) {
    |     print("struth")
    |   }
    | }
    = struth

Equality cannot be checked between two values of different types.

    | fun main() {
    |   if 15 == "fifteen" {
    |     print("wat")
    |   }
    | }
    ? mismatch

    | fun main() {
    |   if 15 != "fifteen" {
    |     print("wat")
    |   }
    | }
    ? mismatch

Equality can be checked between unions.

    | fun main() {
    |   a = 40 as string|integer
    |   b = 40 as string|integer
    |   if a == b {
    |     print("it is")
    |   }
    | }
    = it is

    | fun main() {
    |   a = 40 as string|integer
    |   b = "beep" as string|integer
    |   if a != b {
    |     print("correct")
    |   }
    | }
    = correct

Equality cannot be tested between two disjoint unions.

    | fun main() {
    |   a = 40 as string|integer
    |   b = 40 as integer|void
    |   if a == b {
    |     print("correct")
    |   }
    | }
    ? mismatch

### Builtins ###

The usual.

    | fun main() {
    |   print("Hello, world!")
    | }
    = Hello, world!

Some standard functions are builtin and available as toplevels.

    | fun main() {
    |   a = "hello";
    |   b = len(a);
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
    |   print("hello " + "world")
    | }
    ? type mismatch

    | fun main() {
    |   print(concat("hello ", "world"))
    | }
    = hello world

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

And make them.

    | struct person { name: string; age: integer }
    | main = fun() {
    |   j = make person(name:"Jake", age:23);
    |   print("ok")
    | }
    = ok

And extract the fields from them.

    | struct person { name: string; age: integer }
    | main = fun() {
    |   j = make person(name:"Jake", age:23);
    |   print(j.name)
    |   if j.age > 20 {
    |     print("Older than twenty")
    |   } else {
    |     print("Underage")
    |   }
    | }
    = Jake
    = Older than twenty

Structs must be defined somewhere.

    | main = fun() {
    |   j = make person(name:"Jake", age:23);
    |   j
    | }
    ? undefined

Structs need not be defined before use.

    | main = fun() {
    |   j = make person(name:"Jake", age:23);
    |   j.age
    | }
    | struct person { name: string; age: integer }
    = 23

Structs may not contain structs which don't exist.

    | struct person { name: string; age: foobar }
    | main = fun() { 333 }
    ? undefined

Types must match when making a struct.

    | struct person { name: string; age: integer }
    | main = fun() {
    |   j = make person(name:"Jake", age:"Old enough to know better");
    |   j.age
    | }
    ? type mismatch

    | struct person { name: string; age: integer }
    | main = fun() {
    |   j = make person(name:"Jake");
    |   j.age
    | }
    ? argument mismatch

    | struct person { name: string }
    | main = fun() {
    |   j = make person(name:"Jake", age:23);
    |   j.age
    | }
    ? argument mismatch

Order of field initialization when making a struct doesn't matter.

    | struct person { name: string; age: integer }
    | main = fun() {
    |   j = make person(age: 23, name:"Jake");
    |   j.age
    | }
    = 23

Structs can be tested for equality.  (Since structs are immutable, it
doesn't matter if this is structural equality or identity.)

    | struct person { name: string; age: integer }
    | main = fun() {
    |   j = make person(age: 23, name:"Jake");
    |   k = make person(name:"Jake", age: 23);
    |   j == k
    | }
    = True

    | struct person { age: integer; name: string }
    | main = fun() {
    |   j = make person(age: 23, name:"Jake");
    |   k = make person(age: 23, name:"John");
    |   j == k
    | }
    = False

    | struct person { age: integer; name: string }
    | main = fun() {
    |   j = make person(age: 23, name:"Jake");
    |   k = make person(age: 21, name:"Jake");
    |   j != k
    | }
    = True

Structs of two different types cannot be tested for equality.

    | struct person { age: integer; name: string }
    | struct individual { age: integer; name: string }
    | main = fun() {
    |   j = make person(age: 23, name:"Jake");
    |   k = make individual(age: 23, name:"Jake");
    |   j == k
    | }
    ? mismatch

Structs cannot be compared for ordering.

    | struct person { age: integer; name: string }
    | main = fun() {
    |   j = make person(age: 23, name:"Jake");
    |   k = make person(age: 21, name:"Jake");
    |   j > k
    | }
    ? structs cannot be compared for order

Structs can be passed to functions.

    | struct person { name: string; age: integer }
    | fun wat(bouncer: person) { bouncer.age }
    | main = fun() {
    |   j = make person(name:"Jake", age:23);
    |   wat(j)
    | }
    = 23

Structs have name equivalence, not structural.

    | struct person { name: string; age: integer }
    | struct city { name: string; population: integer }
    | fun wat(hometown: city) { hometown }
    | main = fun() {
    |   j = make person(name:"Jake", age:23);
    |   wat(j)
    | }
    ? type mismatch

Struct fields must all be unique.

    | struct person { name: string; name: string }
    | main = fun() {
    |   j = make person(name:"Jake", name:"Smith");
    | }
    ? defined

Values can be retrieved from structs.

    | struct person { name: string; age: integer }
    | fun age(bouncer: person) { bouncer.age }
    | main = fun() {
    |   j = make person(name:"Jake", age:23);
    |   age(j)
    | }
    = 23

    | struct person { name: string }
    | fun age(bouncer: person) { bouncer.age }
    | main = fun() {
    |   j = make person(name:"Jake");
    |   age(j)
    | }
    ? undefined

Different structs may have the same field name in different positions.

    | struct person { name: string; age: integer }
    | struct city { population: integer; name: string }
    | main = fun() {
    |   j = make person(name:"Jake", age:23);
    |   w = make city(population:600000, name:"Winnipeg");
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
`as ...`.  Type promotion has a very low precedence, and can be
applied to any expression.

The type after the `as` must be a union.

    | fun main() {
    |   a = 20;
    |   b = 30;
    |   a + b as integer
    | }
    ? bad cast

The type of the value being cast by the `as` must be one of the types in the union.

    | fun main() {
    |   a = 20;
    |   b = 30;
    |   a + b as string|void
    | }
    ? bad cast

The type after the `as` must be the type of the expression.

    | fun main() {
    |   a = 20;
    |   b = 30;
    |   c = a + b as integer|string
    |   print("ok")
    | }
    = ok

Each of the individual types named in the union type must be unique.

    | fun foo(a, b: integer|string) {
    |   print("ok")
    | }
    | fun main() {
    |   a = 20;
    |   b = 30;
    |   c = a + b as integer|integer|string
    |   foo(a, c)
    | }
    ? bad union type

One can, vacuously, promote a union type to itself.

    | fun main() {
    |   a = 20;
    |   b = 30;
    |   c = a + b as integer|string
    |   d = c as integer|string
    |   print("ok")
    | }
    = ok

One can promote a union type to another union type, so long as it is a superset.

    | fun main() {
    |   a = 20;
    |   b = 30;
    |   c = a + b as integer|string
    |   d = c as integer|string|void
    |   print("ok")
    | }
    = ok

One cannot promote a union type to a union type that is not a superset.

    | fun main() {
    |   a = 20;
    |   b = 30;
    |   c = a + b as integer|string
    |   d = c as integer|void
    |   print("ok")
    | }
    ? bad cast

Values of union type can be passed to functions.

    | fun foo(a, b: integer|string) {
    |   a + 1
    | }
    | main = fun() {
    |   a = 0;
    |   a = foo(a, 333 as integer|string);
    |   a = foo(a, "hiya" as integer|string);
    |   a
    | }
    = 2

Order of types in a union doesn't matter.

    | fun foo(a, b: integer|string) {
    |   a + 1
    | }
    | main = fun() {
    |   a = 0;
    |   a = foo(a, 333 as integer|string);
    |   a = foo(a, "hiya" as string|integer);
    |   a
    | }
    = 2

Trivial use of `typecase`.

    | main = fun() {
    |   a = 333 as integer|string;
    |   typecase a is integer {
    |     print("int")
    |   };
    | }
    = int

Inside a `typecase` the variable can be used as a value of
the determined type.

    | main = fun() {
    |   a = 333 as integer|string;
    |   typecase a is integer {
    |     print(str(a))
    |   };
    |   typecase a is string {
    |     print(a)
    |   };
    | }
    = 333

The `typecase` construct can operate on the "right" type of a union.

    | fun foo(a, b: integer|string) {
    |   r = a;
    |   typecase b is integer {
    |     r = r + b;
    |   };
    |   typecase b is string {
    |     r = r + len(b);
    |   };
    |   r
    | }
    | main = fun() {
    |   a = 0;
    |   a = foo(a, 333 as integer|string);
    |   a = foo(a, "hiya" as integer|string);
    |   a
    | }
    = 337

The expression in a `typecase` must be a variable.

    | main = fun() {
    |   a = 333 as integer|string;
    |   typecase 333 is integer {
    |     print("what?")
    |   };
    | }
    ? identifier

The expression in a `typecase` can be an argument to the function in
which the `typecase` occurs.

    | fun wat(j: integer|string) {
    |   typecase j is integer {
    |     print("integer")
    |   };
    | }
    | main = fun() {
    |   wat(444 as integer|string)
    | }
    = integer

The expression in a `typecase` cannot effectively be a global, as globals
must be literals and there is no way (right now) to make a literal of union
type.

Inside a `typecase` the variable cannot be updated.

    | main = fun() {
    |   a = 333 as integer|string;
    |   typecase a is integer {
    |     a = 700;
    |   };
    | }
    ? cannot assign

The union can include void.

    | main = fun() {
    |   j = null as void|integer;
    |   typecase j is void {
    |     print("nothing there")
    |   };
    | }
    = nothing there

### Struct Types + Union Types ###

Union types may be used to make fields of a struct "nullable", so that
you can in actuality create recursive, but finite, data structures.

    | struct list {
    |   value: string;
    |   next: list|integer;
    | }
    | main = fun() {
    |   l = make list(
    |     value: "first",
    |     next: make list(
    |       value: "second",
    |       next:0 as list|integer
    |     ) as list|integer)
    |   s = l.next
    |   typecase s is list {
    |     print(s.value)
    |   }
    | }
    = second

You may want to use helper functions to hide this ugliness.

    | struct list {
    |   value: string;
    |   next: list|void;
    | }
    | 
    | fun empty() {
    |   return null as list|void
    | }
    | 
    | fun cons(v: string, l: list|void) {
    |   make list(value:v, next:l) as list|void
    | }
    | 
    | fun nth(n, l: list|void) {
    |   u = l;
    |   v = u;
    |   k = n;
    |   while k > 1 {
    |     typecase u is void { break; }
    |     typecase u is list { v = u.next; }
    |     u = v;
    |     k = k - 1;
    |   }
    |   return u
    | }
    | 
    | main = fun() {
    |   l = cons("first", cons("second", cons("third", empty())));
    |   h = nth(2, l);
    |   typecase h is list { print(h.value); }
    | }
    = second

And in fact, you can restrict the union types to smaller sets to
better indicate the allowable types of the functions.  For example,
`cons` always returns a list, so that should be its return type,
not `list|void`.  Likewise, `nth` requires a list.  In this way we
can implement some of the "Parse, don't Validate" approach.

    | struct list {
    |   value: string;
    |   next: list|void;
    | }
    | 
    | fun cons(v: string, l: list) {
    |   make list(value:v, next:l as list|void)
    | }
    | 
    | fun singleton(v: string) {
    |   make list(value:v, next:null as list|void)
    | }
    | 
    | fun nth(n, l: list) {
    |   u = l as list|void;
    |   v = u;
    |   k = n;
    |   while k > 1 {
    |     typecase u is void { break; }
    |     typecase u is list { v = u.next; }
    |     u = v;
    |     k = k - 1;
    |   }
    |   return u
    | }
    | 
    | main = fun() {
    |   l = cons("first", cons("second", singleton("third")));
    |   h = nth(2, l);
    |   typecase h is list { print(h.value); }
    | }
    = second

Structs may be empty.

    | struct red { }
    | fun show(color: red) {
    |   print("hi")
    | }
    | main = fun() {
    |   show(make red());
    | }
    = hi

In combination with unions, this lets us create "typed enums".

    | struct red { }
    | struct green { }
    | struct blue { }
    | fun show(color: red|green|blue) {
    |   typecase color is red { print("red"); }
    |   typecase color is green { print("green"); }
    |   typecase color is blue { print("blue"); }
    | }
    | main = fun() {
    |   show(make red() as red|green|blue);
    |   show(make blue() as red|green|blue);
    | }
    = red
    = blue
