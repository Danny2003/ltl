def is_propositionally_consistent(subset, closure_first, closure_second):
    """
    check if the subset is propositionally consistent
    """
    closure = closure_first + closure_second
    # if we have true, then there will be either true or not true in the subset
    # if we have not true, then it should be inconsistent
    if ('not', ('atom', 'true')) in subset:
        return False
    for formula in subset:
        if isinstance(formula, tuple) and len(formula) == 3 and formula[0] == 'and':
            if formula[1] not in subset or formula[2] not in subset:
                return False
    for f1 in subset:
        for f2 in subset:
            if f1 != f2:
                if ('and', f1, f2) in closure:
                    if ('and', f1, f2) not in subset:
                        return False
    return True

def is_locally_until_consistent(subset, closure_first, closure_second):
    """
    check if the subset is locally until consistent
    """
    closure = closure_first + closure_second
    # get all until formulas in the closure
    until_formulas = [f for f in closure if isinstance(f, tuple) and len(f) == 3 and f[0] == 'until']
    for u in until_formulas:
        for formula in subset:
            if u[2] == formula:
                if u not in subset:
                    return False
        if u in subset and u[2] not in subset:
            if u[1] not in subset:
                return False
    return True

def is_elementary(subset, closure_first, closure_second):
    return is_propositionally_consistent(subset, closure_first, closure_second) and is_locally_until_consistent(subset, closure_first, closure_second)

def calculate_elementary_sets(closure_first, closure_second):
    """
    calculate all elementary sets of the closure
    generate all possible maximal sets first,
    then filter out the non-elementary sets based on Definition 5.35, Page 276 in the textbook
    note that the closure is split into two halves: half_closure_first and half_closure_second,
    so we have ensured that all sets are maximal here
    """
    subsets = []
    for i in range(1 << len(closure_first)):
        subset = set()
        for j in range(len(closure_first)):
            if i & (1 << j):
                subset.add(closure_first[j])
            else:
                subset.add(closure_second[j])
        subsets.append(subset)
    elementary_sets = []
    for subset in subsets:
        if is_elementary(subset, closure_first, closure_second):
            elementary_sets.append(subset)
    return elementary_sets
