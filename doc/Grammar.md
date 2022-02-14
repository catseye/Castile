Grammar of Castile
==================

This is an EBNF grammar for Castile.

    Program ::= {Defn [";"]}.
    Defn    ::= "fun" ident "(" [Arg {"," Arg}] ")" Body
              | "struct" ident "{" {ident ":" TExpr [";"]} "}" ["for" "(" [ident {"," ident}] ")"]
              | ident (":" TExpr0 | "=" Literal).
    Arg     ::= ident [":" TExpr1].
    Body    ::= "{" {Stmt [";"]} "}".
    Stmt    ::= "while" Expr0 Block
              | "typecase" ident "is" TExpr0 Block
              | "do" Expr0
              | "return" Expr0
              | If
              | Expr0.
    Block   ::= "{" {Stmt [";"]} "}".
    If      ::= "if" Expr0 Block ["else" (Block | If)].
    Expr0   ::= Expr1 {("and" | "or") Expr1} ["as" TExpr0].
    Expr1   ::= Expr2 {(">" | ">=" | "<" | "<=" | "==" | "!=") Expr2}.
    Expr2   ::= Expr3 {("+" | "-") Expr3}.
    Expr3   ::= Expr4 {("*" | "/") Expr4}.
    Expr4   ::= Expr5 {"(" [Expr0 {"," Expr0}] ")" | "." ident}.
    Expr5   ::= "make" ident "(" [ident ":" Expr0 {"," ident ":" Expr0}] ")"
              | "(" Expr0 ")"
              | "not" Expr1
              | Literal
              | ident ["=" Expr0].
    Literal ::= strlit
              | ["-"] intlit
              | "true" | "false" | "null"
              | "fun" "(" [Arg {"," Arg}] ")" Body.
    TExpr0  ::= TExpr1 [{"," TExpr1} "->" TExpr1].
    TExpr1  ::= TExpr2 {"|" TExpr2}.
    TExpr2  ::= "integer"
              | "boolean"
              | "void"
              | "(" TExpr0 ")"
              | ident.
