#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
semantic.py  —  Ações Semânticas (Batalha Naval PLY)
─────────────────────────────────────────────────────
Implementa o comportamento de cada comando reconhecido pelo parser.
Cada função sem_*() é chamada diretamente dentro das regras gramaticais
de parser_grammar.py (Tradução Dirigida pela Sintaxe).

Funções exportadas:
  sem_start(gtype)                 ← p_start_cmd
  sem_place(ship, coord, orient)   ← p_place_cmd
  sem_random()                     ← p_random_cmd
  sem_shoot(coord)                 ← p_shoot_cmd
  sem_board()                      ← p_board_cmd
  sem_help()                       ← p_help_cmd

ATUALIZAÇÕES:
  - sem_start(gtype): um único parâmetro (sem game_mode/CLASSICO).
  - sem_shoot: acerto SEMPRE garante novo tiro (Sequência de Acertos é
    o único modo). Corresponde à "Gramática da Sessão":
        atirar_seq → SHOOT COORDINATE resultado
        resultado  → HIT atirar_seq   (Acerto → Atirar, recursivo)
                   | MISS              (Água → fim do turno)
  - SOLO: o jogador sempre atira na grade do oponente (G.opponent),
    inclusive no modo SOLO — onde existe uma grade "CPU" gerada
    automaticamente, mas que NUNCA atira de volta.
  - sem_board / TABULEIRO: exibe os dois tabuleiros lado a lado.
    Após cada tiro (sem_shoot), os dois tabuleiros também são
    exibidos automaticamente.
"""

import random

from .game_engine import (
    G, Board,
    SHIPS_CONFIG, SHIP_ORDER, TOKEN_TO_KW,
    display_side_by_side,
)

# ════════════════════════════════════════════════════════════════
# Helpers internos
# ════════════════════════════════════════════════════════════════

def _prompt_setup() -> None:
    """
    Exibe o próximo passo do posicionamento.
    Quando todos terminam, inicia a partida automaticamente.
    """
    player = G.setup_player()

    if player is None:
        # Todos os jogadores posicionaram → inicia a batalha
        G.start_play()
        print("\n  ✅ Posicionamento concluído! A batalha começa agora.")
        print(f"  🎯 Turno de {G.cur}  →  ATIRAR <COORD>   (ex: ATIRAR B4)")
        if G.cur == 'CPU':
            _cpu_turn()
        return

    ship = G.current_ship()
    cfg  = SHIPS_CONFIG[ship]
    kw   = TOKEN_TO_KW[ship]

    # Em PVP, avisa para passar o computador ao trocar de jogador
    if G.gtype == 'PVP' and G.ss_idx == 0 and G.sp_idx > 0:
        print(f"\n  ─────────── Passe o computador para {player} ───────────")

    print(f"\n  [{player}] Posicione: {cfg['label']} (tamanho {cfg['size']})")
    print(f"  → POSICIONAR {kw} <COORD> <HORIZONTAL|VERTICAL>")
    print(f"     ex: POSICIONAR {kw} A1 HORIZONTAL")
    print(f"  → ALEATORIO   (posiciona todos os navios restantes automaticamente)")
    print(f"  → TABULEIRO   (ver posicionamento atual)")


def _show_both_boards(player: str) -> None:
    """Exibe os dois tabuleiros lado a lado: o próprio e os tiros no inimigo."""
    opp   = G.opponent(player)
    left  = G.boards[player].render_lines(title=player)
    right = G.boards[opp].render_shots_lines(title="SEUS TIROS")
    print()
    display_side_by_side(left, right)
    print()


def _show_result(player: str, coord: str, result: str,
                 sunk: str | None, board: Board) -> None:
    """Exibe o resultado de um tiro e verifica vitória."""
    if result == 'MISS':
        print(f"  💧 ÁGUA! Tiro em {coord} → errou.")
        if G.consec > 0:
            print(f"     Sequência de {G.consec} acerto(s) encerrada.")
        G.consec = 0

    else:  # HIT
        if sunk:
            label = SHIPS_CONFIG[sunk]['label']
            print(f"  🔥 ACERTO! {coord} → {label} AFUNDADO!")
        else:
            print(f"  💥 ACERTO em {coord}!")

        if board.all_sunk():
            G.phase  = 'DONE'
            G.winner = player
            emoji  = '🏆' if player != 'CPU' else '💀'
            sufixo = '' if player != 'CPU' else ' (CPU venceu…)'
            print(f"\n  {emoji} VITÓRIA{sufixo}! {player} afundou todos os navios!")
            print(f"     Use REINICIAR para jogar novamente.")


def _cpu_turn() -> None:
    """
    CPU executa sua(s) jogada(s) automaticamente.

    Único modo (Sequência de Acertos): a CPU continua atirando
    enquanto acertar; erra → passa a vez para o jogador.
    """
    if G.phase != 'PLAYING' or G.cur != 'CPU':
        return

    player_board = G.boards[G.opponent('CPU')]
    print(f"\n  🤖 CPU está jogando...")

    while G.phase == 'PLAYING' and G.cur == 'CPU':
        available = [
            Board.idx_to_coord(r, c)
            for r in range(10) for c in range(10)
            if player_board.shots[r][c] == '~'
        ]
        if not available:
            break

        coord  = random.choice(available)
        result, sunk = player_board.receive_shot(coord)

        if result == 'MISS':
            print(f"  🤖 CPU → {coord}: ÁGUA")
            G.switch()          # CPU errou → passa a vez

        elif result == 'HIT':
            if sunk:
                print(f"  🤖 CPU → {coord}: ACERTO! "
                      f"{SHIPS_CONFIG[sunk]['label']} afundado!")
            else:
                print(f"  🤖 CPU → {coord}: ACERTO!")

            if player_board.all_sunk():
                G.phase  = 'DONE'
                G.winner = 'CPU'
                print(f"\n  💀 CPU venceu a batalha!")
                print(f"     Use REINICIAR para tentar novamente.")
                return

            # Acerto garante novo tiro da CPU (Sequência); loop continua

    if G.phase == 'PLAYING' and G.cur != 'CPU':
        print(f"\n  → Turno de {G.cur}  →  ATIRAR <COORD>")


# ════════════════════════════════════════════════════════════════
# Ações Semânticas (chamadas pelo parser)
# ════════════════════════════════════════════════════════════════

def sem_start(gtype: str) -> None:
    """
    INICIAR <gtype>
    Produção: start_cmd → START player_mode
    """
    if G.phase != 'IDLE':
        print("  Jogo em andamento. Use REINICIAR para recomeçar.")
        return

    G.init(gtype)

    gtype_str = {'PVP': 'Jogador vs Jogador',
                 'PVC': 'Jogador vs CPU',
                 'SOLO': 'Solo (sem oponente ativo)'}[gtype]

    print(f"\n  🚢 Jogo iniciado!")
    print(f"     Tipo: {gtype_str}  |  Modo: Sequência de Acertos")
    print(f"\n  📋 Fase de posicionamento dos navios")
    _prompt_setup()


def sem_place(ship: str, coord: str, orient: str) -> None:
    """
    POSICIONAR <ship> <coord> <orient>
    Produção: place_cmd → PLACE ship_type COORDINATE orientation
    """
    if G.phase == 'IDLE':
        print("  Inicie o jogo: INICIAR <PVP|PVC|SOLO>")
        return
    if G.phase != 'SETUP':
        print("  Fase de posicionamento já encerrada!")
        return

    player   = G.setup_player()
    expected = G.current_ship()

    if ship != expected:
        print(f"  ❌ Posicione {SHIPS_CONFIG[expected]['label']} primeiro! "
              f"(tentou: {SHIPS_CONFIG[ship]['label']})")
        _prompt_setup()
        return

    board = G.boards[player]
    ok, msg = board.place(ship, coord, orient)

    if ok:
        print(f"  ✅ {SHIPS_CONFIG[ship]['label']} → {coord} {orient}")
        G.advance()
        _prompt_setup()
    else:
        print(f"  ❌ {msg}")
        _prompt_setup()


def sem_random() -> None:
    """
    ALEATORIO — posiciona todos os navios restantes do jogador atual.
    Produção: random_cmd → RANDOM
    """
    if G.phase != 'SETUP':
        print("  Posicionamento aleatório só disponível na fase de setup.")
        return

    player = G.setup_player()
    if player is None:
        print("  Todos os navios já foram posicionados.")
        return

    board      = G.boards[player]
    ships_left = SHIP_ORDER[G.ss_idx:]

    print(f"\n  🎲 [{player}] Posicionamento aleatório:")
    for ship in ships_left:
        placed = False
        for _ in range(10_000):
            r      = random.randint(0, 9)
            c      = random.randint(0, 9)
            coord  = Board.idx_to_coord(r, c)
            orient = random.choice(['HORIZONTAL', 'VERTICAL'])
            ok, _  = board.place(ship, coord, orient)
            if ok:
                placed = True
                cfg = SHIPS_CONFIG[ship]
                print(f"     {cfg['label']:15} → {coord:3} {orient}")
                break
        if not placed:
            print(f"  ❌ Não foi possível posicionar {SHIPS_CONFIG[ship]['label']}")

    # Marca todos os navios como posicionados e avança ao próximo jogador
    G.sp_idx += 1
    G.ss_idx  = 0
    _prompt_setup()


def sem_shoot(coord: str) -> None:
    """
    ATIRAR <coord>
    Produção: shoot_cmd → SHOOT COORDINATE

    Único modo de jogo — Sequência de Acertos:
      Acerto (HIT)  → joga de novo (G.consec += 1)
      Água   (MISS) → passa a vez (G.switch())

    O jogador SEMPRE atira na grade do oponente (G.opponent), inclusive
    no modo SOLO, onde a grade "CPU" nunca atira de volta.
    """
    if G.phase == 'IDLE':
        print("  Inicie o jogo: INICIAR <PVP|PVC|SOLO>")
        return
    if G.phase == 'SETUP':
        print("  Termine de posicionar os navios antes de atirar!")
        return
    if G.phase == 'DONE':
        print(f"  Jogo encerrado. Vencedor: {G.winner}. Use REINICIAR.")
        return

    current = G.cur
    target  = G.opponent(current)        # sempre o inimigo, mesmo no SOLO
    board   = G.boards[target]

    result, sunk = board.receive_shot(coord)

    if result == 'REPEAT':
        print(f"  ⚠️  Já atirado em {coord}! Escolha outra posição.")
        return

    _show_result(current, coord, result, sunk, board)

    if G.phase == 'DONE':
        _show_both_boards(current)
        return

    # ── Controle de turnos (Sequência de Acertos) ─────────────
    if result == 'MISS':
        if G.gtype != 'SOLO':
            G.switch()
            print(f"  → Turno de {G.cur}.")

    else:  # HIT — acerto sempre garante novo tiro
        G.consec += 1
        print(f"  🎯 Sequência: {G.consec} acerto(s). Continue atirando!")

    # Exibe os dois tabuleiros atualizados após cada tiro
    _show_both_boards(current)

    # CPU joga depois de exibir o resultado do jogador
    if G.phase == 'PLAYING' and G.cur == 'CPU':
        _cpu_turn()
        _show_both_boards(G.opponent('CPU'))


def sem_board() -> None:
    """
    TABULEIRO — exibe os dois tabuleiros lado a lado.
    Produção: board_cmd → BOARD
    """
    if G.phase == 'IDLE':
        print("  Nenhum jogo em andamento.")
        return

    if G.phase == 'SETUP':
        player = G.setup_player()
        if player and player in G.boards:
            G.boards[player].display(title=f"Posicionamento – {player}")

    elif G.phase in ('PLAYING', 'DONE'):
        p = G.cur or G.players[0]
        _show_both_boards(p)


def sem_help() -> None:
    """
    AJUDA — exibe os comandos disponíveis.
    Produção: help_cmd → HELP
    """
    print("""
  ╔══════════════════════════════════════════════════════════╗
  ║           BATALHA NAVAL  —  Comandos PLY                 ║
  ╠══════════════════════════════════════════════════════════╣
  ║  INICIAR <TIPO>                                          ║
  ║    TIPO: PVP | PVC | SOLO                                ║
  ║    Modo único: Sequência de Acertos                      ║
  ║      (acerto sempre garante novo tiro)                   ║
  ║                                                          ║
  ║  POSICIONAR <NAVIO> <COORD> <HORIZONTAL|VERTICAL>        ║
  ║    Navios:  PORTA_AVIOES (5)   CORACADO  (4)             ║
  ║             DESTROYER    (3)   SUBMARINO (3)             ║
  ║             PATRULHA     (2)                             ║
  ║    Coord:   A1 … J10  (coluna A-J, linha 1-10)           ║
  ║    HORIZONTAL = esquerda→direita                         ║
  ║    VERTICAL   = cima→baixo                               ║
  ║                                                          ║
  ║  ALEATORIO  → posiciona navios restantes (auto)          ║
  ║  ATIRAR <C> → atira em coordenada   ex: ATIRAR B4        ║
  ║  TABULEIRO  → exibe os dois tabuleiros lado a lado       ║
  ║  REINICIAR  → reinicia o jogo                            ║
  ║  AJUDA      → esta mensagem                              ║
  ║  SAIR       → encerra o programa                         ║
  ╠══════════════════════════════════════════════════════════╣
  ║  Legenda: ~=água  O=erro  X=acerto                       ║
  ║    P=porta-aviões   C=couraçado   D=destroyer            ║
  ║    S=submarino      T=patrulha                           ║
  ╚══════════════════════════════════════════════════════════╝
""")
