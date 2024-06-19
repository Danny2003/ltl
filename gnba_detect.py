from ts import TransitionSystem
from gnba_def import GNBA, NBA
from gnba_cons import powerset

def gnba_to_nba(gnba: GNBA, props, detail):
    """
    transform a GNBA to a NBA based on the construction in Theorem 4.56 in the textbook
    """
    nba_states = []
    nba_initial_states = []
    nba_transitions = {}
    nba_acceptance_conditions = []
    
    if gnba.acceptance_conditions:
        for state in gnba.states:
            for acc in range(len(gnba.acceptance_conditions)):
                # Q \times {0, 1, ..., |F| - 1}
                nba_state = (state, acc)
                nba_states.append(nba_state)
                # $\delta'((q,j),A):= \{(q',j)\mid q'\in\delta(q,A)\}$ if $q\not\in F_j$, 
                # and $\delta'((q,j),A):= \{(q',{(j+1)}{\mod{}}{k})\mid q'\in\delta(q,A)\}$ otherwise.
                nba_transitions[nba_state] = {}
                for actions in gnba.transitions[state]:
                    nba_transitions[nba_state][actions] = []
                    for next_state in gnba.transitions[state][actions]:
                        if state not in gnba.acceptance_conditions[acc]:
                            nba_transitions[nba_state][actions].append((next_state, acc))
                        else:
                            nba_transitions[nba_state][actions].append((next_state, (acc + 1) % len(gnba.acceptance_conditions)))
        for state in gnba.initial_states:
            nba_initial_states.append((state, 0))
        
        if gnba.acceptance_conditions:
            nba_acceptance_conditions = [(state, 0) for state in gnba.acceptance_conditions[0]]
        else:
            nba_acceptance_conditions = []

        # ensure nonblocking
        nba_states.append(('trap', 0))
        nba_transitions[('trap', 0)] = {}

        ps = powerset(props)
        for state in nba_states:
            for action in ps:
                if action not in nba_transitions[state]:
                    nba_transitions[state][action] = [('trap', 0)]
                elif nba_transitions[state][action] == []:
                    nba_transitions[state][action] = [('trap', 0)]
        
        if detail:
            print("NBA states:")
            for state in nba_states:
                print(state)
            print("NBA initial states:")
            for initial_state in nba_initial_states:
                print(initial_state)
            print("NBA acceptance conditions:")
            if not nba_acceptance_conditions:
                print("empty")
            else:
                for s in nba_acceptance_conditions:
                    print(s)
            print()

        return NBA(nba_states, nba_initial_states, nba_transitions, nba_acceptance_conditions)
    else:
        nba_states = gnba.states.copy()
        nba_initial_states = gnba.initial_states.copy()
        nba_transitions = gnba.transitions.copy()
        # In this case, all states are accepting states
        nba_acceptance_conditions = gnba.states.copy()

        # ensure nonblocking
        nba_states.append(('trap', 0))
        nba_transitions[('trap', 0)] = {}

        ps = powerset(props)
        for state in nba_states:
            for action in ps:
                if action not in nba_transitions[state]:
                    nba_transitions[state][action] = [('trap', 0)]
                elif nba_transitions[state][action] == []:
                    nba_transitions[state][action] = [('trap', 0)]
        if detail:
            print("NBA states:")
            for state in nba_states:
                print(state)
            print("NBA initial states:")
            for initial_state in nba_initial_states:
                print(initial_state)
            print("NBA acceptance conditions:")
            if not nba_acceptance_conditions:
                print("empty")
            else:
                for s in nba_acceptance_conditions:
                    print(s)
            print()

        return NBA(nba_states, nba_initial_states, nba_transitions, nba_acceptance_conditions)

def product_construction(ts: TransitionSystem, nba: NBA, props, detail):
    """
    construct the product of a transition system and a NBA
    based on Definition 4.16, Page 165 in the textbook
    the nba has been ensured to be nonblocking in the gnba_to_nba function
    """
    product_states = []
    product_initial_states = []
    product_transitions = {}
    product_labeling = {}

    props_prime = [p[1] for p in props]
    # Here we only keep the propositions that are used in the NBA
    for s in ts.states:
        new_labels = set()
        for l in ts.labeling[s]:
            if l in props_prime:
                new_labels.add(l)
        ts.labeling[s] = new_labels
    ts.propositions = props_prime.copy()

    for ts_state in ts.states:
        for nba_state in nba.states:
            # S \times Q
            product_state = (ts_state, nba_state)
            product_states.append(product_state)
            # \exists q\prime \in Q_0: q \in \delta(q\prime, L(s))
            # s: ts_state
            if ts_state in ts.initial_states:
                # print(ts_state)
                # q\prime: nba_initial_state
                for nba_initial_state in nba.initial_states:
                    for actions in nba.transitions[nba_initial_state]:
                        if (nba_state in nba.transitions[nba_initial_state][actions] and
                            ts.labeling[ts_state] == {act[1] for act in actions}):
                                if product_state not in product_initial_states:
                                    product_initial_states.append(product_state)
            product_transitions[product_state] = {}

    for ts_state in ts.states:
        for action in ts.actions:
            if ts_state in ts.transitions:
                if action in ts.transitions[ts_state]:
                    for ts_next_state in ts.transitions[ts_state][action]:
                        for nba_state in nba.states:
                            for nba_act in nba.transitions[nba_state]:
                                if (ts.labeling[ts_state] == {act[1] for act in nba_act}):
                                    nba_next_states = nba.transitions[nba_state][nba_act]
                                    for nba_next_state in nba_next_states:
                                        product_state = (ts_state, nba_state)
                                        product_next_state = (ts_next_state, nba_next_state)
                                        if action not in product_transitions[product_state]:
                                            product_transitions[product_state][action] = []
                                        product_transitions[product_state][action].append(product_next_state)

    for product_state in product_states:
        ts_state, nba_state = product_state
        product_labeling[product_state] = {nba_state}  # Labeling the product state with the NBA state
    if detail:
        print("Product states:")
        for state in product_states:
            print(state)
        print("Product initial states:")
        for initial_state in product_initial_states:
            print(initial_state)
        print()

    return TransitionSystem(product_states, product_initial_states, product_transitions, ts.actions, {s for s in nba.states}, product_labeling)

def cycle_check(ts: TransitionSystem, state):
    """
    implement the Algorithm 7 Cycle detection in the textbook
    """
    T = set() # Visited states in the inner DFS
    V = [] # Stack for the inner DFS
    cycle_found = False

    V.append(state)
    T.add(state)
    while V and not cycle_found:
        s_prime = V[-1]
        post_states = []
        for action in ts.transitions[s_prime]:
            for post_state in ts.transitions[s_prime][action]:
                post_states.append(post_state)
        if state in post_states:
            cycle_found = True
            V.append(state)
        else:
            unvisited = [s_pp for s_pp in post_states if s_pp not in T]
            if unvisited:
                s_pp = unvisited[0]
                V.append(s_pp)
                T.add(s_pp)
            else:
                V.pop()
    return cycle_found, V

def nested_dfs(ts: TransitionSystem, nba: NBA, detail):
    """
    implement the Algorithm 8 Persistence checking by nested depth-first search in the textbook
    """
    R = set() # Visited states in the outer DFS
    U = [] # Stack for the outer DFS
    V = [] # Stack for the inner DFS
    cycle_found = False

    def reachable_cycle(s):
        nonlocal cycle_found
        nonlocal R
        nonlocal U
        nonlocal V
        nonlocal ts
        nonlocal nba
        U.append(s)
        R.add(s)
        while U and not cycle_found:
            s_prime = U[-1]
            post_states = []
            for action in ts.transitions[s_prime]:
                for post_state in ts.transitions[s_prime][action]:
                    post_states.append(post_state)
            unvisited = [s_pp for s_pp in post_states if s_pp not in R]
            if unvisited:
                s_pp = unvisited[0]
                U.append(s_pp)
                R.add(s_pp)
            else:
                U.pop()
                for state in ts.labeling[s_prime]:
                    if state in nba.acceptance_conditions:
                        cycle_found, V = cycle_check(ts, s_prime)
                        # if cycle_found:
                        #     print(state)
    tmp = [s for s in ts.initial_states if s not in R]
    while tmp and not cycle_found:
        s = tmp[0]
        reachable_cycle(s)
        tmp = [s for s in ts.initial_states if s not in R]
    
    if not cycle_found:
        if detail:
            print("result: true\n")
            return None
        return 1
    else:
        if detail:
            # Construct the counterexample
            # Since the top of the stack in U, V is the last element in the two lists, 
            # we don't need to reverse U + V
            countercase = U + V
            counter = 0
            length = len(countercase)
            print(f"result: false\ncountercase: ", end = "")
            for state in countercase:
                counter += 1
                print(f"s_{state[0]}", end = "")
                if not counter == length:
                    print(" -> ", end = "")
                else:
                    print()
            print()
            return None
        return 0