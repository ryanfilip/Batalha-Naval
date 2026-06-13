#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
docs/arvore_derivacao.py
─────────────────────────
Exibe árvores de derivação e árvores anotadas (com valores semânticos)
para os principais comandos da linguagem Batalha Naval PLY.

Requisito do trabalho:
  d. Mostrar um exemplo de uma árvore de derivação e de uma árvore
     de derivação anotada de uma sentença aceita pela linguagem.

ATUALIZAÇÃO:
  - Modo CLASSICO removido. "INICIAR CLASSICO PVC" → "INICIAR PVC"
    (start_cmd → START player_mode, sem game_mode)
  - Adicionada a "Árvore da Sessão", baseada na gramática elaborada
    com o professor:
        atirar_seq → SHOOT COORDINATE resultado
        resultado  → HIT atirar_seq   (Acerto → Atirar, recursivo)
                   | MISS              (Água → fim do turno)
    que é exatamente a regra de Sequência de Acertos (modo único do jogo).
"""


# ════════════════════════════════════════════════════════════════
# Estrutura de árvore (dicionário simples)
# ════════════════════════════════════════════════════════════════

def node(label: str, *children) -> dict:
    return {'label': label, 'children': list(children)}

def leaf(label: str) -> dict:
    return {'label': label, 'children': []}


def print_tree(n: dict, prefix: str = "", is_last: bool = True) -> None:
    connector = "└── " if is_last else "├── "
    print(prefix + connector + n['label'])
    children = n.get('children', [])
    for i, child in enumerate(children):
        ext = "    " if is_last else "│   "
        print_tree(child, prefix + ext, i == len(children) - 1)


# ════════════════════════════════════════════════════════════════
# ÁRVORES DE DERIVAÇÃO — gramática POR COMANDO (sem anotação)
# ════════════════════════════════════════════════════════════════

# ── Sentença: "ATIRAR B4" ─────────────────────────────────────
tree_atirar = node(
    "command",
    node("shoot_cmd",
         leaf("SHOOT"),
         leaf("COORDINATE  'B4'"),
    )
)

# ── Sentença: "POSICIONAR PORTA_AVIOES A1 HORIZONTAL" ─────────
tree_posicionar = node(
    "command",
    node("place_cmd",
         leaf("PLACE"),
         node("ship_type",
              leaf("CARRIER  ← 'PORTA_AVIOES'"),
         ),
         leaf("COORDINATE  'A1'"),
         node("orientation",
              leaf("HORIZONTAL"),
         ),
    )
)

# ── Sentença: "INICIAR PVC"  (sem game_mode — CLASSICO removido) ──
tree_iniciar = node(
    "command",
    node("start_cmd",
         leaf("START"),
         node("player_mode",
              leaf("PVC"),
         ),
    )
)

# ── Sentença: "POSICIONAR SUBMARINO E5 VERTICAL" ──────────────
tree_submarino = node(
    "command",
    node("place_cmd",
         leaf("PLACE"),
         node("ship_type",
              leaf("SUBMARINE  ← 'SUBMARINO'"),
         ),
         leaf("COORDINATE  'E5'"),
         node("orientation",
              leaf("VERTICAL"),
         ),
    )
)


# ════════════════════════════════════════════════════════════════
# ÁRVORES ANOTADAS (com valores semânticos em cada nó)
# ════════════════════════════════════════════════════════════════

# ── Anotada: "ATIRAR B4" ──────────────────────────────────────
tree_atirar_anot = node(
    "command  { p[0] = ('shoot', 'B4') }",
    node("shoot_cmd  { p[0] = ('shoot', 'B4');  chama: sem_shoot('B4') }",
         leaf("SHOOT       { p[1] = 'SHOOT'  (token SHOOT, valor 'ATIRAR') }"),
         leaf("COORDINATE  { p[2] = 'B4' }"),
    )
)

# ── Anotada: "POSICIONAR PORTA_AVIOES A1 HORIZONTAL" ──────────
tree_posicionar_anot = node(
    "command  { p[0] = ('place', 'CARRIER', 'A1', 'HORIZONTAL') }",
    node("place_cmd  { p[0] = ('place','CARRIER','A1','HORIZONTAL');\n"
         "             │         chama: sem_place('CARRIER','A1','HORIZONTAL') }",
         leaf("PLACE      { p[1] = 'PLACE' }"),
         node("ship_type  { p[0] = 'CARRIER' }",
              leaf("CARRIER    { p[1] = 'CARRIER'  ← lexema 'PORTA_AVIOES' }"),
         ),
         leaf("COORDINATE { p[3] = 'A1' }"),
         node("orientation { p[0] = 'HORIZONTAL' }",
              leaf("HORIZONTAL { p[4] = 'HORIZONTAL' }"),
         ),
    )
)

# ── Anotada: "INICIAR PVP"  (sem game_mode) ───────────────────
tree_iniciar_anot = node(
    "command  { p[0] = ('start', 'PVP') }",
    node("start_cmd  { p[0] = ('start','PVP');\n"
         "             │         chama: sem_start('PVP') }",
         leaf("START        { p[1] = 'START' }"),
         node("player_mode  { p[0] = 'PVP' }",
              leaf("PVP          { p[2] = 'PVP' }"),
         ),
    )
)


# ════════════════════════════════════════════════════════════════
# ÁRVORE DA SESSÃO — gramática elaborada com o professor
# ════════════════════════════════════════════════════════════════
#
#   atirar_seq → SHOOT COORDINATE resultado
#   resultado  → HIT atirar_seq      (Acerto → Atirar, RECURSIVO)
#              | MISS                 (Água → fim do turno)
#
# Equivalente ao original:
#   Atirar -> Alvo
#   Alvo   -> Acerto | Água
#   Acerto -> Atirar | ...
#
# Exemplo: o jogador joga "ATIRAR B4" (ACERTO) e em seguida "ATIRAR C5"
# (ÁGUA). A recursão em `resultado → HIT atirar_seq` é o que garante o
# novo tiro após o acerto — ou seja, é a Sequência de Acertos
# representada DIRETAMENTE na gramática.
#

tree_sessao_atirar = node(
    "atirar_seq   (1ª jogada: ATIRAR B4)",
    leaf("SHOOT"),
    leaf("COORDINATE  'B4'"),
    node("resultado",
         leaf("HIT   ← acerto em B4"),
         node("atirar_seq   (2ª jogada: ATIRAR C5)",
              leaf("SHOOT"),
              leaf("COORDINATE  'C5'"),
              node("resultado",
                   leaf("MISS  ← água em C5  →  fim do turno"),
              ),
         ),
    )
)

# ── Versão anotada da árvore da sessão ────────────────────────
tree_sessao_atirar_anot = node(
    "atirar_seq  { cod = 'sem_shoot(B4)' || cod(resultado) }",
    leaf("SHOOT       { lex = 'ATIRAR' }"),
    leaf("COORDINATE  { lex = 'B4' }"),
    node("resultado  { resultado = HIT → cod = cod(atirar_seq2) }",
         leaf("HIT   { sem_shoot('B4') retornou HIT;  G.consec += 1 }"),
         node("atirar_seq2  { cod = 'sem_shoot(C5)' || cod(resultado2) }",
              leaf("SHOOT       { lex = 'ATIRAR' }"),
              leaf("COORDINATE  { lex = 'C5' }"),
              node("resultado2  { resultado2 = MISS → fim da recursão }",
                   leaf("MISS  { sem_shoot('C5') retornou MISS;  G.switch() }"),
              ),
         ),
    )
)


# ════════════════════════════════════════════════════════════════
# Main
# ════════════════════════════════════════════════════════════════

DERIVATION_TREES = [
    ("ATIRAR B4",                              tree_atirar),
    ("POSICIONAR PORTA_AVIOES A1 HORIZONTAL",  tree_posicionar),
    ("INICIAR PVC",                            tree_iniciar),
    ("POSICIONAR SUBMARINO E5 VERTICAL",       tree_submarino),
]

ANNOTATED_TREES = [
    ("ATIRAR B4",                              tree_atirar_anot),
    ("POSICIONAR PORTA_AVIOES A1 HORIZONTAL",  tree_posicionar_anot),
    ("INICIAR PVP",                            tree_iniciar_anot),
]

SESSION_TREES = [
    ("Sessão: ATIRAR B4 (acerto) → ATIRAR C5 (água)",       tree_sessao_atirar),
    ("Sessão (anotada)",                                    tree_sessao_atirar_anot),
]


def main():
    sep = "═" * 72

    print(f"\n{sep}")
    print("  BATALHA NAVAL PLY  —  Árvores de Derivação")
    print("  Trabalho P2  —  Compiladores 2026/1")
    print(sep)

    print("\n\n  ┌─── PARTE 1: Árvores de Derivação (gramática por comando) ──┐\n")
    for cmd, tree in DERIVATION_TREES:
        print(f"  Sentença: \"{cmd}\"")
        print("  " + "─" * 60)
        print_tree(tree, "  ")
        print()

    print(f"\n{sep}")
    print("\n\n  ┌─── PARTE 2: Árvores de Derivação Anotadas ─────────────────┐\n")
    for cmd, tree in ANNOTATED_TREES:
        print(f"  Sentença: \"{cmd}\"")
        print("  " + "─" * 60)
        print_tree(tree, "  ")
        print()

    print(f"\n{sep}")
    print("\n\n  ┌─── PARTE 3: Árvore da Sessão — Sequência de Acertos ───────┐\n")
    print("  Gramática (elaborada com o professor):")
    print("    atirar_seq → SHOOT COORDINATE resultado")
    print("    resultado  → HIT atirar_seq   (Acerto → Atirar, recursivo)")
    print("               | MISS              (Água → fim do turno)\n")
    for cmd, tree in SESSION_TREES:
        print(f"  {cmd}")
        print("  " + "─" * 60)
        print_tree(tree, "  ")
        print()

    input(f"\n{sep}\n  Pressione Enter para sair...")


if __name__ == '__main__':
    main()
