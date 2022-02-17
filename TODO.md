TODO
----

### Implementation ###

call equal_tagged_value() when you find a union type when
comparing structs deeply.  (C backend, probably others)

There appears to be a bug with casting a union type to
itself?  The tag in the tagged value is the union?

Name mangling for compilers (prepend with `_` most likely.)

And literal characters in strings, especially `'` and `"`.

Figure out a way to do `input`, `read`, and `write` with node.js backend.

Implement `int`, `chr`, `ord` for Ruby, JavaScript, stackmac, C.

Better indentation in the JavaScript backend.

TaggedValue -> just a tuple.

stackmac: store tagged values as two values on the stack.
and void types in unions of (void, X) should only be one value.
(structs are still boxed though)

AST nodes should have source line numbers, it would be really nice.

Implement garbage collection of some sort in the C backend.  Either that
or implement some kind of resource-awareness in the language itself.

Other backends (Python? Java? CIL? Scheme?)

### Design ###

Don't output final value.  Command-line arguments passed to `main`.  (`sysmain`?)

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

### Object Orientation ###

Castile will likely not have any "real" object-oriented features.  Probably,
only nominal subtyping, with a Lua-like method call operator.  Meaning
something like this:

    struct counter {
      value: integer;
      bump: counter, integer -> counter
    }
    
    struct named_counter < counter {
      name: string;
    }

    forward bump: counter, integer -> counter

    bump = fun(c: counter, v: integer) {
      return make counter(value=c.value + v, bump=bump;
    }

    new_counter = fun(init) {
      return make counter(value=init, bump=bump);
    }

    new_named_counter = fun(init) {
      g = make named_counter(value=init, bump=bump, name="Jeremy");
      return g:bump(5);
    }

`bump` can operate on a `named_counter` type, but only because it
is declared to be a subtype of `counter`, so its fields are known to be
a superset of `counter`'s fields.  The `bump` method itself is not defined
within either structure, and the `:` syntax is used to pass the object as
the first argument.

### Memory Management ###

Some notes on memory management.

Some properties of Castile have some potential for simplifying memory
management.  For example, structures are immutable.  I do not expect to
be able to get away with avoiding garbage collection completely, but I
suspect there to be ways to tie reference counting to execution in a
"nice" fashion.  Although this will likely still be difficult.

I'd like Castile's memory allocation system to be based on the following
idea:

Every time you call a function of type `A -> B`, you have created an
object of type `B`.

If, in some function, your argument `a` to the call of the function of type
`A -> B` was your last use of `a`, you have destroyed an object of type `a`.
(Unless objects of type `B` contain objects of type `A`.)

If you call a function of type `A -> A`, you haven't created or destroyed
any objects.  (Even if you discard the argument and allocate a new `A` to
be returned, you can just "allocate" the new `A` over the old one.)

I don't know enough about linear types to know how well that can be
expressed with them.

Suppose you are `f`, a function `A -> B`, and `B` contains `A`.  You
actually ignore the `A` given to you, and call another function `g` to
allocate a new `B` containing the new `A`.

It would seem that the caller of `f` must pass "this is the last use of
the argument" to you, and that you must pass "it's ok to overwrite
my `A` with your new `A`" to `g`.  This is complicated enough communication
that it would probably be best modelled as a global dictionary of some sort,
rather than each function telling each other function what's up.  For
example, at the point of the last use of the `A` just before calling `f`, the
address of that `A` could be placed on a list of "newly available `A`s."
