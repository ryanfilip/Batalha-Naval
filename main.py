"""
main.py  —  Ponto de Entrada (Batalha Naval PLY)
─────────────────────────────────────────────────
Loop principal: lê comandos do usuário, repassa ao parser PLY.

Fluxo:
  entrada de texto
      ↓
  [Lexer]  src/lexer.py          → tokenização
      ↓
  [Parser] src/parser_grammar.py → reconhecimento sintático
      ↓
  [Semântica] src/semantic.py    → execução da ação de jogo
      ↓
  [Motor]  src/game_engine.py    → atualização do estado

ATUALIZAÇÃO: prompt de boas-vindas atualizado — sem modos CLASSICO/SEQUENCIA.
"""

import sys
from src.parser_grammar import parser, lexer
from src.game_engine import G


def main() -> None:
    print("""
  ╔══════════════════════════════════════════════════════════╗
  ║    ⚓  BATALHA NAVAL  ⚓    Compiladores PLY 2026/1     ║
  ╠══════════════════════════════════════════════════════════╣
  ║  Modo único: Sequência de Acertos                        ║
  ║  (acerto garante novo tiro; erro passa a vez)            ║
  ╚══════════════════════════════════════════════════════════╝
  Bem-vindo, almirante! Digite AJUDA para ver os comandos.
  Exemplo rápido:  INICIAR PVC
""")

    while True:
        try:
            if   G.phase == 'IDLE':    prompt = "batalha> "
            elif G.phase == 'SETUP':   prompt = f"setup[{G.setup_player() or '?'}]> "
            elif G.phase == 'PLAYING': prompt = f"[{G.cur}]> "
            else:                      prompt = "fim> "

            line = input(prompt).strip()
            if not line:
                continue
            parser.parse(line, lexer=lexer)

        except KeyboardInterrupt:
            print("\n  Interrompido. Use SAIR para encerrar.")
        except EOFError:
            print("\n  ⚓ Até logo!")
            sys.exit(0)


if __name__ == '__main__':
    main()
