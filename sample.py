import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict


class NFA:
    def __init__(self, states, alphabet, start_state, accept_states, transitions):
        self.states = states  # Set of states
        self.alphabet = alphabet  # Alphabet (input symbols)
        self.start_state = start_state  # Start state
        self.accept_states = accept_states  # Accept (final) states
        self.transitions = transitions  # Transition function (dictionary of dictionaries)

    def add_transition(self, state, symbol, next_state):
        self.transitions[state][symbol].add(next_state)

    def get_epsilon_closure(self, state):
        """Find the epsilon closure of a given state"""
        closure = set([state])
        stack = [state]
        while stack:
            curr_state = stack.pop()
            if '' in self.transitions[curr_state]:
                for next_state in self.transitions[curr_state]['']:
                    if next_state not in closure:
                        closure.add(next_state)
                        stack.append(next_state)
        return closure


class DFA:
    def __init__(self, states, alphabet, start_state, accept_states, transition_function):
        self.states = states  # Set of states
        self.alphabet = alphabet  # Alphabet (input symbols)
        self.start_state = start_state  # Start state
        self.accept_states = accept_states  # Accept (final) states
        self.transition_function = transition_function  # Transition function (dictionary of dictionaries)

    def transition(self, state, symbol):
        return self.transition_function[state][symbol]


def regex_to_nfa(regex):
    """Convert a regular expression to NFA using Thompson's construction"""
    stack = []

    # Operators
    def concat(nfa1, nfa2):
        nfa1.add_transition(nfa1.accept_states[0], '', nfa2.start_state)
        return NFA(nfa1.states | nfa2.states, nfa1.alphabet | nfa2.alphabet,
                   nfa1.start_state, nfa2.accept_states, {**nfa1.transitions, **nfa2.transitions})

    def union(nfa1, nfa2):
        start_state = len(nfa1.states) + len(nfa2.states)
        accept_state = start_state + 1
        transitions = defaultdict(lambda: defaultdict(set))
        
        # Add epsilon transitions from the new start state to the start states of the two NFAs
        transitions[start_state][''].update([nfa1.start_state, nfa2.start_state])
        
        # Add epsilon transitions from the accept states of nfa1 and nfa2 to the new accept state
        transitions[next(iter(nfa1.accept_states))][''].add(accept_state)
        transitions[next(iter(nfa2.accept_states))][''].add(accept_state)
        
        return NFA(nfa1.states | nfa2.states | {start_state, accept_state},
                nfa1.alphabet | nfa2.alphabet, start_state, {accept_state}, transitions)

    def kleene_star(nfa):
        start_state = len(nfa.states)
        accept_state = start_state + 1
        transitions = defaultdict(lambda: defaultdict(set))
        
        # Add epsilon transitions from the new start state to the old start state and new accept state
        transitions[start_state][''].update([nfa.start_state, accept_state])
        
        # Add epsilon transition from the old accept state back to the old start state
        transitions[next(iter(nfa.accept_states))][''].add(accept_state)
        transitions[accept_state][''].add(nfa.start_state)
        
        return NFA(nfa.states | {start_state, accept_state}, nfa.alphabet,
                start_state, {accept_state}, {**nfa.transitions, **transitions})

    def single_char(c):
        start_state = 0
        accept_state = 1
        transitions = defaultdict(lambda: defaultdict(set))
        transitions[start_state][c].add(accept_state)
        return NFA({start_state, accept_state}, {c}, start_state, {accept_state}, transitions)

    # Parse the regex
    for c in regex:
        if c.isalnum():
            stack.append(single_char(c))
        elif c == '.':
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            stack.append(concat(nfa1, nfa2))
        elif c == '|':
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            stack.append(union(nfa1, nfa2))
        elif c == '*':
            nfa = stack.pop()
            stack.append(kleene_star(nfa))

    return stack.pop()


def nfa_to_dfa(nfa):
    """Convert an NFA to DFA using the subset construction algorithm"""
    start_closure = frozenset(nfa.get_epsilon_closure(nfa.start_state))
    unmarked_states = [start_closure]
    dfa_states = {start_closure}
    dfa_transitions = {}
    dfa_accept_states = set()

    while unmarked_states:
        current_set = unmarked_states.pop()
        dfa_transitions[current_set] = {}

        if nfa.accept_states & current_set:
            dfa_accept_states.add(current_set)

        for symbol in nfa.alphabet:
            next_set = set()
            for state in current_set:
                if symbol in nfa.transitions[state]:
                    for next_state in nfa.transitions[state][symbol]:
                        next_set.update(nfa.get_epsilon_closure(next_state))
            next_set = frozenset(next_set)
            if next_set not in dfa_states:
                dfa_states.add(next_set)
                unmarked_states.append(next_set)
            dfa_transitions[current_set][symbol] = next_set

    dfa_start_state = start_closure
    return DFA(dfa_states, nfa.alphabet, dfa_start_state, dfa_accept_states, dfa_transitions)


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
        print(f"{state}\t", "\t".join(map(str, transitions)))


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


# Main code to select options
def main():
    regex = input("Enter a regular expression: ")
    print("1. Convert to NFA")
    print("2. Convert to DFA")
    print("3. Minimize DFA")
    option = int(input("Choose an option: "))

    nfa = regex_to_nfa(regex)

    if option == 1:
        print("NFA constructed:")
        # visualize NFA (can be implemented)
    elif option == 2:
        dfa = nfa_to_dfa(nfa)
        print("DFA constructed:")
        visualize_dfa(dfa)
        visualize_dfa_graph(dfa)
    elif option == 3:
        dfa = nfa_to_dfa(nfa)
        minimized_dfa = minimize_dfa(dfa)
        print("Minimized DFA constructed:")
        visualize_dfa(minimized_dfa)
        visualize_dfa_graph(minimized_dfa)


if __name__ == "__main__":
    main()
