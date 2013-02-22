jang
====

* What is Jang? 

Jang is a programming language experiment implemented in Python.  It was
designed with several features in mind which constrained the implementation.
One of the first features is that everything in Jang is serializable.  Although
this serializability is not accessible from within Jang at the moment, it is
accessible from the Python interpreter.  This means that you can set up a web
REPL server in which after each request, the REPL state is stored in a database.



The first feature is that everything in Jang should be serializable
and storable in a database, including anonymous functions with closures.

The second feature is that Jang should support tail-call optimization (note,
this is not yet done but will hopefully be implemented in the coming days).

Both of these features are features which Python lacks.  Together, they enable a more functional programming style, as well as describing a sort of asynchronous client-server interaction.
