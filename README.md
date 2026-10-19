# Char

> Char is a simple functional language that does functional things

## Functions
Functions are declared using the `fun` keyword and follow this syntax:
```
fun {function name} {arguments} => {function body}
```

## When expressions
In Char there is a special expression called the `when` expression that allows you to check for one or more condition into one single expression:
```
when {condition} | |{condition) | _ => {expression}
```

## I/O

`print {expression}` is oused for outputting content to the screen
`input {optional prompt}` is used for taking user input
`import {file name}` will import a file content into another

## Comments

Comments start with `#`

## Block expressions

Blocks are defined with curly braces (`{}`) and they evaluate expressions from top to bottom and return the last expression written in them

## Lists

Lists are defined like this:
`[a_1, a_2, ..., a_n]`

you can get the length of a list using `len`
