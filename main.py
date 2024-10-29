import streamlit as st
from collections import defaultdict, deque
import graphviz

# Function to convert grammar to NDFA
def grammar_to_ndfa(grammar):
    rules = grammar.split(":")  # Split productions by colon
    ndfa = {
        "states": set(),
        "alphabet": set(),
        "transitions": defaultdict(set),
        "start_state": None,
        "accept_states": set()
    }

    # Parse each rule
    for rule in rules:
        if "->" in rule:
            lhs, rhs = rule.split("->")
            lhs = lhs.strip()
            rhs_options = rhs.split("|")

            ndfa["states"].add(lhs)
            for option in rhs_options:
                option = option.strip()
                for char in option:
                    if char.islower():  # Assuming lowercase letters are part of the alphabet
                        ndfa["alphabet"].add(char)

                # Create transitions for each option
                for char in option:
                    if char.islower():  # Only consider terminal characters
                        ndfa["transitions"][lhs].add(char)
                    elif char.isupper():  # Non-terminal character
                        ndfa["transitions"][lhs].add(char)

            # Treat epsilon (ε) as an accept state
            if "ε" in option:
                ndfa["accept_states"].add(lhs)

    ndfa["start_state"] = rules[0].split("->")[0].strip()  # Set the start state as the first LHS

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
                    dfa["states"].add(next_state_name)
                    state_map[next_state_name] = f"Q{len(dfa['states'])}"
                    unprocessed_states.append(next_state_name)
                dfa["transitions"][(current_state_name, char)] = state_map[next_state_name]

    # Determine accepting states
    for state in state_map.keys():
        if any(s in ndfa["accept_states"] for s in state):
            dfa["accept_states"].add(state_map[state])

    dfa["start_state"] = 'Q0'  # Set the start state

    return dfa

# Function to minimize the DFA using Myhill-Nerode theorem
def minimize_dfa(dfa):
    partition = []
    state_list = list(dfa["states"])
    
    # Initial partitioning
    accepting = set(dfa["accept_states"])
    non_accepting = set(state_list) - accepting
    
    if accepting:
        partition.append(accepting)
    if non_accepting:
        partition.append(non_accepting)

    # Split partitions until they are stable
    while True:
        new_partition = []
        for part in partition:
            part_list = list(part)
            while part_list:
                representative = part_list.pop()
                same_group = {representative}
                to_check = part_list.copy()
                to_check.append(representative)

                for state in to_check:
                    if not are_distinguishable(dfa, representative, state):
                        same_group.add(state)
                
                part_list = [s for s in part_list if s not in same_group]
                new_partition.append(same_group)

        if len(new_partition) == len(partition):
            break
        partition = new_partition

    # Build minimized DFA
    min_dfa = {
        "states": set(),
        "alphabet": dfa["alphabet"],
        "transitions": {},
        "start_state": None,
        "accept_states": set()
    }
    
    state_map = {}
    for part in partition:
        part_name = frozenset(part)
        min_dfa["states"].add(part_name)
        if dfa["start_state"] in part:
            min_dfa["start_state"] = part_name
        if any(s in dfa["accept_states"] for s in part):
            min_dfa["accept_states"].add(part_name)
    
    # Create transitions
    for part in partition:
        part_name = frozenset(part)
        for char in dfa["alphabet"]:
            next_states = set()
            for state in part:
                if (state, char) in dfa["transitions"]:
                    next_states.add(dfa["transitions"][(state, char)])

            if next_states:
                next_part = next((p for p in partition if next_states & p), None)
                if next_part:
                    min_dfa["transitions"][(part_name, char)] = frozenset(next_part)

    return min_dfa

def are_distinguishable(dfa, state1, state2):
    """Check if two states are distinguishable in the given DFA."""
    for char in dfa["alphabet"]:
        next1 = dfa["transitions"].get((state1, char))
        next2 = dfa["transitions"].get((state2, char))
        
        if next1 != next2:
            return True
    return False

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

# Input for grammar
st.header("Grammar Input")
grammar_input = st.text_area("Enter your grammar (in BNF format, separate productions with colons):", 
                              st.session_state.grammar_input, height=150)

# Display the entered grammar for rechecking
st.subheader("Entered Grammar:")
st.text(grammar_input)

# Addition of new productions
new_production = st.text_input("Enter new production (e.g., A -> aA | b):")
if st.button("Add Production"):
    if new_production:
        # Append new production with colon separator
        if st.session_state.grammar_input.strip():
            st.session_state.grammar_input += f": {new_production}"  
        else:
            st.session_state.grammar_input = new_production  # For the first production
        st.success("Production added!")
        st.experimental_rerun()  # Rerun to refresh the UI with updated grammar

# Process input on button click
if st.button("Convert Grammar"):
    grammar = grammar_input.strip()
    
    if grammar:
        # Convert grammar to NDFA
        st.session_state.ndfa = grammar_to_ndfa(grammar)
        st.subheader("Nondeterministic Finite Automaton (NDFA)")
        st.json(st.session_state.ndfa)

        # Visualize NDFA
        ndfa_graph = visualize_automaton(st.session_state.ndfa, "NDFA")
        st.graphviz_chart(ndfa_graph)

        # Convert NDFA to DFA
        st.session_state.dfa = ndfa_to_dfa(st.session_state.ndfa)
        st.subheader("Deterministic Finite Automaton (DFA)")
        st.json(st.session_state.dfa)

        # Visualize DFA
        dfa_graph = visualize_automaton(st.session_state.dfa, "DFA")
        st.graphviz_chart(dfa_graph)

        # Minimize DFA and visualize only if `dfa` is correctly created
        if st.session_state.dfa:
            st.session_state.minimized_dfa = minimize_dfa(st.session_state.dfa)
            st.subheader("Minimized DFA")
            st.json(st.session_state.minimized_dfa)

            # Visualize minimized DFA
            minimized_dfa_graph = visualize_automaton(st.session_state.minimized_dfa, "Minimized DFA")
            st.graphviz_chart(minimized_dfa_graph)

# String testing logic
test_string = st.text_input("Enter a string to test against the minimized DFA:", "")
if st.button("Test String"):
    if st.session_state.minimized_dfa:
        current_state = st.session_state.minimized_dfa.get("start_state")
        accepted = True

        # Process each character in the test string
        for char in test_string:
            next_state = st.session_state.minimized_dfa["transitions"].get((current_state, char))
            if next_state:
                current_state = next_state  # Move to the next state
            else:
                accepted = False
                break  # Break if no valid transition exists

        # Check if the final state is an accept state
        if accepted and current_state in st.session_state.minimized_dfa["accept_states"]:
            st.session_state.test_result = "The string is accepted by the DFA."
        else:
            st.session_state.test_result = "The string is rejected by the DFA."
    else:
        st.session_state.test_result = "Please convert a valid grammar before testing strings."

# Display the test result
if st.session_state.test_result:
    st.success(st.session_state.test_result)

# Notes for implementation details
st.markdown("""
### Implementation Details:
- *NDFA Conversion*: The application converts input BNF grammar to a nondeterministic finite automaton (NDFA).
- *DFA Conversion*: The NDFA is converted to a deterministic finite automaton (DFA) using subset construction.
- *Minimization*: The DFA is minimized using the Myhill-Nerode theorem.
- *Visualization*: Automata are visualized using Graphviz for easy understanding.
- *String Testing*: Users can input strings to test against the minimized DFA.
""")
