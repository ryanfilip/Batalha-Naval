"""
docs/tabela_producoes.py
─────────────────────────
Tabela de produções da gramática da Batalha Naval PLY
"""

GRAMATICA = [
    ("CMD",         "Iniciar  Player_mode"),
    ("Iniciar",     "Posicionar  |  Ajuda  |  Reiniciar  |  Sair"),
    ("Player_mode", "PVP  |  PVC  |  Solo"),
    ("Posicionar",  "Ship  Posicionar  |  Aleatorio"),
    ("Aleatorio",   "Atirar  |  Tabuleiro  |  Reiniciar  |  Sair"),
    ("Ship",        "Coordenada  Orientacao"),
    ("Coordenada",  "id"),
    ("Orientacao",  "Horizontal  |  Vertical"),
    ("Atirar",      "Alvo"),
    ("Alvo",        "Acerto  |  Agua"),
    ("Acerto",      "Atirar  |  Tabuleiro  |  Reiniciar  |  Sair"),
    ("Ship",        "Porta_Avioes  |  Couracado  |  Destroier  |  Submarino  |  Patrulha"),
    ("Tabuleiro",   "Atirar  |  Reiniciar  |  Sair"),
    ("Ajuda",       "Iniciar  |  Reiniciar  |  Sair"),
]

ACOES = [
    ("CMD -> Iniciar  Player_mode",
     "sem_start(Player_mode.val)"),
    ("Iniciar -> Posicionar",
     "sem_place(Ship.val, Coordenada.lex, Orientacao.val)"),
    ("Iniciar -> Ajuda",
     "sem_help()"),
    ("Iniciar -> Reiniciar",
     "G.reset()"),
    ("Iniciar -> Sair",
     "sys.exit(0)"),
    ("Player_mode -> PVP | PVC | Solo",
     "Player_mode.val = token.lex"),
    ("Posicionar -> Ship  Posicionar",
     "recursão: posiciona Ship, continua para o próximo navio"),
    ("Posicionar -> Aleatorio",
     "sem_random()"),
    ("Aleatorio -> Atirar",
     "sem_shoot(Coordenada.lex)"),
    ("Aleatorio -> Tabuleiro",
     "sem_board()"),
    ("Aleatorio -> Reiniciar | Sair",
     "G.reset()  |  sys.exit(0)"),
    ("Ship -> Coordenada  Orientacao",
     "Ship.val = (Coordenada.lex, Orientacao.val)"),
    ("Coordenada -> id",
     "Coordenada.lex = id.lex   regex: [A-J](10|[1-9])"),
    ("Orientacao -> Horizontal | Vertical",
     "Orientacao.val = token.lex"),
    ("Atirar -> Alvo",
     "sem_shoot(Alvo.coord)"),
    ("Alvo -> Acerto",
     "G.consec += 1  (acerto garante novo tiro — Sequência)"),
    ("Alvo -> Agua",
     "G.switch()  (erro: passa a vez)"),
    ("Acerto -> Atirar",
     "sem_shoot(Coordenada.lex)  [recursão da Sequência de Acertos]"),
    ("Acerto -> Tabuleiro",
     "sem_board()"),
    ("Acerto -> Reiniciar | Sair",
     "G.reset()  |  sys.exit(0)"),
    ("Ship -> Porta_Avioes | Couracado | Destroier | Submarino | Patrulha",
     "Ship.val = token.lex"),
    ("Tabuleiro -> Atirar",
     "sem_shoot(Coordenada.lex)"),
    ("Tabuleiro -> Reiniciar | Sair",
     "G.reset()  |  sys.exit(0)"),
    ("Ajuda -> Iniciar",
     "sem_start(Player_mode.val)"),
    ("Ajuda -> Reiniciar | Sair",
     "G.reset()  |  sys.exit(0)"),
]


def _tabela(titulo, cabecalho, linhas, larguras):
    w_total = sum(larguras) + len(larguras) * 3 + 1
    sep = "─" * w_total
    fmt = "│ " + " │ ".join(f"{{:<{w}}}" for w in larguras) + " │"
    if titulo:
        print(f"\n  {titulo}")
    print("┌" + sep + "┐")
    print(fmt.format(*[h[:w] for h, w in zip(cabecalho, larguras)]))
    print("├" + sep + "┤")
    for row in linhas:
        print(fmt.format(*[str(v)[:w] for v, w in zip(row, larguras)]))
    print("└" + sep + "┘")


def main():
    sep = "═" * 72
    print(f"\n{sep}")
    print("  BATALHA NAVAL PLY  —  Gramática (elaborada com o professor)")
    print(sep)
    _tabela("", ["Não-terminal", "Produções"], GRAMATICA, [14, 58])

    print(f"\n{sep}")
    print("  BATALHA NAVAL PLY  —  Produções × Ações Semânticas")
    print(sep)
    _tabela("", ["Produção", "Ação Semântica"], ACOES, [46, 50])

    print()
    input(f"{sep}\n  Pressione Enter para sair...")


if __name__ == "__main__":
    main()