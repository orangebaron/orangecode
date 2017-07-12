# Orange_Code

*A high-level, object-oriented language that runs on just about any platform with a python interpreter.*

## Getting Started

To download, copy the orange_code folder to your python's Lib library. You can then use the terminal and runner versions (found in the terminal and runner folders) to run orange_code by running their respective .py files.

## Overview

Orange_code is a programming language where most traditional programming structures have been turned into classes. Methods are represented as classes; primitive datatypes are represented as classes, which means that strings or numbers can be given their own state variables; and tables, if statements, while loops, and for loops, are all represented as classes.
Another goal of orange_code is to make everything as editable as possible. Basic functions of primitive variables (e.g. and, plus, etc.) can be modified; method code can be changed after the creation of the method; and the method to get a certain variable can be modified.

## DOCUMENTATION TIME
aka when this readme stops being tryhard

# How Thingies Work
A line of orange_code is a bunch of object paths, literals, and ()/[]/{}-enclosed code separated by operators. For example, in a.b.c.x+"abc"/('this'+is+code), a.b.c.x is an object path, "abc" is a string literal, and ('this'+is+code) is code enclosed with parentheses. The operators in this example are + and /
# Order of Operations
Orange_code breaks up a line according to the order of operations. For example, since ~ has higher priority in the order of operations than /, and / higher than +, 1~2+3/4 is the same as 1~((2+3)/4). The full order of operations is (from highest to lowest priority): '=', '~', '===', '~==', '**==', '//==', '*==', '/==', '%==', '+==', '-==', '&==', '|==', '!&==', '!|==', '>==', '<==', '!==', '==', '~=', '**=', '//=', '*=', '/=', '%=', '+=', '-=', '&=', '|=', '!&=', '!|=', '>=', '<=', '!=', '**', '//', '*', '/', '%', '+', '-', '&', '|', '!&', '!|', '>', '<', '`#', '`.', '!'
