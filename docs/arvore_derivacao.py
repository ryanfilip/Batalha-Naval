"""
docs/arvore_derivacao.py
─────────────────────────
Árvores de derivação baseadas na gramática elaborada com o professor.

Gramática:
  CMD        -> Iniciar  Player_mode
  Iniciar    -> Posicionar | Ajuda | Reiniciar | Sair
  Player_mode-> PVP | PVC | Solo
  Posicionar -> Ship Posicionar | Aleatorio
  Aleatorio  -> Atirar | Tabuleiro | Reiniciar | Sair
  Ship       -> Coordenada Orientacao
  Coordenada -> id
  Orientacao -> Horizontal | Vertical
  Atirar     -> Alvo
  Alvo       -> Acerto | Agua
  Acerto     -> Atirar | Tabuleiro | Reiniciar | Sair
  Ship       -> Porta_Avioes | Couracado | Destroier | Submarino | Patrulha
  Tabuleiro  -> Atirar | Reiniciar | Sair
  Ajuda      -> Iniciar | Reiniciar | Sair
"""


# ════════════════════════════════════════════════════════════════
# Utilitário de impressão de árvore
# ════════════════════════════════════════════════════════════════

def node(label, *children):
    return {"label": label, "children": list(children)}

def leaf(label):
    return {"label": label, "children": []}

def print_tree(n, prefix="", is_last=True):
    connector = "└── " if is_last else "├── "
    print(prefix + connector + n["label"])
    children = n.get("children", [])
    for i, child in enumerate(children):
        ext = "    " if is_last else "│   "
        print_tree(child, prefix + ext, i == len(children) - 1)


# ════════════════════════════════════════════════════════════════
# ÁRVORE 1
# Sentença: "INICIAR PVC"  seguido de  "POSICIONAR PORTA_AVIOES B4 HORIZONTAL"
# Derivação:
#   CMD -> Iniciar Player_mode
#   Iniciar -> Posicionar
#   Posicionar -> Ship Posicionar
#   Ship -> Porta_Avioes  +  Ship -> Coordenada Orientacao
#   Coordenada -> id ('B4')  |  Orientacao -> Horizontal
#   Player_mode -> PVC
# ════════════════════════════════════════════════════════════════

tree1 = node("CMD",
    node("Iniciar",
        node("Posicionar",
            node("Ship",
                node("Ship",
                    leaf("Porta_Avioes")
                ),
                node("Coordenada",
                    leaf("id  'B4'")
                ),
                node("Orientacao",
                    leaf("Horizontal")
                ),
            ),
            node("Posicionar",
                leaf("Aleatorio  ← demais navios")
            ),
        )
    ),
    node("Player_mode",
        leaf("PVC")
    ),
)

# ════════════════════════════════════════════════════════════════
# ÁRVORE 2
# Sentença: "ATIRAR B4" com ACERTO, depois "ATIRAR C5" com ÁGUA
# Derivação:
#   Aleatorio -> Atirar
#   Atirar -> Alvo
#   Alvo -> Acerto  (HIT — acerto garante novo tiro)
#   Acerto -> Atirar  (recursão da Sequência de Acertos)
#   Atirar -> Alvo
#   Alvo -> Agua    (MISS — passa a vez)
# ════════════════════════════════════════════════════════════════

tree2 = node("Aleatorio",
    node("Atirar  'B4'",
        node("Alvo",
            node("Acerto  ← HIT",
                node("Atirar  'C5'  ← novo tiro (Sequência)",
                    node("Alvo",
                        leaf("Agua  ← MISS  -> passa a vez")
                    )
                )
            )
        )
    )
)

# ════════════════════════════════════════════════════════════════
# ÁRVORE 3
# Sentença: "INICIAR PVP" seguido de posicionamento aleatório e tiros
# Derivação completa de uma partida curta
# ════════════════════════════════════════════════════════════════

tree3 = node("CMD",
    node("Iniciar",
        node("Posicionar",
            node("Aleatorio",
                node("Atirar  'E5'",
                    node("Alvo",
                        node("Acerto  ← HIT",
                            node("Atirar  'E6'  ← Sequência",
                                node("Alvo",
                                    leaf("Agua  ← MISS  -> vez do oponente")
                                )
                            )
                        )
                    )
                )
            )
        )
    ),
    node("Player_mode",
        leaf("PVP")
    ),
)

# ════════════════════════════════════════════════════════════════
# ÁRVORE 4
# Sentença: "INICIAR SOLO"  +  "AJUDA"  seguido de reiniciar
# Mostra o ramo Ajuda da gramática
# ════════════════════════════════════════════════════════════════

tree4 = node("CMD",
    node("Iniciar",
        node("Ajuda",
            node("Reiniciar  ← volta ao início")
        )
    ),
    node("Player_mode",
        leaf("Solo")
    ),
)

# ════════════════════════════════════════════════════════════════
# ÁRVORE 5 — Anotada
# Sentença: "ATIRAR B4" (acerto) -> "ATIRAR C5" (água)
# Mostra os atributos semânticos em cada nó
# ════════════════════════════════════════════════════════════════

tree5_anot = node("Aleatorio  { sem_shoot(Coordenada.lex) }",
    node("Atirar  'B4'  { Alvo.coord = 'B4' }",
        node("Alvo  { resultado = HIT }",
            node("Acerto  { G.consec = 1 }",
                node("Atirar  'C5'  { Alvo.coord = 'C5' }  ← Sequência de Acertos",
                    node("Alvo  { resultado = MISS }",
                        leaf("Agua  { G.switch()  -> passa a vez }")
                    )
                )
            )
        )
    )
)


tree6_anot = node("CMD  { sem_start(Player_mode.val) }",
    node("Iniciar  { sem_place(Ship.val, Coordenada.lex, Orientacao.val) }",
        node("Posicionar  { Ship.val = ('B4','HORIZONTAL') }",
            node("Ship  { Ship.val = (Coordenada.lex, Orientacao.val) }",
                node("Ship  { Ship.val = 'PORTA_AVIOES' }",
                    leaf("Porta_Avioes  { token.lex = 'PORTA_AVIOES' }")
                ),
                node("Coordenada  { Coordenada.lex = 'B4' }",
                    leaf("id  'B4'")
                ),
                node("Orientacao  { Orientacao.val = 'HORIZONTAL' }",
                    leaf("Horizontal")
                ),
            ),
            node("Posicionar -> Aleatorio  { sem_random() }",
                node("Aleatorio -> Atirar  { sem_shoot('E5') }",
                    node("Alvo  { resultado = HIT }",
                        node("Acerto  { G.consec = 1 }",
                            leaf("Atirar  'F5'  ← Sequência de Acertos")
                        )
                    )
                )
            )
        )
    ),
    node("Player_mode  { Player_mode.val = 'PVC' }",
        leaf("PVC  { token.lex = 'PVC' }")
    ),
)


# ════════════════════════════════════════════════════════════════
# Main
# ════════════════════════════════════════════════════════════════

ARVORES = [
    ("INICIAR PVC  +  POSICIONAR PORTA_AVIOES B4 HORIZONTAL",
     tree1,
     "Árvore de Derivação"),

    ("ATIRAR B4 (acerto)  ->  ATIRAR C5 (água)",
     tree2,
     "Árvore de Derivação — Sequência de Acertos"),

    ("INICIAR PVP  +  ALEATORIO  +  ATIRAR E5 (acerto) -> ATIRAR E6 (água)",
     tree3,
     "Árvore de Derivação — Partida Completa"),

    ("INICIAR SOLO  +  AJUDA  +  REINICIAR",
     tree4,
     "Árvore de Derivação — Ramo Ajuda"),

    ("ATIRAR B4 (acerto)  ->  ATIRAR C5 (água)",
     tree5_anot,
     "Árvore Anotada — Sequência de Acertos"),

    ("INICIAR PVC  +  POSICIONAR  +  ATIRAR E5 (acerto)",
     tree6_anot,
     "Árvore Anotada — Partida Completa"),
]


def main():
    sep = "═" * 72
    print(f"\n{sep}")
    print("  BATALHA NAVAL PLY  —  Árvores de Derivação")
    print("  Gramática elaborada com o professor  |  Compiladores 2026/1")
    print(sep)

    for sentenca, arvore, tipo in ARVORES:
        print(f"\n  [{tipo}]")
        print(f"  Sentença: \"{sentenca}\"")
        print("  " + "─" * 68)
        print_tree(arvore, "  ")
        print()

    input(f"\n{sep}\n  Pressione Enter para sair...")


if __name__ == "__main__":
    main()