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
Tail-call optimization gives the ability to (in certain well-defined and easily
recognizable circumstances) make recursive calls to functions without consuming
any additional space, either on the stack or on the heap.

The most natural way to evaluate a syntax tree is recursively.  This uses the
host language's stack to store both a stack of expressions and their respective
internal evaluation states.  If the host language is tail-call optimized, it is
typically easy to transfer this optimization to the interpreted language.  

Unfortunately, Python is not a tail-call optimized language.  Therefore, to
bring tail-call optimization to Jang, we need to evaluate Jang expressions
non-recursively. This section addresses the question of how we can (nicely)
implement tail-call optimization for Jang.

Not all calls are tail calls, so we will still need to maintain a stack.  The things we push onto the stack will be partially executed functions or partially evaluated expressions.  They will require the result of a function or expression further down on the stack before their execution/evaluation can be resumed.

As a simple example of what kind of state needs to be stored, consider the
expression `foo() + bar()`.  You start with an addition expression on the stack,
with neither of its arguments evaluated so far.  Now the function call `foo()`
is pushed onto the stack, and it gives some result.  Our evaluator passes this
result to the addition expression, which stores it, and the expression then
requests `bar()` to be evaluated.  So `bar()` is pushed onto the stack, its
result is passed to the addition expression, and then the addition expression's
result is passed to whatever was higher up on the stack.

Now, if a function or expression requests a tail-call, our evaluator can simply
replace that function/expression on the stack with the requested expression.
This is how tail-call optimization works in Jang.

The core of this scheme is the representation of in-progress, currently
evaluating/executing expressions.  Python has coroutines, which are a nice way
of writing functions which need to wait for extra input and produce multiple
outputs, and it would nice to implement our partial expressions this way.  It
would look something like this:

```python
def addExpr(expr1, expr2):
  val1 = yield ("eval", expr1)
  val2 = yield("eval", expr2)
  yield("result", val+val2)
```

However, coroutines are not serializable, which means they are not a viable
choice if we ever want to add a coroutine-like `getUserInput()` function to
Jang, or if we want Jang-internal coroutines.

A coroutine is implicitly storing the position of its execution so far (i.e.
which arguments, if any, have already been evaluated), so to make a serializable
version of a coroutine we need to make that state explicit.  We thus make
`AddExpr` into a class, and arrange that `AddExpr.eval()` will be called
multiple times, returning a message to the evaluator each time.  The example
below shows the "eval" message, which asks the evaluator to evaluate an
expression and pass the result to `Eval()` on the next call.  You can also see
the "result" message, which is what `Eval()` returns when it is has a final
result.

```python
class AddExpr:
  def __init__(self, expr1, expr2):
    self.expr1 = self.expr2
    self.expr2 = self.expr2
    self.state = 0
  
  def Eval(self, env, subValue=None):
    self.state += 1
    if self.state == 1:
      return ("eval", env, self.expr1)
    elif self.state == 2:
      self.val1 = subValue
      return ("eval", env, self.expr2)
    else:
      self.val2 = subValue
      return ("result", self.val1 + self.val2)
```
      
 
The evaluator needs to (using O(1) Python stack space) run expressions' `Eval()`
methods.  Their return values "request" the evaluator to perform certain
actions.  For normal stackful recursion, they can request that the evaluator
evaluate another expression.  The key is that they can also request that the
evaluator perform a tail-call on an expression.  If expression X returns
("tailcall", Y), it means that the final value of X is whatever the final value
of Y is.  

One thing we need to consider is that return statements are special in that they
can cause multiple expressions to be popped from the stack, as in if we have the
following:

```javascript
var getParity = function(x) {
  if (x % 2 == 0) {
    return "even"
  }
  if (x % 2 == 1) {
    return "odd"
  }
}
```

If x is even, then the first `if` statement is pushed onto the stack.  It is not
a tail-call because it is not the last statement of the function.  Then `return
"even"` pops both the if statement AND the function call from the stack.  For
return to work properly, it must know where the top of its stack frame is.  The
top of its stack frame is the index of the last function call.  Fortunately, any
tail calls that happen after the function is called do not affect this index.  
