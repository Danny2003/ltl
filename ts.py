class TransitionSystem:
    """
    class for TransitionSystem
    Attributes:
        states: list of states
        initial_states: list of initial states
        transitions: dictionary of transitions
        actions: list of actions
        propositions: list of propositions
        labeling: list of labeling, each element is a set of propositions
    """
    def __init__(self, states, initial_states, transitions, actions, propositions, labeling):
        """
        initial construction function for TransitionSystem
        """
        self.states = states
        self.initial_states = initial_states
        self.transitions = transitions
        self.actions = actions
        self.propositions = propositions
        self.labeling = labeling
    def copy(self):
        """
        copy construction function for TransitionSystem
        """
        states = self.states.copy()
        initial_states = self.initial_states.copy()
        transitions = {s: {a: self.transitions[s][a].copy() for a in self.transitions[s]} for s in self.transitions}
        actions = self.actions.copy()
        propositions = self.propositions.copy()
        labeling = [self.labeling[i].copy() for i in range(len(self.labeling))]
        return TransitionSystem(states, initial_states, transitions, actions, propositions, labeling)
    
def parse_transition_system(input_str):
    """
    parse the input string to construct a TransitionSystem
    """
    lines = input_str.strip().split('\n')
    s, t = map(int, lines[0].split())
    
    initial_states = list(map(int, lines[1].split()))
    actions = list(map(int, lines[2].split()))
    propositions = lines[3].split()
    transitions = {}
    for i in range(4, 4 + t):
        src, act, dst = map(int, lines[i].split())
        if src not in transitions:
            transitions[src] = {}
        if act not in transitions[src]:
            transitions[src][act] = []
        transitions[src][act].append(dst)
    for act in actions:
        for state in transitions:
            if act not in transitions[state]:
                transitions[state][act] = []
    labeling = []
    for i in range(4 + t, 4 + t + s):
        label = list(map(int, lines[i].split()))
        if label == [-1]:
            labeling.append(set())
        else:
            labeling.append({propositions[j] for j in label})
    return TransitionSystem(list(range(s)), initial_states, transitions, actions, propositions, labeling)

