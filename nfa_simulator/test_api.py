"""
Testes da API Flask – NFA Simulator
Linguagens Formais e Computabilidade – Projeto 01

Roda com: python test_api.py
(o servidor Flask precisa estar rodando em localhost:5000)
"""

import json
import urllib.request
import urllib.error
import sys

BASE = "http://localhost:5000"
PASS = 0
FAIL = 0


def req(method, path, body=None):
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"} if data else {}
    r = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(r) as res:
        return res.status, json.loads(res.read())


def check(label, status, got, expected_status, expected_accepted=None):
    global PASS, FAIL
    ok = status == expected_status
    if expected_accepted is not None:
        ok = ok and got.get("accepted") == expected_accepted
    symbol = "✅" if ok else "❌"
    print(f"  {symbol}  {label}")
    if not ok:
        print(f"       got status={status}, accepted={got.get('accepted')}")
        print(f"       expected status={expected_status}, accepted={expected_accepted}")
        FAIL += 1
    else:
        PASS += 1


print("\n" + "=" * 55)
print("  NFA Simulator – API Tests")
print("=" * 55)

# --- /simulate: NFA que termina em 'ab' ---
nfa_ab = {
    "states": ["q0", "q1", "q2"], "alphabet": ["a", "b"],
    "start": "q0", "accept": ["q2"],
    "transitions": {
        "q0": {"a": ["q0", "q1"], "b": ["q0"]},
        "q1": {"b": ["q2"]},
        "q2": {}
    }
}

print("\n[1] NFA – termina em 'ab'")
s, r = req("POST", "/simulate", {"nfa": nfa_ab, "input": "aab"})
check("'aab' → ACEITA", s, r, 200, True)

s, r = req("POST", "/simulate", {"nfa": nfa_ab, "input": "ba"})
check("'ba'  → REJEITA", s, r, 200, False)

s, r = req("POST", "/simulate", {"nfa": nfa_ab, "input": ""})
check("''    → REJEITA (vazia)", s, r, 200, False)

s, r = req("POST", "/simulate", {"nfa": nfa_ab, "input": "ab"})
check("'ab'  → ACEITA", s, r, 200, True)

# --- /simulate: NFA com ε-transições ---
nfa_eps = {
    "states": ["q0", "q1", "q2", "q3"], "alphabet": ["a", "b"],
    "start": "q0", "accept": ["q1", "q3"],
    "transitions": {
        "q0": {"ε": ["q1", "q2"]},
        "q1": {"a": ["q1"]},
        "q2": {"b": ["q3"]},
        "q3": {}
    }
}

print("\n[2] NFA com ε-transições")
s, r = req("POST", "/simulate", {"nfa": nfa_eps, "input": "aaa"})
check("'aaa' → ACEITA", s, r, 200, True)

s, r = req("POST", "/simulate", {"nfa": nfa_eps, "input": "b"})
check("'b'   → ACEITA (q3 é aceite)", s, r, 200, True)

s, r = req("POST", "/simulate", {"nfa": nfa_eps, "input": "bb"})
check("'bb'  → REJEITA (q3 não tem transição p/ b)", s, r, 200, False)

s, r = req("POST", "/simulate", {"nfa": nfa_eps, "input": "ab"})
check("'ab'  → REJEITA (mistura)", s, r, 200, False)

s, r = req("POST", "/simulate", {"nfa": nfa_eps, "input": ""})
check("''    → ACEITA (ε-fecho já inclui q1)", s, r, 200, True)

# --- /validate ---
print("\n[3] Validação de NFA")
try:
    s, r = req("POST", "/validate", {"nfa": nfa_ab})
    check("NFA válido → 200", s, r, 200)
except urllib.error.HTTPError as e:
    check("NFA válido → 200", e.code, {}, 200)

invalid = {**nfa_ab, "start": "qX"}
try:
    s, r = req("POST", "/validate", {"nfa": invalid})
    check("NFA inválido → 422", s, r, 422)
except urllib.error.HTTPError as e:
    body = json.loads(e.read())
    check("NFA inválido → 422", e.code, body, 422)

# --- /examples ---
print("\n[4] Exemplos embutidos")
s, r = req("GET", "/examples")
check("GET /examples retorna dict", s, r, 200)
print(f"       Exemplos disponíveis: {list(r.keys())}")

# --- Sumário ---
print("\n" + "=" * 55)
total = PASS + FAIL
print(f"  Resultado: {PASS}/{total} passaram  {'🎉' if FAIL == 0 else '⚠️'}")
print("=" * 55 + "\n")
sys.exit(0 if FAIL == 0 else 1)
