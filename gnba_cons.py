from gnba_def import GNBA
from translate_formula import eliminate_double_not, eliminate_same_and, transform, calculate_closure
from calculate_elementary_sets import calculate_elementary_sets

def powerset(s: list):
    """
    construct the power set of a set, assuming the input set is a list without duplicate elements
    """
    ps = set()
    for i in range((1 << len(s))):
        new_set = {s[j] for j in range(len(s)) if i & (1 << j)}
        ps.add(frozenset(new_set))
    return ps

def construct_gnba(elementary_sets, closure, props, ltl_formula, detail):
    """
    construct a GNBA from the elementary sets and the closure of a LTL formula
    following the construction in Lecture Notes 11. Linear Temporal Logic C
    Args:
        elementary_sets: list of elementary sets
        closure: list of closure
        props: list of atom propositions
        ltl_formula: the negation of the original LTL formula after transformation
        detail: whether to print the details
    """
    states = [frozenset(s) for s in elementary_sets]
    initial_states = [s for s in states if ltl_formula in s]
    transitions = {s: {} for s in states}
    acceptance_conditions = []

    for formula in closure:
        if formula[0] == 'until':
            acceptance_conditions.append([s for s in states if not (formula in s and formula[2] not in s)])

    ps = powerset(props)
    
    # The transition function $\delta$ is defined such that for every $B\in Q$ and $A\subseteq \props$, we have that 
    #   * $\delta(B, A)=\emptyset$ if $A\ne B\cap \props$ (i.e., the state $B$ only reads $B\cap \props$ and otherwise get stuck); 
    #   * if $A= B\cap \props$ then 

    # $$
    # \begin{eqnarray*}
    # \delta(B, A)&=&\{B'\in Q \,\mid\,  \\
    # & & \quad\forall (\nxt\psi\in closure(\varphi)).(\nxt\psi\in B\Leftrightarrow \psi\in B')\, \wedge \\
    # & & \quad\forall (\varphi_1\,\unt\,\varphi_2\in closure(\varphi)).(\varphi_1\,\unt\,\varphi_2\in B\mbox{ iff }\varphi_2\in B \vee (\varphi_1\in B\wedge \varphi_1\,\unt\,\varphi_2 \in B')))\}
    # \end{eqnarray*}
    # $$ 
    for B in states:
        for A in ps:
            A = frozenset(A)
            B_props = B.intersection(props)
            if A == B_props:
                valid_transitions = []
                for B_prime in states:
                    if (all((formula[1] in B_prime) if formula in B else True for formula in [next_formula for next_formula in closure if next_formula[0] == 'next']) and
                        all((formula in B) if formula[1] in B_prime else True for formula in [next_formula for next_formula in closure if next_formula[0] == 'next']) and
                        all(((formula[2] in B) or (formula[1] in B and formula in B_prime)) if formula in B else True for formula in [until_formula for until_formula in closure if until_formula[0] == 'until']) and
                        all((formula in B) if ((formula[2] in B) or (formula[1] in B and formula in B_prime)) else True for formula in [until_formula for until_formula in closure if until_formula[0] == 'until'])):
                        valid_transitions.append(B_prime)
                transitions[B][A] = valid_transitions
    if detail:
        print()
        print("GNBA states:")
        for state in states:
            print(state)
        print("GNBA initial states:")
        for initial_state in initial_states:
            print(initial_state)
        print("GNBA acceptance conditions:")
        if not acceptance_conditions:
            print("empty")
        for s in acceptance_conditions:
            counter = 0
            print(f"F_{counter}:")
            for state in s:
                print(state)
            counter = counter + 1
        print()
    return GNBA(states, initial_states, transitions, acceptance_conditions)

def construct_gnba_from_ltl_formula(ltl_formula, detail):
    new_formula = eliminate_same_and(eliminate_double_not(transform(ltl_formula)))
    if detail:
        print(f"negation of the original formula after transformation:\n{new_formula}")
    half_closure_first, half_closure_second = calculate_closure(new_formula)
    closure = half_closure_first + half_closure_second
    elementary_sets = calculate_elementary_sets(half_closure_first, half_closure_second)
    props = [p for p in closure if (isinstance(p, tuple) and p[0] == 'atom' and p[1] != 'true')]
    return construct_gnba(elementary_sets, closure, props, new_formula, detail), props
