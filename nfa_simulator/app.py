"""
Flask API Server – NFA Simulator
Linguagens Formais e Computabilidade – Projeto 01

Endpoints:
  POST /simulate   – simulate an NFA on an input string
  GET  /examples   – return the built-in example NFAs
  POST /validate   – validate an NFA definition (without simulating)
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os

from nfa import simulate, validate_nfa

app = Flask(__name__)
CORS(app)   # allow requests from the HTML page (file:// or any origin)


# ---------------------------------------------------------------------------
# Built-in examples (same NFAs used in the HTML page)
# ---------------------------------------------------------------------------

EXAMPLES = {
    "termina_em_ab": {
        "comment": "Aceita cadeias sobre {a,b} que terminam em 'ab'",
        "states": ["q0", "q1", "q2"],
        "alphabet": ["a", "b"],
        "start": "q0",
        "accept": ["q2"],
        "transitions": {
            "q0": {"a": ["q0", "q1"], "b": ["q0"]},
            "q1": {"b": ["q2"]},
            "q2": {}
        }
    },
    "epsilon_exemplo": {
        "comment": "NFA com ε-transições: aceita cadeias de só 'a's ou só 'b's",
        "states": ["q0", "q1", "q2", "q3"],
        "alphabet": ["a", "b"],
        "start": "q0",
        "accept": ["q1", "q3"],
        "transitions": {
            "q0": {"ε": ["q1", "q2"]},
            "q1": {"a": ["q1"]},
            "q2": {"b": ["q3"]},
            "q3": {}
        }
    },
    "div3_binario": {
        "comment": "DFA (usado como NFA) que aceita números binários divisíveis por 3",
        "states": ["q0", "q1", "q2"],
        "alphabet": ["0", "1"],
        "start": "q0",
        "accept": ["q0"],
        "transitions": {
            "q0": {"0": ["q0"], "1": ["q1"]},
            "q1": {"0": ["q2"], "1": ["q0"]},
            "q2": {"0": ["q1"], "1": ["q2"]}
        }
    }
}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def index():
    return jsonify({
        "name": "NFA Simulator API",
        "version": "1.0",
        "endpoints": {
            "POST /simulate": "Simulate an NFA on an input string",
            "GET  /examples": "List built-in example NFAs",
            "POST /validate": "Validate an NFA definition"
        }
    })


@app.post("/simulate")
def route_simulate():
    """
    Request body (JSON):
      {
        "nfa": { <NFA definition> },
        "input": "aab"
      }

    Response:
      {
        "accepted": true/false,
        "trace": [ { "symbol": "a", "states": ["q0","q1"] }, ... ],
        "final_states": ["q2"],
        "accept_states": ["q2"]
      }
    """
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "Request body must be JSON"}), 400

    nfa_def = body.get("nfa")
    input_string = body.get("input", "")

    if not nfa_def:
        return jsonify({"error": "Missing field: 'nfa'"}), 400

    # Validate before simulating
    try:
        validate_nfa(nfa_def)
    except ValueError as e:
        return jsonify({"error": str(e)}), 422

    result = simulate(nfa_def, input_string)
    return jsonify(result)


@app.get("/examples")
def route_examples():
    """Return all built-in example NFAs."""
    return jsonify(EXAMPLES)


@app.get("/examples/<name>")
def route_example_by_name(name):
    """Return one example NFA by key name."""
    ex = EXAMPLES.get(name)
    if not ex:
        available = list(EXAMPLES.keys())
        return jsonify({"error": f"Example '{name}' not found", "available": available}), 404
    return jsonify(ex)


@app.post("/validate")
def route_validate():
    """
    Validate an NFA definition without simulating it.

    Request body: { "nfa": { <NFA definition> } }
    Response:     { "valid": true } or { "valid": false, "error": "..." }
    """
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "Request body must be JSON"}), 400

    nfa_def = body.get("nfa")
    if not nfa_def:
        return jsonify({"error": "Missing field: 'nfa'"}), 400

    try:
        validate_nfa(nfa_def)
        return jsonify({"valid": True})
    except ValueError as e:
        return jsonify({"valid": False, "error": str(e)}), 422


# ---------------------------------------------------------------------------
# Dev server entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n🚀  NFA Simulator API running at http://localhost:{port}")
    print(f"    Endpoints: GET /examples  |  POST /simulate  |  POST /validate\n")
    app.run(debug=True, port=port)
