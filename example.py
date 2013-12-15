from solver import parse, ASTNode
import re

def test_parse():
    testFormulae = [
            'a+b',
            'a+b+c',
            'a&b',
            'a&b&c',
            'a&b+c',
            'a+b&c',
            'a+(b+c)',
            '(a+b)+c',
            'a&(b&c)',
            '(a&b)&c',
            'a+(b&c)',
            'a&(b+c)',
            '(a+b)&c',
            '(a&b)+c',
            'a&b+b&c+a&b&c',
            '(a&b)&(b&c)&(a&b&c)',
            '(a+b)&(b+c)&(a+b+c)',
            '!a',
            '!a+b',
            '!a&b',
            'a+!b',
            'a&!b',
            '!a&b+b&c+a&b&c',
            'a+!(b&!(a&!c))',
            '!!a',
            '!(!a)',
            '!(!(a+b)&!(a&c))',
            'b&!!a',
            'b&(!!(a))'
            ]
    for formula in testFormulae:
        ast = parse(formula)
        print "%s => %s" % (formula, str(ast))
        print '---'
        print ast.output()
        print '==='

def test_solve():
    testFormulae = [
            'a',
            '!a',
            'a+b',
            'a+b+c',
            'a&b',
            'a&b&c',
            'a&b+c',
            'a+b&c',
            'a+(b+c)',
            '(a+b)+c',
            'a&(b&c)',
            '(a&b)&c',
            'a+(b&c)',
            'a&(b+c)',
            '(a+b)&c',
            '(a&b)+c',
            'a&b+b&c+a&b&c',
            '(a&b)&(b&c)&(a&b&c)',
            '(a+b)&(b+c)&(a+b+c)',
            '!a+b',
            '!a&b',
            'a+!b',
            'a&!b',
            '!a&b+b&c+a&b&c',
            'a+!(b&!(a&!c))',
            '!!a',
            '!(!a)',
            '!(!(a+b)&!(a&c))',
            'b&!!a',
            'b&(!!(a))'
            ]
    for formula in testFormulae:
        print "solution(s) to %s:" % formula
        ast = parse(formula)
        varList = ''.join(sorted(set(re.findall('[a-z]', formula))))
        solutions = ast.solve(varList)
        if len(solutions) > 0:
            thickBorder = '=' * (len(varList) * 2 - 1)
            thinBorder = '-' * (len(varList) * 2 - 1)
            print thickBorder
            print '|'.join(list(varList))
            print thinBorder
            print '\n'.join(map(lambda s: '|'.join(list(str(s))), \
                solutions))
            print thinBorder
        else:
            print 'None'
        print ''
    pass

def test_dnf():
    testFormulae = [
            'a',
            '!a',
            'a+b',
            'a&b',
            'a&b&c',
            'a&b+c',
            'a&(b+c)',
            'a&!b',
            '!(a+b)',
            '!(a&b)',
            '!(a+b&c)',
            '(a+b)&(b+c)',
            '(!a+b)&(a+b)',
            '(!a+b+c)&(a+!b+c)',
            '(!a+b+c)&(a+!b+c)&(a+b+!c)'
            ]
    for formula in testFormulae:
        ast = parse(formula)
        print "%s => %s => %s" % (formula, str(ast), str(ast.toDNF()))
        # print ast.output()

def test_cnf():
    testFormulae = [
            'a',
            '!a',
            'a+b',
            'a+!b',
            'a&b',
            '!a&b',
            'a+b&c',
            'a+!a&b+!a&c',
            '!a&(b+c)',
            '(a+b)&(!b+c+!d)&(d+!e)',
            'a+b',
            'a&b',
            '!(b+c)',
            '(a&b)+c',
            'a&(b+(d&e))'
            ]
    for formula in testFormulae:
        ast = parse(formula)
        print "%s => %s => %s" % (formula, str(ast), str(ast.toCNF()))

if __name__ == '__main__':
    test_parse()
    test_solve()
    test_dnf()
    test_cnf()
