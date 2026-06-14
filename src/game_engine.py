#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
game_engine.py
──────────────
Motor do jogo Batalha Naval: grade, navios e estado da partida.

Responsabilidade:
  - Board   : representa a grade 10×10 de um jogador
  - GameState : controla fases (IDLE → SETUP → PLAYING → DONE)

Não contém lógica de compilador (lexer/parser).
"""

import random


SHIPS_CONFIG: dict[str, dict] = {
    'CARRIER':    {'size': 5, 'sym': 'P', 'label': 'Porta-Aviões'},
    'BATTLESHIP': {'size': 4, 'sym': 'C', 'label': 'Couraçado'},
    'DESTROYER':  {'size': 3, 'sym': 'D', 'label': 'Destroyer'},
    'SUBMARINE':  {'size': 3, 'sym': 'S', 'label': 'Submarino'},
    'PATROL':     {'size': 2, 'sym': 'T', 'label': 'Patrulha'},
}

# Ordem de posicionamento (tamanho decrescente)
SHIP_ORDER: list[str] = ['CARRIER', 'BATTLESHIP', 'DESTROYER', 'SUBMARINE', 'PATROL']

# Palavra digitada pelo usuário → tipo do token PLY
SHIP_KEYWORDS: dict[str, str] = {
    'PORTA_AVIOES': 'CARRIER',
    'CORACADO':     'BATTLESHIP',
    'DESTROYER':    'DESTROYER',
    'SUBMARINO':    'SUBMARINE',
    'PATRULHA':     'PATROL',
}

TOKEN_TO_KW: dict[str, str] = {v: k for k, v in SHIP_KEYWORDS.items()}


# ════════════════════════════════════════════════════════════════
# Board — Grade 10×10 de um jogador
# ════════════════════════════════════════════════════════════════

class Board:
    COLS = 'ABCDEFGHIJ'

    def __init__(self):
        self.grid: list[list[str]]  = [['~'] * 10 for _ in range(10)]
        self.shots: list[list[str]] = [['~'] * 10 for _ in range(10)]
        self.ships: dict[str, list] = {}


    @staticmethod
    def coord_to_idx(coord: str) -> tuple[int, int]:
        """'B4' → (row=3, col=1)"""
        return int(coord[1:]) - 1, ord(coord[0]) - ord('A')

    @staticmethod
    def idx_to_coord(r: int, c: int) -> str:
        return chr(ord('A') + c) + str(r + 1)


    def place(self, ship_key: str, coord: str, orientation: str) -> tuple[bool, str]:
        """
        Posiciona um navio na grade.
        Retorna (ok: bool, mensagem: str).

        HORIZONTAL → cresce pela coluna (esquerda → direita)
        VERTICAL   → cresce pela linha  (cima → baixo)
        A coordenada informada é sempre o canto superior-esquerdo do navio.
        """
        size = SHIPS_CONFIG[ship_key]['size']
        sym  = SHIPS_CONFIG[ship_key]['sym']
        r0, c0 = self.coord_to_idx(coord)
        cells: list[tuple[int, int]] = []

        for i in range(size):
            r = r0 + (i if orientation == 'VERTICAL'   else 0)
            c = c0 + (i if orientation == 'HORIZONTAL' else 0)
            if not (0 <= r < 10 and 0 <= c < 10):
                return False, "Navio fora dos limites da grade (A–J, 1–10)!"
            if self.grid[r][c] != '~':
                return False, f"Posição {self.idx_to_coord(r, c)} já está ocupada!"
            cells.append((r, c))

        for r, c in cells:
            self.grid[r][c] = sym
        self.ships[ship_key] = list(cells)
        return True, "OK"

    # ── Receber tiro ──────────────────────────────────────────

    def receive_shot(self, coord: str) -> tuple[str, str | None]:
        """
        Processa um tiro na coordenada.
        Retorna ('HIT' | 'MISS' | 'REPEAT', nome_do_navio_afundado_ou_None).
        """
        r, c = self.coord_to_idx(coord)

        if self.shots[r][c] != '~':
            return 'REPEAT', None

        cell = self.grid[r][c]
        if cell in ('~', 'O'):
            self.grid[r][c] = self.shots[r][c] = 'O'
            return 'MISS', None

        self.grid[r][c] = self.shots[r][c] = 'X'
        sunk = None
        for sk, cells in self.ships.items():
            if (r, c) in cells:
                cells.remove((r, c))
                if not cells:
                    sunk = sk    
                break
        return 'HIT', sunk

    def all_sunk(self) -> bool:
        return all(not cells for cells in self.ships.values())


    def display(self, hide_ships: bool = False, title: str = '') -> None:
        if title:
            print(f"\n  ── {title} ──")
        print("       " + " ".join(self.COLS))   # espaço simples entre colunas
        print("     ╔" + "═" * 21 + "╗")
        for r in range(10):
            row = [
                '~' if (hide_ships and self.grid[r][c] not in ('~', 'O', 'X'))
                else self.grid[r][c]
                for c in range(10)
            ]
            print(f"  {r + 1:2d} ║ {' '.join(row)} ║")
        print("     ╚" + "═" * 21 + "╝")

    def display_shots(self, title: str = '') -> None:
        if title:
            print(f"\n  ── {title} ──")
        print("       " + " ".join(self.COLS))  
        print("     ╔" + "═" * 21 + "╗")
        for r in range(10):
            print(f"  {r + 1:2d} ║ {' '.join(self.shots[r])} ║")
        print("     ╚" + "═" * 21 + "╝")


    def render_lines(self, hide_ships: bool = False, title: str = '') -> list[str]:
        """Renderiza a grade real como lista de strings (para exibição lado a lado)."""
        lines = []
        lines.append(f"{'── ' + title + ' ──':^27}" if title else ' ' * 27)
        lines.append(f"      {' '.join(self.COLS):<21}")    
        lines.append(f"    ┌{'─' * 21}┐")
        for r in range(10):
            row = [
                '~' if (hide_ships and self.grid[r][c] not in ('~', 'O', 'X'))
                else self.grid[r][c]
                for c in range(10)
            ]
            lines.append(f" {r + 1:2d} │ {' '.join(row)} │")
        lines.append(f"    └{'─' * 21}┘")
        return lines

    def render_shots_lines(self, title: str = '') -> list[str]:
        """Renderiza apenas os tiros como lista de strings (para exibição lado a lado)."""
        lines = []
        lines.append(f"{'── ' + title + ' ──':^27}" if title else ' ' * 27)
        lines.append(f"      {' '.join(self.COLS):<21}")    # 6 + 21 = 27 chars
        lines.append(f"    ┌{'─' * 21}┐")
        for r in range(10):
            lines.append(f" {r + 1:2d} │ {' '.join(self.shots[r])} │")
        lines.append(f"    └{'─' * 21}┘")
        return lines


def display_side_by_side(left: list[str], right: list[str], gap: int = 4) -> None:
    """Exibe dois tabuleiros (listas de linhas) lado a lado no terminal."""
    for l, r in zip(left, right):
        print(f"{l:<27}{' ' * gap}{r}")


# ════════════════════════════════════════════════════════════════
# GameState — Estado global da partida
# ════════════════════════════════════════════════════════════════

class GameState:
    """
    Máquina de estados da partida:
      IDLE → SETUP → PLAYING → DONE

    Único modo de jogo: Sequência de Acertos (acerto garante novo tiro).
    Veja docs/arvore_derivacao.py / tabela_producoes.py — "Gramática da
    Sessão": resultado → HIT atirar_seq | MISS.
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.gtype:   str | None = None     # 'PVP' | 'PVC' | 'SOLO'
        self.phase:   str        = 'IDLE'   # IDLE | SETUP | PLAYING | DONE
        self.players: list[str]       = []
        self.boards:  dict[str, Board] = {}
        self.sp_idx:  int = 0               # índice do jogador em setup
        self.ss_idx:  int = 0               # índice do navio em setup
        self.cur:     str | None = None     # jogador atual (PLAYING)
        self.winner:  str | None = None
        self.consec:  int = 0               # acertos consecutivos (sequência)

    def init(self, gtype: str):
        self.gtype = gtype
        self.players = {
            'PVP':  ['JOGADOR1', 'JOGADOR2'],
            'PVC':  ['JOGADOR',  'CPU'],
            'SOLO': ['JOGADOR',  'CPU'],
        }[gtype]
        self.boards = {p: Board() for p in self.players}
        self.phase  = 'SETUP'
        self.sp_idx = 0
        self.ss_idx = 0
        if 'CPU' in self.players:
            self._cpu_place()

    def _cpu_place(self):
        """Posiciona todos os navios da CPU aleatoriamente."""
        board = self.boards['CPU']
        for ship in SHIP_ORDER:
            ok = False
            while not ok:
                r      = random.randint(0, 9)
                c      = random.randint(0, 9)
                coord  = Board.idx_to_coord(r, c)
                orient = random.choice(['HORIZONTAL', 'VERTICAL'])
                ok, _  = board.place(ship, coord, orient)

    # ── Setup helpers ─────────────────────────────────────────

    def setup_player(self) -> str | None:
        """Retorna o próximo jogador humano a posicionar, ou None se todos terminaram."""
        while self.sp_idx < len(self.players):
            p = self.players[self.sp_idx]
            if p == 'CPU':              
                self.sp_idx += 1
                self.ss_idx  = 0
            else:
                return p
        return None

    def current_ship(self) -> str | None:
        if self.ss_idx < len(SHIP_ORDER):
            return SHIP_ORDER[self.ss_idx]
        return None

    def advance(self):
        """Avança ao próximo navio; se acabaram, passa ao próximo jogador."""
        self.ss_idx += 1
        if self.ss_idx >= len(SHIP_ORDER):
            self.sp_idx += 1
            self.ss_idx  = 0


    def start_play(self):
        self.phase  = 'PLAYING'
        self.cur    = self.players[0]
        self.consec = 0

    def opponent(self, p: str | None = None) -> str:
        if p is None:
            p = self.cur
        if len(self.players) < 2:
            return self.players[0]
        return self.players[1 - self.players.index(p)]

    def switch(self):
        self.cur    = self.opponent()
        self.consec = 0


G = GameState()
