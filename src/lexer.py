"""
lexer.py  —  Analisador Léxico PLY (Batalha Naval)
───────────────────────────────────────────────────
Define os TOKENS da linguagem de comandos do jogo e as
EXPRESSÕES REGULARES que os reconhecem.

ATUALIZAÇÃO: os tokens CLASSIC ('CLASSICO') e SEQUENCE ('SEQUENCIA')
foram REMOVIDOS. O jogo agora tem um único modo — Sequência de
Acertos — embutido diretamente na gramática da sessão (ver
docs/tabela_producoes.py, seção "Gramática da Sessão":
resultado → HIT atirar_seq | MISS).

Tokens da linguagem:
┌─────────────────┬────────────────────┬──────────────────────────────────┐
│ Tipo do token   │ Padrão / Palavra   │ Descrição                        │
├─────────────────┼────────────────────┼──────────────────────────────────┤
│ SHOOT           │ ATIRAR             │ Comando de tiro                  │
│ PLACE           │ POSICIONAR         │ Posicionar navio                 │
│ START           │ INICIAR            │ Iniciar partida                  │
│ QUIT            │ SAIR               │ Encerrar programa                │
│ HORIZONTAL      │ HORIZONTAL         │ Orientação do navio              │
│ VERTICAL        │ VERTICAL           │ Orientação do navio              │
│ CARRIER         │ PORTA_AVIOES       │ Navio (5 células)                │
│ BATTLESHIP      │ CORACADO           │ Navio (4 células)                │
│ DESTROYER       │ DESTROYER          │ Navio (3 células)                │
│ SUBMARINE       │ SUBMARINO          │ Navio (3 células)                │
│ PATROL          │ PATRULHA           │ Navio (2 células)                │
│ PVP             │ PVP                │ Jogador vs Jogador               │
│ PVC             │ PVC                │ Jogador vs CPU                   │
│ SOLO            │ SOLO               │ Solo                             │
│ HELP            │ AJUDA              │ Exibir ajuda                     │
│ BOARD           │ TABULEIRO          │ Exibir grade                     │
│ RANDOM          │ ALEATORIO          │ Posicionamento aleatório         │
│ RESTART         │ REINICIAR          │ Reiniciar jogo                   │
│ COORDINATE      │ [A-J](10|[1-9])    │ Coordenada (ex: B4, A10)         │
│ ID              │ [A-Za-z_][...]     │ Identificador genérico           │
└─────────────────┴────────────────────┴──────────────────────────────────┘
"""

import re
import ply.lex as lex

# ════════════════════════════════════════════════════════════════
# Palavras reservadas: texto digitado (maiúsculo) -> tipo do token
# ════════════════════════════════════════════════════════════════

RESERVED: dict[str, str] = {
    # ── Comandos principais ────────────────────────────────────
    'ATIRAR':       'SHOOT',
    'POSICIONAR':   'PLACE',
    'INICIAR':      'START',
    'SAIR':         'QUIT',
    # ── Orientações ───────────────────────────────────────────
    'HORIZONTAL':   'HORIZONTAL',
    'VERTICAL':     'VERTICAL',
    # ── Navios (palavra → token) ───────────────────────────────
    'PORTA_AVIOES': 'CARRIER',
    'CORACADO':     'BATTLESHIP',
    'DESTROYER':    'DESTROYER',
    'SUBMARINO':    'SUBMARINE',
    'PATRULHA':     'PATROL',
    # ── Tipos de partida ──────────────────────────────────────
    'PVP':          'PVP',
    'PVC':          'PVC',
    'SOLO':         'SOLO',
    # ── Utilitários ───────────────────────────────────────────
    'AJUDA':        'HELP',
    'TABULEIRO':    'BOARD',
    'ALEATORIO':    'RANDOM',
    'REINICIAR':    'RESTART',
}

tokens: list[str] = list(set(RESERVED.values())) + ['COORDINATE', 'ID']

# ════════════════════════════════════════════════════════════════
# Regras léxicas (expressões regulares)
# ════════════════════════════════════════════════════════════════

def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    """
    Reconhece identificadores e palavras reservadas.

    Expressão regular:  [A-Za-z_][A-Za-z0-9_]*
    Inclui underscore para reconhecer PORTA_AVIOES como token único.

    Prioridade de classificação:
      1. Coordenada  – ex: B4, A10  → token COORDINATE
      2. Reservada   – ex: ATIRAR   → token específico (ex: SHOOT)
      3. Genérico    – qualquer outro identificador → token ID
    """
    upper = t.value.upper()

    m = re.match(r'^([A-J])(10|[1-9])$', upper)
    if m:
        t.type  = 'COORDINATE'
        t.value = upper       
        return t

    tok_type = RESERVED.get(upper)
    if tok_type:
        t.type  = tok_type
        t.value = tok_type      
    else:
        t.type  = 'ID'
        t.value = upper
    return t

t_ignore = ' \t\r'

t_ignore_COMMENT = r'\#[^\n]*'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    ch = t.value[0]
    if not ch.isspace():
        print(f"  [ERRO LÉXICO] Símbolo inválido: '{ch}' (linha {t.lexer.lineno})")
    t.lexer.skip(1)

lexer = lex.lex()
