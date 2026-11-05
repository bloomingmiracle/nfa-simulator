# Simulador de AFN (NFA)
**Linguagens Formais e Computabilidade – Projeto 01**
Grupo: LTD-UFPB | Prof. Andrei Formiga

---

## O que o projeto faz

Simula Autômatos Finitos Não-Determinísticos (AFN / NFA) com suporte a **ε-transições**.  
Para uma cadeia de entrada, o simulador:

1. Calcula o **ε-fecho** do estado inicial
2. Para cada símbolo, executa **move** + **ε-fecho**
3. Registra um **trace** passo a passo
4. Aceita se algum estado ativo final for de aceitação

---

## Estrutura de arquivos

```
nfa_simulator/
├── nfa.py              # Motor NFA em Python (ε-fecho, move, simulate)
├── app.py              # Servidor Flask (API REST)
├── exemplo.json        # NFA exemplo: aceita cadeias terminadas em 'ab'
├── exemplo_epsilon.json # NFA com ε-transições
├── test_api.py         # Testes da API (12 casos)
└── README.md           # Este arquivo
```

A interface visual (HTML/JS com vis.js) está disponível como artifact no claude.ai.

---

## Como rodar

### 1 — Só o motor Python (linha de comando)

```bash
python nfa.py exemplo.json aab          # → ACEITA
python nfa.py exemplo.json ba           # → REJEITA
python nfa.py exemplo_epsilon.json aaa  # → ACEITA (ε-transições)
```

### 2 — Servidor Flask (API)

```bash
# Instalar dependências (uma vez)
pip install flask flask-cors

# Iniciar servidor
python app.py
# → http://localhost:5000
```

Endpoints:

| Método | Rota | O que faz |
|--------|------|-----------|
| GET | `/` | Info da API |
| POST | `/simulate` | Simula NFA em cadeia |
| POST | `/validate` | Valida definição de NFA |
| GET | `/examples` | Lista exemplos embutidos |
| GET | `/examples/<nome>` | Retorna um exemplo pelo nome |

### 3 — Testar a API

Com o servidor rodando:
```bash
python test_api.py   # 12/12 ✅
```

Exemplo de chamada curl:
```bash
curl -X POST http://localhost:5000/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "nfa": {
      "states": ["q0","q1","q2"],
      "alphabet": ["a","b"],
      "start": "q0",
      "accept": ["q2"],
      "transitions": {
        "q0": {"a": ["q0","q1"], "b": ["q0"]},
        "q1": {"b": ["q2"]},
        "q2": {}
      }
    },
    "input": "aab"
  }'
```

---

## Formato JSON do NFA

```json
{
  "states":      ["q0", "q1", "q2"],
  "alphabet":    ["a", "b"],
  "start":       "q0",
  "accept":      ["q2"],
  "transitions": {
    "q0": { "a": ["q0", "q1"], "b": ["q0"] },
    "q1": { "b": ["q2"] },
    "q2": {}
  }
}
```

Para ε-transições, use `"ε"` como símbolo:
```json
"q0": { "ε": ["q1", "q2"] }
```

---

## Conceitos-chave

**ε-fecho** (`epsilon_closure`): dado um conjunto de estados, retorna todos os estados alcançáveis seguindo ε-transições recursivamente (incluindo os originais).

**Move** (`move`): dado um conjunto de estados e um símbolo, retorna todos os estados alcançáveis lendo esse símbolo.

**Simulação**: alterna `move` + `ε-fecho` para cada símbolo da entrada. Aceita se a interseção entre estados ativos finais e estados de aceitação for não-vazia.
