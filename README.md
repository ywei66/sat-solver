sat-solver
==========

A naïve SAT solver written in Python for practice purpose. Specification can be found on the programming question of the 2013 Feb's entrance exam to Tokyo University's CS master program.

By the time of writing, I was new to Python. So it's not very _Pythonic_, for example, it contains _Camel Case_ in method names. It is more about solving problems any way.

Update History:

###2013/12/15

* README.md
* solver.py
* test.py

Several textual editing on `README.md`. Renamed the two python file.

###2013/06/12

* extendedFormula.py

When I was about to write a memo about this project, I did a little research on CNF in Wikipedia, and found some sample formula. Then I stopped to test my code with them, because I hadn't tested it thoroughly. To my disappointment, I found errors:

    !(b+c)  => !c&!b # correct
    (a&b)+c => (!a+!c)&(!b+!c) # incorrect, should be (a+c)&(b+c)
    a&(b+(d&e)) => a&(!b+!d)&(!b+!e) # incorrect, should be a&(b+d)&(b+e)

Since the algorithm does double negation, and the error is that a variable is incorrectly negated, I doubt the CNF conversion on negation isn't expand with De Morgains law correctly (the first one doesn't need such expansion because of an optimization based on the fact that !!F = F).

Some debug outputs suggests that double negations weren't converted correctly (there are no double negations in Simple Form; they are produced by expanding with De Morgan's law -- expanded by _Neg's CNF method which calls it self recursively such that the double negations, as intermediate values, is held within the expansion).

Reading the code, I found _Neg's CNF method relies on argument `positive' to detect double negation (when positive=False) without producing a _Neg instance that has another _Neg instance as its `negated' attribute. However, the argument is never set to False (because the De Morgan expansion produces _Neg with _Neg). So I changed a few lines, and made it correct.

###2012/06/11

+ extendedFormula.py
+ extendedFormula_driver.py

Now I have solutions to all 6 questions. Break-throughs include:

1) parse a valid boolean formula with variables, !, & and +. This is based on the parsing alorithm I found yesterday, but made powerful by the following important insights (in response to yesterday's puzzles):
	a) if there are only +, we don't need to create any disjunction node. This applies to the creation of conjunction nodes when there are only &.
	b) when there are both + and &, we need to create conjunction nodes only.
	c) & and ! are both right-associative, so can be put into the same stack.
	d) a bracketed area can be seen as a single variable. It can be the operand of any symbol if and only if the left bracket follows that symbol IMMEDIATELY.

2) with a little tweak on the parser, the result AST is in a form that satisfies:
	a) Elements of a conjunction do not include any conjunctions;
	b) Elements of a disjunction do not include any disjunctions;
	c) The formula being negated is not a negation itself.

3) conversion into DNF is done recursively:
	a) a variable is in DNF by itself;
	b) a negation is in DNF if it negates a variable, or we can apply De Morgan's law, expand, and convert recursively;
	c) a disjunction is in DNF if all elements are in DNF, so we just need to convert each element recursively;
	d) a conjunction is in DNF if each element is either a var or a negated var, but this is no ofthen the case; so I convert each element into DNF recursively, then expand the conjunction into a disjunction and then normalize that disjunction.

4) conversion into CNF is done recursively; the solution is to apply double negation and reduce into DNF:
	a) a variable is in CNF by itself;
	b) a negation is in CNF if it negates a variable, or we can appy De Morgen's law, expand, and convert recursively;
	c) a conjunction is in CNF if each element is in CNF, so we need to convert each one recursively;
	d) a disjunction is in CNF if each element is either a var or negated var, but again this is ofthen not the case; my approach is to do double negation, recursively convert the inner negation into DNF then recursively convert the outter negation into CNF (because by De Morgan's law, the negation of a dijunction is a conjuction with each part negated).


###2012/06/10

+ solver.py

To deal with brackets, I wrote a parsing function. It uses one stack for tokens and another stack to store the position of each unclosed left bracket. Because the matching property of brackets implies an LIFO process: the most recently seen left bracket gets matched first.

"The position (index) of each unclosed left bracket" is practicaly the size of the token stack at the time of a left bracket as the next token, by the way.

To parse operators, just put each symbol into a stack, and create an AST node with the next token and the token on top of the token stack, whenever the operator stack isn't empty. The result looks fine for purely disjunctions and negations: (a+(b+(c+d))), and !(!(!a)). But when there are conjunctions, precedence is ignored, for example: a&b+c turns into a&(b+c).

I was just too tired to come up with any idea though.

###2012/06/10

+ booleanFormula.py

I solved the previous 3 questions in "KISS" manner. But it is too simple such that I cannot extended it to solve the 4th problem -- I have to introduce a new algorithm (parsing).

A highlight of this solution is that my algorithm of finding assignments that satisfy the formula:

1) I don't do brutal-force search, a.k.a. generate 2^n different assignments and test each one (n = # of variables)

2) rather, I do it based on the rule that:
	a) a conjunction is true if and only if all elements are true;
	b) a disjunction is true if any element is true.

3) so I do it top-down, generatively. 
	a) for a disjunction or conjunction, find the solutions for each operand, and combine them, while the combination rules are different. In set analogy, treat the solutions to each operand as a set:
	b) then the solutions to a disjunction is simply the union while
	c) those to a conjunction is an "intersection" -- cartesian product is used to find the "intersection" of two solution sets and the product of two solutions is either nothing (when an assignment cannot satisfy another formula) or as {arbitary, true} x {true, true} = {true, true}.
	b) for a variable, the solution is to set that variable to true.
	c) For a negation, the solution is to negate the solution to what it negates.

4) I introduced a special value - arbitray, in addition to true and false. It means that the variable can be either true or false, while the formula remains true. For example, a + b&c, where b and c are both true, a can be either true or false.

5) the problem statement does not specify how the assignements look like, but if it wants true or false only, I just need to add an extra generative layer on top of "arbitary". For example, {a, true, true} gets converted into {true, true, true} and {false, true, true}.
