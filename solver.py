import sys
import re

V_TRUE = 't'
V_FALSE = 'f'
V_ARBITRARY = 'a'

T_VAR = 'variable'
T_NEG = 'negation'
T_CONJUNCTION = 'conjunction'
T_DISJUNCTION = 'disjunction'

def ValueNegate(val):
    lookup = {
            V_ARBITRARY: V_ARBITRARY,
            V_TRUE: V_FALSE,
            V_FALSE: V_TRUE
            }
    return lookup.get(val)

class Solution:
    """
    ADT of the solution. Encoded as a string consisting:
        a arbitrary
        t true
        f false
    """

    def __init__(self, varList, assignments=''):
        self.varList = varList
        if (len(assignments) == len(varList)):
            self.assignments = list(assignments)
        else: # set every assignement to arbitary
            self.assignments = [V_ARBITRARY \
                    for i in range(len(varList))]

    def setVar(self, var, value):
        """
        Assigns value to a variable.
        Returns True if assign succeeds. Otherwise returns False.
        """
        try:
            index = self.varList.index(var)
            self.assignments[index] = value
        except ValueError:
            return False
        return True

    def getVar(self, var):
        value = None
        try:
            index = self.varList.index(var)
            value = self.assignments[index]
        except ValueError:
            pass
        return value

    def contradictsWith(self, another):
        """
        Tests wether the solution is contradicts with another.
        """
        for i, val in enumerate(self.assignments):
            if val != V_ARBITRARY \
                    and another.assignments[i] == ValueNegate(val):
                return True
        return False

    def combine(self, another):
        """
        Returns the combinations two solution.
        Use the current solution as the primary source. Copy assignment
        from another only for variables that are set to V_ARBITRARY.
        """
        assignments = ''
        for i, val in enumerate(self.assignments):
            if (val == V_ARBITRARY):
                assignments += another.assignments[i]
            else:
                assignments += val
        return Solution(self.varList, assignments)

    def __eq__(self, another):
        """ Makes it possible to use set operation on this type. """
        return isinstance(another, Solution) \
                and str(self) == str(another)

    def __hash__(self):
        """ Makes it possible to use set operation on this type. """
        return hash(str(self))

    def __str__(self):
        return ''.join(self.assignments)

def normalizePartial(node, positive=True):
    partial = node.toDNF(positive)
    return partial.nodeType == T_DISJUNCTION and partial.childNodes or [partial]

class ASTNode:
    """A valid ASTNode contains anything but those of the same type."""

    def __init__(self, tokenPosition):
        self.tokenPosition = tokenPosition
        self.childNodes = []

    def output(self, padding=0):
        lspace = '  ' * padding
        return "%s%s:%d\n%s" % (lspace, self.nodeType, \
                self.tokenPosition, self.outputChildren(padding))

    def outputChildren(self, padding=0):
        return '\n'.join(map(lambda c: c.output(padding + 1), \
                 self.childNodes))

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, another):
        return isinstance(another, ASTNode) \
                and another.nodeType == self.nodeType \
                and str(self) == str(another)

    def __str__(self):
        raise NotImplementedError

    def simplify(self):
        raise NotImplementedError

    def solve(self, varList, positive=True):
        """Returns all assignments that makes the node true."""
        raise NotImplementedError

    def toDNF(self, positive=True):
        raise NotImplementedError

    def toCNF(self, positive=True):
        raise NotImplementedError

class _Var(ASTNode):
    """A valid _Var contains only a lowercased character."""

    def __init__(self, tokenPosition, var):
        ASTNode.__init__(self, tokenPosition)
        self.nodeType = T_VAR
        self.var = var

    def outputChildren(self, padding):
        lspace = '  ' * padding
        return "%s%s" % (lspace, self.var)

    def simplify(self):
        return self

    def solve(self, varList, positive=True):
        solution = Solution(varList)
        solution.setVar(self.var, positive and V_TRUE or V_FALSE)
        return [solution]

    def toDNF(self, positive=True):
        # 'a' is in DNF
        return self

    def toCNF(self, positive=True):
        # 'a' is in CNF
        return self

    def __str__(self):
        return self.var

class _Neg(ASTNode):
    """A valid _Neg contains a _Var, _CForm or _DForm as one being negated."""

    def __init__(self, tokenPosition, negated):
        """negated can be _Var, _CForm or _DForm and double negation is not allowed."""
        ASTNode.__init__(self, tokenPosition)
        self.nodeType = T_NEG
        self.negated = negated

    def outputChildren(self, padding):
        return self.negated.output(padding + 1)

    def simplify(self):
        return self

    def solve(self, varList, positive=True):
        return self.negated.solve(varList, not positive)

    def toDNF(self, positive=True):
        if self.negated.nodeType == T_VAR:
            # `!a' is in DNF
            return self
        elif self.negated.nodeType == T_NEG:
            # `!!F = F'
            return self.negated.negated.toDNF()
        else:
            # appy De Morgan's Law
            if positive:
                if self.negated.nodeType == T_CONJUNCTION:
                    # `!(a&b) => !a+!b'
                    return _DForm(self.tokenPosition, \
                            map(lambda c: _Neg(c.tokenPosition, c).toDNF(True), \
                            self.negated.childNodes)).toDNF(True)
                elif self.negated.nodeType == T_DISJUNCTION:
                    # `!(a+b) => !a&!b'
                    return _CForm(self.tokenPosition, \
                            map(lambda c: _Neg(c.tokenPosition, c).toDNF(True), \
                            self.negated.childNodes)).toDNF(True)
                elif self.negated.nodeType == T_NEG:
                    return self.negated.toDNF(True)
            else:
                # optimization: !!F = F
                return self.negated

    def toCNF(self, positive=True):
        if self.negated.nodeType == T_VAR:
            # `!a' is in CNF
            return self
        elif self.negated.nodeType == T_NEG:
            # `!!F = F'
            return self.negated.negated.toCNF()
        else:
            # appy De Morgan's Law
            if positive:
                if self.negated.nodeType == T_CONJUNCTION:
                    # `!(a&b) => !a+!b'
                    return _DForm(self.tokenPosition, \
                            map(lambda c: _Neg(c.tokenPosition, c).toCNF(True), \
                            self.negated.childNodes)).toCNF(True)
                elif self.negated.nodeType == T_DISJUNCTION:
                    # `!(a+b) => !a&!b'
                    return _CForm(self.tokenPosition, \
                            map(lambda c: _Neg(c.tokenPosition, c).toCNF(True), \
                            self.negated.childNodes)).toCNF(True)
                elif self.negated.nodeType == T_NEG:
                    return self.negated.toCNF(True)
            else:
                # optimization: !!F = F
                return self.negated

    def __str__(self):
        return '!' + (self.negated.nodeType == T_DISJUNCTION \
                and "%s%s%s" %('(', str(self.negated),')') or str(self.negated))

class _DForm(ASTNode):
    """A valid _DForm contains severl _CForm, _Var and _Neg as its child nodes"""

    def __init__(self, tokenPosition, nodes):
        ASTNode.__init__(self, tokenPosition)
        self.nodeType = T_DISJUNCTION
        for nd in nodes:
            if nd.nodeType == T_DISJUNCTION:
                self.childNodes += nd.childNodes
            else:
                self.childNodes.append(nd)

    def simplify(self):
        return self

    def solve(self, varList, positive=True):
        """The DForm is true if any expression is true."""
        solutions = []
        for nd in self.childNodes:
            solutions += nd.solve(varList, positive)
        return set(solutions)

    def toDNF(self, positive=True):
        # a DF is normal if every operand is in DNF
        self.childNodes = list(set([c.toDNF(positive) for c in self.childNodes]))
        return self

    def toCNF(self, positive=True):
        normalized = True
        for nd in self.childNodes:
            if nd.nodeType == T_VAR:
                pass
            elif nd.nodeType == T_NEG and nd.negated.nodeType == T_VAR:
                pass
            else:
                normalized = False
                break
        if normalized:
            return self
        dnf = _Neg(self.tokenPosition, self).toDNF(positive)
        return _Neg(self.tokenPosition, dnf).toCNF(positive)

    def __str__(self):
        return '+'.join(map(str, self.childNodes))

class _CForm(ASTNode):
    """A valid _CForm contains severl _DForm, _Var and _Neg as child nodes."""

    def __init__(self, tokenPosition, nodes):
        ASTNode.__init__(self, tokenPosition)
        self.nodeType = T_CONJUNCTION
        for nd in nodes:
            if nd.nodeType == T_CONJUNCTION:
                self.childNodes += nd.childNodes
            else:
                self.childNodes.append(nd)

    def simplify(self):
        return self

    def solve(self, varList, positive=True):
        """The CForm is true if and only if every expression is true."""
        solutions = self.childNodes[0].solve(varList, positive)
        # a well-formed CForm has more than 1 child nodes
        for nd in self.childNodes[1:]:
            solutions = [si.combine(sj) for si in solutions \
                    for sj in nd.solve(varList, positive) \
                    if not si.contradictsWith(sj)]
        return set(solutions)

    def toDNF(self, positive=True):
        dnf = normalizePartial(self.childNodes[0], positive)
        for nd in self.childNodes[1:]:
            dnf2 = normalizePartial(nd)
            interm = []
            for right in dnf2:
                for left in dnf:
                    # the types of left and right are in {T_VAR, T_NEG, T_CONJUNCTION}
                    lp = left.nodeType == T_CONJUNCTION and left.childNodes or [left]
                    rp = right.nodeType == T_DISJUNCTION and right.childNodes or [right]
                    skipAtom = False
                    skipConjunction = False
                    incr = [] # chars necessary to add
                    # if the right appears in the left, ignore the right
                    # if the right contradicts with the left, ignore both
                    for rc in rp:
                        for lc in lp:
                            if lc.nodeType == T_VAR:
                                if rc.nodeType == T_VAR and rc == lc:
                                    skipAtom = True
                                    pass
                                elif rc.nodeType == T_NEG and rc.negated == lc:
                                    skipConjunction = True
                                    break
                            elif lc.nodeType == T_NEG:
                                if rc.nodeType == T_VAR and lc.negated == rc:
                                    skipConjunction = True
                                    break
                                elif rc.nodeType == T_NEG and lc.negated == rc.negated:
                                    skipAtom = True
                                    break
                        if skipAtom:
                            skipAtom = False
                            continue
                        if skipConjunction:
                            break
                        incr.append(rc) # then it's safe to conjunct left with this node
                    if skipConjunction:
                        continue
                    interm.append(left if len(incr) == 0 else \
                            _CForm(self.tokenPosition, sorted(lp + incr, key= \
                            lambda n: str(n) if n.nodeType == T_VAR else str(n.negated))))
            dnf = interm
        return len(dnf) > 1 and _DForm(self.tokenPosition, dnf).toDNF() or dnf[0]

    def toCNF(self, positive=True):
        # a CF is normal if every operand is in CNF
        self.childNodes = list(set([c.toCNF(positive) for c in self.childNodes]))
        return self

    def __str__(self):
        return '&'.join(map(lambda c: c.nodeType == T_DISJUNCTION \
                and "%s%s%s" % ('(', str(c), ')') or str(c), self.childNodes))

def pushNode(node, nodeStack, symbolStack):
    """Push a node back into the stack and do combination if there is
    matching operation symbols.
    A matching symbol is one imediately left to the the node. For example,
    `a&b&!c' The matching symbol for b is the first ampersand, while that
    for c is the bang.
    Such combination is continuous. For example, after
    combining c with the bang, creating a negation node, the negation node
    can be combined with the amperson immediately left to it."""
    while len(symbolStack) > 0 and \
            symbolStack[-1][1] == node.tokenPosition - 1:
        (symbol, symbolPosition) = symbolStack.pop()
        if (symbol == '&'):
            previousNode = nodeStack.pop()
            node = _CForm(previousNode.tokenPosition, \
                    [previousNode, node])
        elif(symbol == '!'):
            if node.nodeType == T_NEG:
                # double negation is unecessary, just like initializing
                # a _CForm with single node, update the position instead
                node = node.negated
                node.tokenPosition = symbolPosition
            else:
                node = _Neg(symbolPosition, node)
    nodeStack.append(node)

def parse(formula):
    """Parse the boolean formula represented as string into an AST"""
    nodeStack = []
    bracketStack = []
    symbolStack = []
    for nextPosition, nextToken in enumerate(formula):
        if nextToken == '(':
            # record the where the content starts, as well as where the '('
            # locates inside the original formula
            bracketStack.append((len(nodeStack), nextPosition))
        elif nextToken == ')':
            # find where the matching '(' starts and what follow it
            (nodePosition, bracketPosition) = bracketStack.pop()
            # fetch content after the matching '(' and create a DForm node
            bracketedNodes = nodeStack[nodePosition:]
            nodeStack = nodeStack[:nodePosition]
            if len(bracketedNodes) > 1:
                dFormNode = _DForm(bracketPosition, bracketedNodes)
                pushNode(dFormNode, nodeStack, symbolStack)
            else:
                # a DForm node with only 1 child node is unnecessary
                # so we push the content instead, with new position
                bracketedNodes[0].tokenPosition = bracketPosition
                pushNode(bracketedNodes[0], nodeStack, symbolStack)
        elif nextToken == '&'or nextToken == '!':
            symbolStack.append((nextToken, nextPosition))
        elif nextToken == '+':
            # there is no need to parse CForm explicitly becase it is
            # either a single or a list of var(s), negation(s), DForm(s)
            pass
        else:
            # for a token in any valid formula, it must be [a-z]
            varNode = _Var(nextPosition, nextToken)
            pushNode(varNode, nodeStack, symbolStack)
    # by the end the node stack has either one single node or multiple
    # nodes those multiple nodes can be seen as braketed as a whole
    if (len(nodeStack) > 1):
        # -1 means the left bracket is inserted on purpose
        return _DForm(-1, nodeStack)
    else:
        return nodeStack[-1]

if __name__ == '__main__':
    pass
