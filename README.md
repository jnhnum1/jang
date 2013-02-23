Jang
====

What is Jang? 
----

Jang is a programming language implemented in Python.  It was designed with
several key features in mind.  One of the first features is that everything in
Jang is serializable.  This makes Jang ideal for coding interactions between a
server and a client in a coroutine-like fashion.  Although Jang code cannot
currently serialize Jang objects, this would be a trivial feature to add.
However, the following is possible now:

### Sample Use-Case

#### 1. Create an initial Jang state
This can include bindings to Python (non-serializable) functions, which
constitutes a way to call Python from Jang.  This constitutes one half of the
Python/Jang foreign function interface.  These top-level bindings can
be transient - that is, they don't need to be semantically the same each time
the environment is loaded.  For example, you could include a `writeToClient`
binding to a function which takes an object, and writes it to the current
client connection.  The same Jang state might be loaded for many
different connections, but `writeToClient` would always refer to the current
connection.
   
#### 2. Call Jang functions from Python
This constitutes the other half of the Python/Jang foreign function
interface.  Together, these two capabilities make Jang usable in an existing
web server running Python.  For example, one might have the following Jang
function:

```javascript
var makeCounter = function() {
  var counter = 0;
  return function() {
    writeToClient(counter);
    counter += 1;
  }
}

var printCounter = makeCounter();
```

Then in Python, one could call `TODO`.

#### 3. Serialize the entire Jang environment
Once you have finished processing the current request from the client, you
can store that state away in a database while you handle other clients'
requests.

#### 4. Load the Jang environment
If you're going to store the state, you obviously need to be able to load it.
So the next time you get a request from your client asking to increment a
counter, you can just load up their Jang state and call `TODO` again, and the
client will auto-magically get the next value.

### Syntax
Jang's syntax is a mix of Javascript and Python, but mostly Javascript.  It
resembles Javascript in the way that variables and functions are declared.  The
`var` keyword indicates the creation of a new local binding rather than
modifying an existing binding, and anonymous functions can be easily created
with the function keyword just as in Javascript.

Some Python syntactic sugar was included - Jang lists support ranged indexing,
and boolean logic operators can be specified using the english "and", "or",
"not", or "xor".

When in doubt, unfortunately there is no better documentation on the syntax than
looking at the source in jang/lang.py.

### Semantics (TODO)
(NEW) Tail-call optimization is coming to Jang!  This will allow more
programming in a truly functional style.  It isn't only simple recursion which
is optimized, however - mutual recursion will also be optimized.

Jang, like Javascript, has first-class functions, lexical closures, and
prototypal inheritance.

Limitations
----

### Libraries
There are few libraries for Jang right now.  This is mitigated by
Jang's easy-to-use foreign function interface.  See proto_functions.py
for an example of how "native" (Python) functions can be added to Jang types.
See prelude.jang for how Jang can be extended in Jang by modifying object
prototypes.

### Serialization Format
Jang's serialization currently uses Python's pickle module.  This means that it
is not safe to deserialize a Jang state from an untrusted source.  It also means
that the serialization/deserialization process is not as efficient as it could
be.

### Performance
Jang is an interpreted language running inside an interpreted language.  It is
probably sub-optimal to do heavy lifting inside Jang.  Again, this can be
remedied by using the foreign function interface to delegate e.g. linear algebra
to NumPy, which in turn delegates to highly-optimized C.

### No exceptions
There is no reason that exceptions and exception handling can't be added to
Jang; they just haven't been added at this point because I haven't yet thought
about how they should behave.

Implementation
----

### Serializability
The requirement that everything be serializable restricted the implementation
style for large portions of Jang.  There are places where using Python's
generators or coroutines or closures would have been a natural implementation
choice, but none of those are picklable.

Instead, all of Jang's objects, and all of their fields, and so on, must be
implemented as top-level objects.

#### Transient Global Variables
The one exception to this rule is in the creation of the root environment.
Special functions may be added here which are not picklable.  See context.py for
details.

### Tail-call Optimization
Python is not a tail-call optimized language.  Therefore, to bring tail-call
optimization to Jang, we need to evaluate Jang expressions non-recursively.
