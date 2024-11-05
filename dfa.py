import streamlit as st
from collections import defaultdict, deque
import graphviz


# Function to convert grammar to NDFA
def grammar_to_ndfa(grammar):
    rules = grammar.split(":")
    ndfa = {
        "states": set(),
        "alphabet": set(),
        "transitions": defaultdict(set),
        "start_state": None,
        "accept_states": set()
    }

    for rule in rules:
        if "->" in rule:
            lhs, rhs = rule.split("->")
            lhs = lhs.strip()
            rhs_options = rhs.split("|")

            ndfa["states"].add(lhs)
            for option in rhs_options:
                option = option.strip()
                for char in option:
                    if char.islower():
                        ndfa["alphabet"].add(char)

                for char in option:
                    if char.islower():
                        ndfa["transitions"][lhs].add(char)
                    elif char.isupper():
                        ndfa["transitions"][lhs].add(char)

            if "ε" in option:
                ndfa["accept_states"].add(lhs)

    ndfa["start_state"] = rules[0].split("->")[0].strip()

    return ndfa

# Function to convert NDFA to DFA
def ndfa_to_dfa(ndfa):
    dfa = {
        "states": set(),
        "alphabet": ndfa["alphabet"],
        "transitions": {},
        "start_state": None,
        "accept_states": set()
    }

    state_map = {}
    new_state = frozenset([ndfa["start_state"]])
    state_map[new_state] = 'Q0'
    dfa["states"].add('Q0')

    unprocessed_states = deque([new_state])

    while unprocessed_states:
        current = unprocessed_states.popleft()
        current_state_name = state_map[current]

        for char in dfa["alphabet"]:
            next_states = set()
            for state in current:
                if state in ndfa["transitions"] and char in ndfa["transitions"][state]:
                    next_states.update(ndfa["transitions"][state])

            if next_states:
                next_state_name = frozenset(next_states)
                if next_state_name not in state_map:
                    state_map[next_state_name] = f"Q{len(state_map)}"
                    dfa["states"].add(state_map[next_state_name])
                    unprocessed_states.append(next_state_name)
                dfa["transitions"][(current_state_name, char)] = state_map[next_state_name]

    for state in state_map.keys():
        if any(s in ndfa["accept_states"] for s in state):
            dfa["accept_states"].add(state_map[state])

    dfa["start_state"] = 'Q0'

    return dfa

# Function to minimize the DFA
def minimize_dfa(dfa):
    partition = [set(dfa["accept_states"]), set(dfa["states"]) - set(dfa["accept_states"])]

    while True:
        new_partition = []
        for group in partition:
            subgroups = {}
            for state in group:
                key = tuple(dfa["transitions"].get((state, char)) for char in dfa["alphabet"])
                if key not in subgroups:
                    subgroups[key] = set()
                subgroups[key].add(state)
            new_partition.extend(subgroups.values())
        
        if new_partition == partition:
            break
        partition = new_partition

    state_map = {frozenset(group): f"M{idx}" for idx, group in enumerate(partition)}

    min_dfa = {
        "states": set(state_map.values()),
        "alphabet": dfa["alphabet"],
        "transitions": {},
        "start_state": state_map[frozenset([dfa["start_state"]])],
        "accept_states": set(state_map[frozenset(group)] for group in partition if group & dfa["accept_states"])
    }

    for group in partition:
        representative = next(iter(group))
        for char in dfa["alphabet"]:
            target = dfa["transitions"].get((representative, char))
            if target:
                min_dfa["transitions"][(state_map[frozenset(group)], char)] = state_map[frozenset([t for t in partition if target in t][0])]

    return min_dfa

# Function to visualize the NDFA or DFA
def visualize_automaton(automaton, title):
    dot = graphviz.Digraph(comment=title)

    # Adding states
    for state in automaton["states"]:
        if state in automaton["accept_states"]:
            dot.node(str(state), str(state), shape='doublecircle')
        else:
            dot.node(str(state), str(state))
    
    # Adjust the transition visualization logic
    for key, end in automaton["transitions"].items():
        if isinstance(key, tuple) and len(key) == 2:
            start, char = key
        else:
            start = key  # Handle single-item keys
            char = ''    # Default or empty label for single-item keys
        dot.edge(str(start), str(end), label=char)

    return dot


# Streamlit UI
st.title("Grammar to DFA/NDFA Minimization Tool")

# Initialize session state for grammar and results
if 'grammar_input' not in st.session_state:
    st.session_state.grammar_input = "S -> aS | bS | ε"
if 'ndfa' not in st.session_state:
    st.session_state.ndfa = {}
if 'dfa' not in st.session_state:
    st.session_state.dfa = {}
if 'minimized_dfa' not in st.session_state:
    st.session_state.minimized_dfa = {}
if 'test_result' not in st.session_state:
    st.session_state.test_result = ""

grammar_input = st.text_area("Enter your grammar (in BNF format, separate productions with colons):", st.session_state.grammar_input, height=150)

new_production = st.text_input("Enter new production (e.g., A -> aA | b):")
if st.button("Add Production"):
    if new_production:
        if st.session_state.grammar_input.strip():
            st.session_state.grammar_input += f": {new_production}"  
        else:
            st.session_state.grammar_input = new_production
        st.experimental_rerun()

if st.button("Convert Grammar"):
    grammar = grammar_input.strip()
    
    if grammar:
        st.session_state.ndfa = grammar_to_ndfa(grammar)
        st.subheader("NDFA")
        st.json(st.session_state.ndfa)
        st.graphviz_chart(visualize_automaton(st.session_state.ndfa, "NDFA"))

        st.session_state.dfa = ndfa_to_dfa(st.session_state.ndfa)
        st.subheader("DFA")
        st.json(st.session_state.dfa)
        st.graphviz_chart(visualize_automaton(st.session_state.dfa, "DFA"))

        if st.session_state.dfa:
            st.session_state.minimized_dfa = minimize_dfa(st.session_state.dfa)
            st.subheader("Minimized DFA")
            st.json(st.session_state.minimized_dfa)
            st.graphviz_chart(visualize_automaton(st.session_state.minimized_dfa, "Minimized DFA"))

test_string = st.text_input("Enter a string to test against the minimized DFA:", "")
if st.button("Test String"):
    if st.session_state.minimized_dfa:
        current_state = st.session_state.minimized_dfa.get("start_state")
        accepted = True

        for char in test_string:
            next_state = st.session_state.minimized_dfa["transitions"].get((current_state, char))
            if next_state:
                current_state = next_state
            else:
                accepted = False
                break

        if accepted and current_state in st.session_state.minimized_dfa["accept_states"]:
            st.session_state.test_result = "The string is accepted by the DFA."
        else:
            st.session_state.test_result = "The string is rejected by the DFA."
    else:
        st.session_state.test_result = "Please convert a valid grammar before testing strings."

if st.session_state.test_result:
    st.success(st.session_state.test_result)
