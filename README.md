# ⚓ Batalha Naval PLY

> **Trabalho P2 – Compiladores 2026/1**  
> Exploração e aplicação dos conceitos de **análise léxica**, **sintática** e **semântica** por meio da modificação de um gerador de analisador.

---

## 📌 Sobre o projeto

Simulador do jogo **Batalha Naval** implementado como uma **linguagem de comandos** processada por um compilador escrito com **PLY (Python Lex-Yacc)**.

O usuário digita comandos em português (ex: `ATIRAR B4`, `INICIAR PVC`) que são reconhecidos pelo analisador léxico-sintático e executados pelas ações semânticas.

### Modo de jogo

O jogo possui um **único modo**: **Sequência de Acertos**.

> **Acerto** → garante novo tiro (o turno continua)  
> **Erro (Água)** → passa a vez para o oponente

Esse comportamento está modelado diretamente na **Gramática da Sessão** (elaborada com o professor):

```
atirar_seq → SHOOT COORDINATE resultado
resultado  → HIT atirar_seq      ← Acerto: recursão (novo tiro)
           | MISS                 ← Água: fim do turno
```

### Tipos de partida

| Tipo  | Descrição                                               |
|-------|---------------------------------------------------------|
| `PVP` | Jogador vs Jogador (hot-seat)                           |
| `PVC` | Jogador vs CPU (IA aleatória — também joga em sequência)|
| `SOLO`| Jogador contra grade gerada automaticamente; CPU não atira de volta |

---

## 🗂️ Estrutura do repositório

```
batalha_naval_ply/
│
├── src/                         ← Código-fonte do compilador
│   ├── __init__.py
│   ├── game_engine.py           # Motor: Board, GameState, display_side_by_side
│   ├── lexer.py                 # Análise léxica: 20 tokens + regex
│   ├── parser_grammar.py        # Análise sintática: 26 produções BNF
│   └── semantic.py              # Ações semânticas: sem_*() functions
│
├── tests/                       ← Testes automatizados
│   ├── __init__.py
│   └── test_batalha_naval.py    # 40+ casos: motor, lexer, gramática
│
├── docs/                        ← Material para apresentação acadêmica
│   ├── arvore_derivacao.py      # Árvores de derivação + Árvore da Sessão
│   └── tabela_producoes.py      # Tokens + Produções + Gramática da Sessão
│
├── exemplos/
│   └── partida_pvc.txt          # Sessão de jogo anotada
│
├── main.py                      ← Ponto de entrada
├── requirements.txt
├── executar.sh
├── .gitignore
└── README.md
```

---

## ⚙️ Instalação e execução

```bash
pip install ply pytest
python main.py
```

### Script interativo

```bash
chmod +x executar.sh
./executar.sh
```

### Testes

```bash
python -m pytest tests/ -v
```

---

## 🧩 Comandos da linguagem

| Comando | Sintaxe | Exemplo |
|---------|---------|---------|
| Iniciar | `INICIAR <TIPO>` | `INICIAR PVC` |
| Posicionar | `POSICIONAR <NAVIO> <COORD> <ORIENTAÇÃO>` | `POSICIONAR PORTA_AVIOES A1 HORIZONTAL` |
| Aleatório | `ALEATORIO` | `ALEATORIO` |
| Atirar | `ATIRAR <COORD>` | `ATIRAR B4` |
| Tabuleiro | `TABULEIRO` | `TABULEIRO` |
| Reiniciar | `REINICIAR` | `REINICIAR` |
| Ajuda | `AJUDA` | `AJUDA` |
| Sair | `SAIR` | `SAIR` |

**Navios:**

| Palavra | Token | Tamanho |
|---------|-------|---------|
| `PORTA_AVIOES` | `CARRIER` | 5 |
| `CORACADO` | `BATTLESHIP` | 4 |
| `DESTROYER` | `DESTROYER` | 3 |
| `SUBMARINO` | `SUBMARINE` | 3 |
| `PATRULHA` | `PATROL` | 2 |

**Coordenadas:** colunas `A–J` + linhas `1–10`
- `HORIZONTAL` = cresce para a direita (esquerda → direita)
- `VERTICAL` = cresce para baixo (cima → baixo)
- A coordenada é sempre o canto **superior-esquerdo** do navio

---

## 🔬 Detalhes do compilador (PLY)

### Análise Léxica (`src/lexer.py`)

- **20 tokens** 
- Expressão regular principal: `[A-Za-z_][A-Za-z0-9_]*`
  - Detecta coordenadas via `[A-J](10|[1-9])`
  - Mapeia palavras reservadas via `RESERVED`

### Análise Sintática (`src/parser_grammar.py`)

- **26 produções** LALR(1) sem ambiguidades
- `start_cmd → START player_mode` (1 argumento — sem `game_mode`)

### Gramática da Sessão (`docs/`)

Elaborada com o professor. Modela o **fluxo completo** de uma partida:

```
sessao      → START player_mode setup atirar_seq
setup       → place_cmd setup | RANDOM
atirar_seq  → SHOOT COORDINATE resultado
resultado   → HIT atirar_seq        ← Sequência de Acertos (recursão!)
            | MISS                   ← Fim do turno
utilitario  → BOARD | RESTART | QUIT | HELP
```

### Ações Semânticas (`src/semantic.py`)

| Ação | Gatilho | Efeito |
|------|---------|--------|
| `sem_start(gtype)` | `INICIAR` | Inicializa jogo (sem parâmetro de modo) |
| `sem_place(ship, coord, orient)` | `POSICIONAR` | Valida e posiciona navio |
| `sem_random()` | `ALEATORIO` | Posicionamento automático |
| `sem_shoot(coord)` | `ATIRAR` | Tiro + Sequência de Acertos + exibição lado a lado |
| `sem_board()` | `TABULEIRO` | Exibe dois tabuleiros lado a lado |
| `sem_help()` | `AJUDA` | Lista de comandos |

---

## 📊 Para a apresentação

| Requisito | Arquivo |
|-----------|---------|
| Árvores de derivação e anotadas | `docs/arvore_derivacao.py` |
| Tabela de tokens | `docs/tabela_producoes.py` |
| Tabela de produções × ações semânticas | `docs/tabela_producoes.py` |
| Gramática da Sessão (elaborada com professor) | `docs/tabela_producoes.py` |
| Slides (Árvore de Sintaxe + Esquema de Tradução) | `batalha_naval_traducao.pptx` |
| Execução do código | `python main.py` |


---

## 👥 Autores

Ryan Filipe de Mendonça Borges

Leonardo Takahata Yocogawa

Cassio Benjamin Maciel
