import matplotlib.pyplot as plt
import networkx as nx

class DFA:
    def __init__(self, states, alphabet, start_state, accept_states, transition_function):
        self.states = states  # Set of states
        self.alphabet = alphabet  # Alphabet (input symbols)
        self.start_state = start_state  # Start state
        self.accept_states = accept_states  # Accept (final) states
        self.transition_function = transition_function  # Transition function (dictionary of dictionaries)

    def transition(self, state, symbol):
        return self.transition_function[state][symbol]

def minimize_dfa(dfa):
    states = dfa.states
    alphabet = dfa.alphabet
    accept_states = dfa.accept_states

    # Initialize table for distinguishing states
    distinguishable = {}

    # Mark pairs of states as distinguishable if one is final and the other is not
    for state1 in states:
        for state2 in states:
            if (state1 in accept_states) != (state2 in accept_states):
                distinguishable[(state1, state2)] = True

    # Iteratively mark states as distinguishable if their transitions lead to distinguishable states
    changed = True
    while changed:
        changed = False
        for state1 in states:
            for state2 in states:
                if (state1, state2) not in distinguishable:
                    for symbol in alphabet:
                        next1 = dfa.transition(state1, symbol)
                        next2 = dfa.transition(state2, symbol)
                        if (next1, next2) in distinguishable or (next2, next1) in distinguishable:
                            distinguishable[(state1, state2)] = True
                            changed = True
                            break

    # Merge indistinguishable states
    new_states = []
    merged_states = {}
    for state1 in states:
        for state2 in states:
            if (state1, state2) not in distinguishable and (state2, state1) not in distinguishable:
                if state2 not in merged_states:
                    merged_states[state2] = state1
                new_states.append(state1)

    # Construct new minimized DFA
    minimized_states = set(new_states)
    minimized_transition_function = {}
    for state in minimized_states:
        minimized_transition_function[state] = {}
        for symbol in alphabet:
            next_state = dfa.transition(state, symbol)
            if next_state in merged_states:
                next_state = merged_states[next_state]
            minimized_transition_function[state][symbol] = next_state

    minimized_dfa = DFA(minimized_states, alphabet, dfa.start_state, accept_states, minimized_transition_function)
    return minimized_dfa

def visualize_dfa(dfa):
    print("States:", dfa.states)
    print("Alphabet:", dfa.alphabet)
    print("Start State:", dfa.start_state)
    print("Accept States:", dfa.accept_states)
    print("\nTransition Table:")
    print("State\t", "\t".join(dfa.alphabet))
    for state in dfa.states:
        transitions = [dfa.transition(state, symbol) for symbol in dfa.alphabet]
        print(f"{state}\t", "\t".join(transitions))

def visualize_dfa_graph(dfa):
    G = nx.DiGraph()
    
    for state in dfa.states:
        for symbol in dfa.alphabet:
            next_state = dfa.transition(state, symbol)
            G.add_edge(state, next_state, label=symbol)

    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=2000, node_color="skyblue", font_size=10, font_weight="bold")
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    
    plt.show()

# Example DFA
states = {'q0', 'q1', 'q2'}
alphabet = {'a', 'b'}
start_state = 'q0'
accept_states = {'q1'}
transition_function = {
    'q0': {'a': 'q1', 'b': 'q2'},
    'q1': {'a': 'q0', 'b': 'q2'},
    'q2': {'a': 'q2', 'b': 'q1'}
}

dfa = DFA(states, alphabet, start_state, accept_states, transition_function)

# Minimize the DFA
minimized_dfa = minimize_dfa(dfa)

# Visualize original DFA
print("Original DFA:")
visualize_dfa(dfa)

# Visualize minimized DFA
print("\nMinimized DFA:")
visualize_dfa(minimized_dfa)

# Visualize DFA using graph
visualize_dfa_graph(minimized_dfa)
