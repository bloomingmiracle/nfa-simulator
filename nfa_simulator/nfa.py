"""
NFA Simulator - Core Engine
Linguagens Formais e Computabilidade - Projeto 01

Supports:
  - Non-deterministic Finite Automata (NFA / AFN)
  - Epsilon (ε) transitions
  - Step-by-step simulation trace
"""

import json
import sys


# ---------------------------------------------------------------------------
# Core NFA functions
# ---------------------------------------------------------------------------

def epsilon_closure(states, transitions):
    """
    Given a SET of states, return all states reachable via ε-transitions
    (including the states themselves).

    This is the key extra step for NFA with epsilon:
    whenever you land on a state, you also get every state reachable
    by following ε arrows for free.
    """
    closure = set(states)   # start with the states themselves
    stack = list(states)    # use a stack to explore

    while stack:
        state = stack.pop()
        # get all states reachable from 'state' via ε
        eps_targets = transitions.get(state, {}).get("ε", [])
        for target in eps_targets:
            if target not in closure:
                closure.add(target)
                stack.append(target)  # explore further from here

    return closure


def move(states, symbol, transitions):
    """
    Given a SET of states and a symbol, return all states reachable
    by reading that symbol from any state in the set.
    """
    result = set()
    for state in states:
        targets = transitions.get(state, {}).get(symbol, [])
        result.update(targets)
    return result


def simulate(nfa, input_string):
    """
    Simulate the NFA on input_string.

    Returns a dict with:
      - 'accepted': True/False
      - 'trace': list of steps, each with the symbol read and active states
      - 'final_states': the active states after the last symbol
    """
    transitions = nfa["transitions"]
    accept_states = set(nfa["accept"])

    # Step 1: start at the initial state, then immediately take ε-closure
    start = {nfa["start"]}
    current = epsilon_closure(start, transitions)

    # Record the trace (for visualization step-by-step)
    trace = [
        {"symbol": None, "states": sorted(current), "description": "Estado inicial (após ε-fecho)"}
    ]

    # Step 2: for each symbol in the input string...
    for symbol in input_string:
        # 2a. Move: where can we go reading this symbol?
        after_move = move(current, symbol, transitions)
        # 2b. ε-closure: follow any free ε-transitions from there
        current = epsilon_closure(after_move, transitions)

        trace.append({
            "symbol": symbol,
            "states": sorted(current),
            "description": f"Leu '{symbol}' → estados ativos: {sorted(current)}"
        })

        # If we have no active states, the automaton is stuck — stop early
        if not current:
            break

    # Step 3: accept if ANY active state is an accepting state
    accepted = bool(current & accept_states)

    return {
        "accepted": accepted,
        "trace": trace,
        "final_states": sorted(current),
        "accept_states": sorted(accept_states),
    }


# ---------------------------------------------------------------------------
# Loading an NFA from JSON
# ---------------------------------------------------------------------------

def load_nfa(path):
    """Load an NFA definition from a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_nfa(nfa):
    """Basic sanity checks on the NFA definition."""
    required = ["states", "alphabet", "transitions", "start", "accept"]
    for field in required:
        if field not in nfa:
            raise ValueError(f"Campo obrigatório ausente no JSON: '{field}'")

    if nfa["start"] not in nfa["states"]:
        raise ValueError(f"Estado inicial '{nfa['start']}' não está na lista de estados.")

    for s in nfa["accept"]:
        if s not in nfa["states"]:
            raise ValueError(f"Estado de aceitação '{s}' não está na lista de estados.")


# ---------------------------------------------------------------------------
# CLI — run from terminal: python nfa.py nfa.json "input_string"
# ---------------------------------------------------------------------------

def print_trace(result, input_string):
    print("\n" + "=" * 50)
    print(f"  Entrada: '{input_string}'")
    print("=" * 50)

    for step in result["trace"]:
        if step["symbol"] is None:
            print(f"\n  Início → estados: {step['states']}")
        else:
            status = "✓" if step["states"] else "✗ (morto)"
            print(f"  Leu '{step['symbol']}' → estados: {step['states']} {status}")

    print()
    if result["accepted"]:
        print("  ✅  ACEITA  — algum estado final ativo:", result["final_states"])
    else:
        print("  ❌  REJEITA — nenhum estado final ativo nos estados:", result["final_states"])
    print("=" * 50 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python nfa.py <arquivo_nfa.json> <cadeia_de_entrada>")
        print("Exemplo: python nfa.py exemplo.json aab")
        sys.exit(1)

    nfa_path = sys.argv[1]
    input_string = sys.argv[2]

    nfa = load_nfa(nfa_path)
    validate_nfa(nfa)

    result = simulate(nfa, input_string)
    print_trace(result, input_string)
