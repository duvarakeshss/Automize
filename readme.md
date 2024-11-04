# Grammar to DFA Minimization Tool

A Streamlit-based tool that converts context-free grammars in Backus-Naur Form (BNF) to a minimized Deterministic Finite Automaton (DFA). The tool allows users to visualize the transitions between different states in the automata and test if a given string is accepted by the minimized DFA.

## Features

* **Grammar to NDFA Conversion** : Parses input grammar and generates a Nondeterministic Finite Automaton (NDFA).
* **NDFA to DFA Conversion** : Converts the generated NDFA to a Deterministic Finite Automaton (DFA).
* **DFA Minimization** : Minimizes the DFA using the Myhill-Nerode theorem.
* **Visualization** : Displays the structure of the NDFA, DFA, and minimized DFA using Graphviz.
* **String Testing** : AllInstall the required packages:ows users to check if a string is accepted by the minimized DFA.

## Tech Stack

* **Python** : Core programming language.
* **Streamlit** : For building the interactive user interface.
* **Graphviz** : For visualizing the automata.

## Getting Started


### Prerequisites

* **Python** 3.7+
* **Streamlit** and **Graphviz** packages

---

#### Install the required packages:

```bash
pip install streamlit graphviz
```
#### Running the Application
* **Clone the repository :**
  ```bash
  git clone https://github.com/duvarakeshss/Automize
  ```
* **Run the Streamlit app:**
  ```bash
    streamlit run main.py
  ```
  
