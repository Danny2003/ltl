def transform(formula):
    """
    transform the formula into a form that only includes
    'and', 'not', 'next', and 'until' operators
    """
    if formula[0] == 'or':
        return ('not', ('and', ('not', transform(formula[1])), ('not', transform(formula[2]))))
    elif formula[0] == 'implies':
        return ('not', ('and', transform(formula[1]), ('not', transform(formula[2]))))
    elif formula[0] == 'eventually':
        return ('until', ('atom', 'true'), transform(formula[1]))
    elif formula[0] == 'always':
        return ('not', ('until', ('atom', 'true'), ('not', transform(formula[1]))))
    elif formula[0] == 'not':
        return ('not', transform(formula[1]))
    elif formula[0] == 'and':
        return ('and', transform(formula[1]), transform(formula[2]))
    elif formula[0] == 'until':
        return ('until', transform(formula[1]), transform(formula[2]))
    elif formula[0] == 'next':
        return ('next', transform(formula[1]))
    elif formula[0] == 'atom':
        return formula

def eliminate_double_not(formula):
    """
    eliminate double negation in the formula
    """
    if formula[0] == 'and':
        return ('and', eliminate_double_not(formula[1]), eliminate_double_not(formula[2]))
    elif formula[0] == 'until':
        return ('until', eliminate_double_not(formula[1]), eliminate_double_not(formula[2]))
    elif formula[0] == 'next':
        return ('next', eliminate_double_not(formula[1]))
    elif formula[0] == 'not':
        if formula[1][0] == 'not':
            return eliminate_double_not(formula[1][1])
        else:
            return ('not', eliminate_double_not(formula[1]))
    elif formula[0] == 'atom':
        return formula
    else:
        print(f'{formula}: Error: invalid transformation!')

def eliminate_same_and(formula):
    """
    eliminate the redundant subformula in the same 'and' operator
    """
    if formula[0] == 'and':
        if formula[1] == formula[2]:
            return eliminate_same_and(formula[1])
        else:
            return ('and', eliminate_same_and(formula[1]), eliminate_same_and(formula[2]))
    elif formula[0] == 'until':
        return ('until', eliminate_same_and(formula[1]), eliminate_same_and(formula[2]))
    elif formula[0] == 'next':
        return ('next', eliminate_same_and(formula[1]))
    elif formula[0] == 'not':
        return ('not', eliminate_same_and(formula[1]))
    elif formula[0] == 'atom':
        return formula
    else:
        print(f'{formula}: Error: invalid transformation!')

def calculate_closure(formula):
    """
    calculate the closure of the formula, 
    which includes the formula and all its subformulas
    note that the closure is split into two halves: half_closure_first and half_closure_second,
    either includes a formula or its negation
    """
    closure = set()

    def add_to_closure(f):
        nonlocal closure
        if f not in closure:
            closure.add(f)
        if f[0] in {'not', 'next'}:
            if f[1] not in closure:
                add_to_closure(f[1])
        elif f[0] in {'and', 'until'}:
            if f[1] not in closure:
                add_to_closure(f[1])
            if f[2] not in closure:
                add_to_closure(f[2])
    
    add_to_closure(formula)
    half_closure_first = []
    half_closure_second = []
    for s in closure:
        if s not in half_closure_first and s not in half_closure_second:
            half_closure_first.append(s)
            neg_s = eliminate_double_not(('not', s))
            half_closure_second.append(neg_s)
    return half_closure_first, half_closure_second
