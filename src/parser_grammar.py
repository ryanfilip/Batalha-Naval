"""
parser_grammar.py  —  Analisador Sintático PLY (Batalha Naval)
───────────────────────────────────────────────────────────────
Define a GRAMÁTICA da linguagem de comandos e vincula cada produção
a uma AÇÃO SEMÂNTICA (Tradução Dirigida pela Sintaxe).

Gramática BNF — gramática POR COMANDO (o que o PLY parseia a cada
linha digitada). Para o fluxo completo de uma partida (a "Gramática
da Sessão", elaborada com o professor — onde Acerto leva de volta a
Atirar), veja docs/tabela_producoes.py e docs/arvore_derivacao.py.

command     → shoot_cmd
            | place_cmd
            | start_cmd
            | quit_cmd
            | help_cmd
            | board_cmd
            | random_cmd
            | restart_cmd

shoot_cmd   → SHOOT COORDINATE
place_cmd   → PLACE ship_type COORDINATE orientation
start_cmd   → START player_mode
quit_cmd    → QUIT
help_cmd    → HELP
board_cmd   → BOARD
random_cmd  → RANDOM
restart_cmd → RESTART

ship_type   → CARRIER | BATTLESHIP | DESTROYER | SUBMARINE | PATROL
orientation → HORIZONTAL | VERTICAL
player_mode → PVP | PVC | SOLO

Tabela de Produções × Ações Semânticas:
──────────────────────────────────────────────────────────────────────────────
 #   Produção                               Ação Semântica
──────────────────────────────────────────────────────────────────────────────
 1   command     → shoot_cmd                p[0] = p[1]
 2   command     → place_cmd                p[0] = p[1]
 3   command     → start_cmd                p[0] = p[1]
 4   command     → quit_cmd                 p[0] = p[1]
 5   command     → help_cmd                 p[0] = p[1]
 6   command     → board_cmd                p[0] = p[1]
 7   command     → random_cmd               p[0] = p[1]
 8   command     → restart_cmd              p[0] = p[1]
 9   shoot_cmd   → SHOOT COORDINATE         p[0]=('shoot',p[2]); sem_shoot(p[2])
10   place_cmd   → PLACE ship_type          p[0]=('place',p[2],p[3],p[4]);
                    COORDINATE orientation   sem_place(p[2],p[3],p[4])
11   start_cmd   → START player_mode        p[0]=('start',p[2]); sem_start(p[2])
12   quit_cmd    → QUIT                     sys.exit(0)
13   help_cmd    → HELP                     sem_help()
14   board_cmd   → BOARD                    sem_board()
15   random_cmd  → RANDOM                   sem_random()
16   restart_cmd → RESTART                  G.reset()
17   ship_type   → CARRIER                  p[0] = 'CARRIER'
18   ship_type   → BATTLESHIP               p[0] = 'BATTLESHIP'
19   ship_type   → DESTROYER                p[0] = 'DESTROYER'
20   ship_type   → SUBMARINE                p[0] = 'SUBMARINE'
21   ship_type   → PATROL                   p[0] = 'PATROL'
22   orientation → HORIZONTAL               p[0] = 'HORIZONTAL'
23   orientation → VERTICAL                 p[0] = 'VERTICAL'
24   player_mode → PVP                      p[0] = 'PVP'
25   player_mode → PVC                      p[0] = 'PVC'
26   player_mode → SOLO                     p[0] = 'SOLO'
──────────────────────────────────────────────────────────────────────────────
"""

import sys
import ply.yacc as yacc
from .lexer import tokens, lexer 

from .semantic import (
    sem_start, sem_place, sem_random,
    sem_shoot, sem_board, sem_help,
)
from .game_engine import G

# ════════════════════════════════════════════════════════════════
# Produções Gramaticais + Ações Semânticas
# ════════════════════════════════════════════════════════════════


def p_command(p):
    '''command : shoot_cmd
               | place_cmd
               | start_cmd
               | quit_cmd
               | help_cmd
               | board_cmd
               | random_cmd
               | restart_cmd'''
    p[0] = p[1]



def p_shoot_cmd(p):
    '''shoot_cmd : SHOOT COORDINATE'''
    p[0] = ('shoot', p[2])
    sem_shoot(p[2])


def p_place_cmd(p):
    '''place_cmd : PLACE ship_type COORDINATE orientation'''
    p[0] = ('place', p[2], p[3], p[4])
    sem_place(p[2], p[3], p[4])



def p_start_cmd(p):
    '''start_cmd : START player_mode'''
    p[0] = ('start', p[2])
    sem_start(p[2])



def p_quit_cmd(p):
    '''quit_cmd : QUIT'''
    p[0] = ('quit',)
    print("\n  ⚓ Até logo, almirante!\n")
    sys.exit(0)

def p_help_cmd(p):
    '''help_cmd : HELP'''
    p[0] = ('help',)
    sem_help()

def p_board_cmd(p):
    '''board_cmd : BOARD'''
    p[0] = ('board',)
    sem_board()

def p_random_cmd(p):
    '''random_cmd : RANDOM'''
    p[0] = ('random',)
    sem_random()

def p_restart_cmd(p):
    '''restart_cmd : RESTART'''
    p[0] = ('restart',)
    G.reset()
    print("\n  Jogo reiniciado.")
    print("  → INICIAR <PVP|PVC|SOLO>\n")



def p_ship_type(p):
    '''ship_type : CARRIER
                 | BATTLESHIP
                 | DESTROYER
                 | SUBMARINE
                 | PATROL'''
    p[0] = p[1]



def p_orientation(p):
    '''orientation : HORIZONTAL
                   | VERTICAL'''
    p[0] = p[1]  


def p_player_mode(p):
    '''player_mode : PVP
                   | PVC
                   | SOLO'''
    p[0] = p[1] 



def p_error(p):
    if p:
        print(f"\n  [ERRO SINTÁTICO] Token inesperado: '{p.value}' "
              f"(tipo: {p.type}, linha: {p.lexpos})")
    else:
        print("\n  [ERRO SINTÁTICO] Entrada incompleta ou inválida.")
    print("  → Digite AJUDA para ver os comandos disponíveis.\n")


parser = yacc.yacc(debug=False, write_tables=False)
