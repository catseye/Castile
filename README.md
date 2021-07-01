Castile
=======

Version 0.4 | _Entry_ [@ catseye.tc](https://catseye.tc/node/Castile)
| _See also:_ [Eightebed](https://github.com/catseye/Eightebed#readme)
∘ [Dieter](https://github.com/catseye/Dieter#readme)

- - - -

This is the reference distribution for **Castile**, a simple imperative
language with union types.

The design of Castile was influenced (in varying degrees) by C, Rust,
Eightebed, Python, Ruby, and Erlang.  More information on its roots can
be found in [doc/Design.md](doc/Design.md).

The reference implementation can both interpret Castile programs and
compile them to a variety of targets — JavaScript, Ruby, C, and a generic
stack-based VM (included in this distribution).

A rich test suite in [Falderal][] format, which describes the language
with many examples, can be found in [tests/Castile.md](tests/Castile.md).

Quick Start
-----------

Clone this repository, `cd` into the repo directory and run

    bin/castile eg/hello.castile

Alternately, put the `bin` subdirectory on your executable search path, so
that you can run `castile` from any directory on your system.  `castile`
has no dependencies besides Python (either Python 2 or Python 3.)

Motivating Example
------------------

Here are some functions for creating linked lists, written in Castile:

    struct list {
      value: integer;
      next: list|void;
    }

    fun empty() {
      return null as list|void
    }

    fun cons(v: integer, l: list|void) {
      make list(value:v, next:l) as list|void
    }

In this, `list|void` is a union type, which is the moral equivalent of
saying that the value is "nullable".  In order to access any of the
concrete types of the union, one must use `typecase`:

    fun max(l: list|void) {
      u = l;
      v = u;
      n = 0;
      while true {
        typecase u is void {
          break;
        }
        typecase u is list {
          if u.value > n {
            n = u.value
          }
          v = u.next;
        }
        u = v;
      }
      return n
    }

This retains type-safety; the code will never unexpectedly be presented
with a null value.

Union types can also encourage the programmer follow a [Parse, don't validate][]
approach (which, despite the impression you might get from reading that article,
is not restricted to Haskell or even to functional programming).  In the above
code, `cons` will never return a `void`, and `max` is not defined on empty lists.
So ideally, we'd like to tighten their types to exclude those.  And we can:

    ...

    fun cons(v: integer, l: list) {
      make list(value:v, next:l as list|void)
    }

    fun singleton(v: integer) {
      make list(value:v, next:null as list|void)
    }

    fun max(l: list) {
      u = l as list|void;
      v = u;
      ...
    }

Many more examples of Castile programs can be found in
[tests/Castile.md](tests/Castile.md).

[Falderal]: https://catseye.tc/node/Falderal
[Parse, don't validate]: https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/
