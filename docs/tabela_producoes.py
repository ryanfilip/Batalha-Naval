#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
docs/tabela_producoes.py
─────────────────────────
Exibe tabelas de referência para a apresentação do trabalho:
  1. Tokens (análise léxica — expressões regulares)
  2. Produções × Ações Semânticas — gramática POR COMANDO (o que o PLY parseia
     a cada linha digitada)
  3. Gramática da SESSÃO — fluxo da partida (elaborada com o professor),
     mostrando como ATIRAR se encadeia conforme Acerto/Água

Requisito do trabalho:
  c. Mostrar a tabela com as produções e ações semânticas.

NOTA: o modo CLASSICO foi removido. O jogo agora tem um único modo —
      Sequência de Acertos — refletido na gramática da sessão (item 3),
      onde `resultado → HIT atirar_seq` permite atirar novamente após
      acertar.
"""


# ════════════════════════════════════════════════════════════════
# 1) Tokens (Análise Léxica)
# ════════════════════════════════════════════════════════════════

# (tipo_token, padrão_ou_palavra, descrição)
TOKENS_TABLE = [
    ("SHOOT",       "ATIRAR",               "Comando de tiro"),
    ("PLACE",       "POSICIONAR",           "Posicionar navio na grade"),
    ("START",       "INICIAR",              "Iniciar uma partida"),
    ("QUIT",        "SAIR",                 "Encerrar o programa"),
    ("HORIZONTAL",  "HORIZONTAL",           "Orientação do navio"),
    ("VERTICAL",    "VERTICAL",             "Orientação do navio"),
    ("CARRIER",     "PORTA_AVIOES",         "Navio  5 células"),
    ("BATTLESHIP",  "CORACADO",             "Navio  4 células"),
    ("DESTROYER",   "DESTROYER",            "Navio  3 células"),
    ("SUBMARINE",   "SUBMARINO",            "Navio  3 células"),
    ("PATROL",      "PATRULHA",             "Navio  2 células"),
    ("PVP",         "PVP",                  "Jogador vs Jogador"),
    ("PVC",         "PVC",                  "Jogador vs CPU"),
    ("SOLO",        "SOLO",                 "Solo"),
    ("HELP",        "AJUDA",                "Exibir ajuda"),
    ("BOARD",       "TABULEIRO",            "Exibir grade"),
    ("RANDOM",      "ALEATORIO",            "Posicionamento automático"),
    ("RESTART",     "REINICIAR",            "Reiniciar jogo"),
    ("COORDINATE",  "[A-J](10|[1-9])",      "Coordenada  ex: B4, A10, J1"),
    ("ID",          "[A-Za-z_][A-Za-z0-9_]*", "Identificador genérico"),
]


# ════════════════════════════════════════════════════════════════
# 2) Produções × Ações Semânticas — gramática POR COMANDO
#    (src/parser_grammar.py + src/semantic.py)
# ════════════════════════════════════════════════════════════════
#
# Atualização: removido game_mode (CLASSICO/SEQUENCIA).
#   start_cmd → START player_mode    (apenas o tipo de partida)
#   sem_start(p[2])                  (1 argumento, não 2)
#
# (nº, produção, ação semântica, arquivo)
PRODUCTIONS_TABLE = [
    # command (1-8)
    ( 1, "command → shoot_cmd",                    "p[0] = p[1]",                          "parser_grammar.py"),
    ( 2, "command → place_cmd",                    "p[0] = p[1]",                          "parser_grammar.py"),
    ( 3, "command → start_cmd",                    "p[0] = p[1]",                          "parser_grammar.py"),
    ( 4, "command → quit_cmd",                     "p[0] = p[1]",                          "parser_grammar.py"),
    ( 5, "command → help_cmd",                     "p[0] = p[1]",                          "parser_grammar.py"),
    ( 6, "command → board_cmd",                    "p[0] = p[1]",                          "parser_grammar.py"),
    ( 7, "command → random_cmd",                   "p[0] = p[1]",                          "parser_grammar.py"),
    ( 8, "command → restart_cmd",                  "p[0] = p[1]",                          "parser_grammar.py"),
    # comandos concretos (9-16)
    ( 9, "shoot_cmd → SHOOT COORDINATE",           "p[0]=('shoot',p[2]); sem_shoot(p[2])", "semantic.py"),
    (10, "place_cmd → PLACE ship_type COORD orient","p[0]=('place',p[2..4]); sem_place(…)", "semantic.py"),
    (11, "start_cmd → START player_mode",          "p[0]=('start',p[2]); sem_start(p[2])", "semantic.py"),
    (12, "quit_cmd → QUIT",                        "sys.exit(0)",                          "parser_grammar.py"),
    (13, "help_cmd → HELP",                        "sem_help()",                           "semantic.py"),
    (14, "board_cmd → BOARD",                      "sem_board()",                          "semantic.py"),
    (15, "random_cmd → RANDOM",                    "sem_random()",                         "semantic.py"),
    (16, "restart_cmd → RESTART",                  "G.reset()",                            "game_engine.py"),
    # ship_type (17-21)
    (17, "ship_type → CARRIER",                    "p[0]='CARRIER'  (5 células)",          "parser_grammar.py"),
    (18, "ship_type → BATTLESHIP",                 "p[0]='BATTLESHIP'  (4 células)",       "parser_grammar.py"),
    (19, "ship_type → DESTROYER",                  "p[0]='DESTROYER'  (3 células)",        "parser_grammar.py"),
    (20, "ship_type → SUBMARINE",                  "p[0]='SUBMARINE'  (3 células)",        "parser_grammar.py"),
    (21, "ship_type → PATROL",                     "p[0]='PATROL'  (2 células)",           "parser_grammar.py"),
    # orientation (22-23)
    (22, "orientation → HORIZONTAL",               "p[0]='HORIZONTAL'",                    "parser_grammar.py"),
    (23, "orientation → VERTICAL",                 "p[0]='VERTICAL'",                      "parser_grammar.py"),
    # player_mode (24-26)
    (24, "player_mode → PVP",                      "p[0]='PVP'",                           "parser_grammar.py"),
    (25, "player_mode → PVC",                      "p[0]='PVC'",                           "parser_grammar.py"),
    (26, "player_mode → SOLO",                     "p[0]='SOLO'",                          "parser_grammar.py"),
]


# ════════════════════════════════════════════════════════════════
# 3) Gramática da SESSÃO — fluxo da partida (elaborada com o professor)
# ════════════════════════════════════════════════════════════════
#
# Modela a ORDEM em que os comandos são aceitos durante uma partida —
# diferente da tabela acima, que modela CADA COMANDO individualmente.
#
# Ideia original do professor:
#   Atirar -> Alvo
#   Alvo   -> Acerto | Água
#   Acerto -> Atirar | Tabuleiro | Reiniciar | Sair
#
# Versão revisada com os tokens reais do lexer/parser:
#   - "Acerto" e "Água" passam a ser HIT / MISS (resultado do sem_shoot)
#   - "Acerto -> Atirar" é a RECURSÃO que implementa a Sequência de Acertos
#     (modo único do jogo, após a remoção do CLASSICO)
#   - BOARD/RESTART/QUIT/HELP são "utilitários": podem aparecer em
#     praticamente qualquer ponto do fluxo, por isso ficam separados
#
SESSION_GRAMMAR_TABLE = [
    ("sessao → START player_mode setup atirar_seq",
     "Estrutura geral de uma partida completa"),

    ("player_mode → PVP | PVC | SOLO",
     "= Player_mode -> PVP | PVC | Solo (sem alteração)"),

    ("setup → place_cmd setup | RANDOM",
     "= Posicionar -> Ship Posicionar | Aleatorio\n"
     "(recursão = vários navios em sequência)"),

    ("place_cmd → PLACE ship_type\n  COORDINATE orientation",
     "= Ship -> Coordenada Orientacao, unindo também\n"
     "o tipo do navio (Porta_Avioes | ... | Patrulha)"),

    ("ship_type → CARRIER | BATTLESHIP |\n  DESTROYER | SUBMARINE | PATROL",
     "= Ship -> Porta_Avioes | Couraçado |\n"
     "Destroier | Submarino | Patrulha"),

    ("orientation → HORIZONTAL | VERTICAL",
     "= Orientacao -> Horizontal | Vertical (sem alteração)"),

    ("atirar_seq → SHOOT COORDINATE resultado",
     "= Atirar -> Alvo (COORDINATE já validado\n"
     "pelo léxico, no lugar de 'Coordenada -> id')"),

    ("resultado → HIT atirar_seq",
     "= Acerto -> Atirar: RECURSÃO que implementa\n"
     "a Sequência de Acertos (acerto = novo tiro)"),

    ("resultado → MISS",
     "= Alvo -> Água: erro termina a recursão\n"
     "(fim do turno)"),

    ("utilitario → BOARD | RESTART | QUIT | HELP",
     "= {Tabuleiro, Reiniciar, Sair, Ajuda}: comandos\n"
     "disponíveis a qualquer momento"),
]


# ════════════════════════════════════════════════════════════════
# Utilitário de impressão
# ════════════════════════════════════════════════════════════════

def _table(headers: list[str], rows: list[tuple], widths: list[int]) -> None:
    total = sum(widths) + len(widths) * 3 + 1
    sep   = "─" * total
    fmt   = "│ " + " │ ".join(f"{{:<{w}}}" for w in widths) + " │"

    print("┌" + sep + "┐")
    print(fmt.format(*[h[:w] for h, w in zip(headers, widths)]))
    print("├" + sep + "┤")
    for row in rows:
        # Suporta células com múltiplas linhas (\n)
        cols = [str(v).split("\n") for v in row]
        n_lines = max(len(c) for c in cols)
        for i in range(n_lines):
            line_vals = []
            for c, w in zip(cols, widths):
                txt = c[i] if i < len(c) else ""
                line_vals.append(txt[:w])
            print(fmt.format(*line_vals))
        print("├" + sep + "┤" if row != rows[-1] else "└" + sep + "┘")


# ════════════════════════════════════════════════════════════════
# Main
# ════════════════════════════════════════════════════════════════

def main():
    sep = "═" * 74

    # ── Tabela 1: Tokens ─────────────────────────────────────
    print(f"\n{sep}")
    print("  BATALHA NAVAL PLY  —  Tabela de Tokens (Análise Léxica)")
    print(f"  Arquivo: src/lexer.py")
    print(sep)
    _table(
        ["Tipo Token",    "Palavra / Padrão",          "Descrição"],
        TOKENS_TABLE,
        [14,              28,                           28],
    )

    # ── Tabela 2: Produções × Ações Semânticas (por comando) ─
    print(f"\n{sep}")
    print("  BATALHA NAVAL PLY  —  Produções × Ações Semânticas (por comando)")
    print(f"  Arquivo: src/parser_grammar.py  +  src/semantic.py")
    print(sep)
    _table(
        ["#",  "Produção",                              "Ação Semântica",          "Arquivo"],
        PRODUCTIONS_TABLE,
        [3,    44,                                      38,                        18],
    )

    # ── Tabela 3: Gramática da Sessão (fluxo da partida) ─────
    print(f"\n{sep}")
    print("  BATALHA NAVAL PLY  —  Gramática da Sessão (fluxo da partida)")
    print("  Elaborada com o professor — modo único: Sequência de Acertos")
    print(sep)
    _table(
        ["Produção",                                              "Equivalência / Observação"],
        SESSION_GRAMMAR_TABLE,
        [48,                                                       58],
    )

    print()
    input(f"{sep}\n  Pressione Enter para sair...")


if __name__ == '__main__':
    main()
