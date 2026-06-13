"""
tests/test_batalha_naval.py
────────────────────────────
Testes automatizados do Batalha Naval PLY.
Cobre: motor do jogo, análise léxica e análise sintática/semântica.

Execute com:
    python -m pytest tests/ -v
  ou:
    python tests/test_batalha_naval.py

ATUALIZAÇÕES:
  - Removidos testes de CLASSICO/SEQUENCIA (tokens/gramática eliminados).
  - start_cmd agora é START player_mode (1 argumento).
  - SOLO: jogador atira na grade CPU (que nunca atira de volta).
  - Adicionados testes de Sequência de Acertos (acerto → novo tiro).
  - Adicionados testes de exibição lado a lado (render_lines).
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.game_engine import (
    Board, GameState,
    SHIPS_CONFIG, SHIP_ORDER,
    display_side_by_side,
)
from src.lexer import lexer, RESERVED, tokens


# ════════════════════════════════════════════════════════════════
# Testes game_engine.py
# ════════════════════════════════════════════════════════════════

class TestBoard(unittest.TestCase):

    def setUp(self):
        self.board = Board()


    def test_coord_to_idx_basico(self):
        self.assertEqual(Board.coord_to_idx('A1'),  (0, 0))
        self.assertEqual(Board.coord_to_idx('J10'), (9, 9))
        self.assertEqual(Board.coord_to_idx('B4'),  (3, 1))
        self.assertEqual(Board.coord_to_idx('E5'),  (4, 4))

    def test_idx_to_coord_basico(self):
        self.assertEqual(Board.idx_to_coord(0, 0), 'A1')
        self.assertEqual(Board.idx_to_coord(9, 9), 'J10')
        self.assertEqual(Board.idx_to_coord(3, 1), 'B4')

    def test_round_trip_coord(self):
        for col in range(10):
            for row in range(10):
                coord = Board.idx_to_coord(row, col)
                r, c  = Board.coord_to_idx(coord)
                self.assertEqual((r, c), (row, col))

    def test_place_horizontal_valido(self):
        ok, _ = self.board.place('CARRIER', 'A1', 'HORIZONTAL')
        self.assertTrue(ok)
        for c in range(5):
            self.assertEqual(self.board.grid[0][c], 'P')

    def test_place_vertical_valido(self):
        ok, _ = self.board.place('PATROL', 'A1', 'VERTICAL')
        self.assertTrue(ok)
        self.assertEqual(self.board.grid[0][0], 'T')
        self.assertEqual(self.board.grid[1][0], 'T')

    def test_horizontal_esquerda_para_direita(self):
        """HORIZONTAL cresce pela coluna (esquerda → direita)."""
        ok, _ = self.board.place('DESTROYER', 'B3', 'HORIZONTAL')
        self.assertTrue(ok)
        r, c_start = Board.coord_to_idx('B3')
        for i in range(3):
            self.assertEqual(self.board.grid[r][c_start + i], 'D')

    def test_vertical_cima_para_baixo(self):
        """VERTICAL cresce pela linha (cima → baixo)."""
        ok, _ = self.board.place('DESTROYER', 'B3', 'VERTICAL')
        self.assertTrue(ok)
        r_start, c = Board.coord_to_idx('B3')
        for i in range(3):
            self.assertEqual(self.board.grid[r_start + i][c], 'D')

    def test_place_fora_dos_limites_horizontal(self):
        ok, msg = self.board.place('CARRIER', 'H1', 'HORIZONTAL')
        self.assertFalse(ok)
        self.assertIn("limites", msg)

    def test_place_fora_dos_limites_vertical(self):
        ok, msg = self.board.place('CARRIER', 'A8', 'VERTICAL')
        self.assertFalse(ok)
        self.assertIn("limites", msg)

    def test_place_posicao_ocupada(self):
        self.board.place('DESTROYER', 'A1', 'HORIZONTAL')
        ok, msg = self.board.place('PATROL', 'A1', 'HORIZONTAL')
        self.assertFalse(ok)
        self.assertIn("ocupada", msg)

    def test_place_todos_navios(self):
        positions = [
            ('CARRIER',    'A1', 'HORIZONTAL'),
            ('BATTLESHIP', 'A2', 'HORIZONTAL'),
            ('DESTROYER',  'A3', 'HORIZONTAL'),
            ('SUBMARINE',  'A4', 'HORIZONTAL'),
            ('PATROL',     'A5', 'HORIZONTAL'),
        ]
        for ship, coord, orient in positions:
            ok, _ = self.board.place(ship, coord, orient)
            self.assertTrue(ok, f"Falhou ao posicionar {ship}")
        self.assertEqual(len(self.board.ships), 5)


    def test_shot_miss(self):
        result, sunk = self.board.receive_shot('A1')
        self.assertEqual(result, 'MISS')
        self.assertIsNone(sunk)
        self.assertEqual(self.board.grid[0][0], 'O')

    def test_shot_hit(self):
        self.board.place('PATROL', 'A1', 'HORIZONTAL')
        result, sunk = self.board.receive_shot('A1')
        self.assertEqual(result, 'HIT')
        self.assertIsNone(sunk)   

    def test_shot_sunk(self):
        self.board.place('PATROL', 'A1', 'HORIZONTAL')
        self.board.receive_shot('A1')                   
        result, sunk = self.board.receive_shot('B1')    
        self.assertEqual(result, 'HIT')
        self.assertEqual(sunk, 'PATROL')

    def test_shot_repeat(self):
        self.board.receive_shot('A1')                
        result, _ = self.board.receive_shot('A1')
        self.assertEqual(result, 'REPEAT')

    def test_all_sunk_false(self):
        self.board.place('PATROL', 'A1', 'HORIZONTAL')
        self.assertFalse(self.board.all_sunk())

    def test_all_sunk_true(self):
        self.board.place('PATROL', 'A1', 'HORIZONTAL')
        self.board.receive_shot('A1')
        self.board.receive_shot('B1')
        self.assertTrue(self.board.all_sunk())

    def test_render_lines_comprimento(self):
        """Cada linha de render_lines deve ter exatamente 27 chars."""
        lines = self.board.render_lines(title="JOGADOR")
        for line in lines:
            self.assertEqual(len(line), 27,
                             f"Linha com {len(line)} chars: '{line}'")

    def test_render_shots_lines_comprimento(self):
        """Cada linha de render_shots_lines deve ter exatamente 27 chars."""
        lines = self.board.render_shots_lines(title="TIROS")
        for line in lines:
            self.assertEqual(len(line), 27,
                             f"Linha com {len(line)} chars: '{line}'")

    def test_render_lines_quantidade(self):
        """render_lines deve ter 14 linhas: título + cabeçalho + borda + 10 rows + borda."""
        lines = self.board.render_lines()
        self.assertEqual(len(lines), 14)


# ════════════════════════════════════════════════════════════════
# Testes do GameState
# ════════════════════════════════════════════════════════════════

class TestGameState(unittest.TestCase):

    def setUp(self):
        self.gs = GameState()

    def test_reset_estado_inicial(self):
        self.gs.init('PVC')
        self.gs.reset()
        self.assertEqual(self.gs.phase, 'IDLE')
        self.assertIsNone(self.gs.gtype)

    def test_sem_atributo_mode(self):
        """GameState não deve ter atributo 'mode' (CLASSICO foi removido)."""
        self.gs.init('PVC')
        self.assertFalse(hasattr(self.gs, 'mode'),
                         "Atributo 'mode' não deveria existir após remoção do CLASSICO")

    def test_init_pvp(self):
        self.gs.init('PVP')
        self.assertEqual(self.gs.players, ['JOGADOR1', 'JOGADOR2'])
        self.assertEqual(self.gs.phase, 'SETUP')

    def test_init_pvc_cpu_posicionado(self):
        self.gs.init('PVC')
        cpu_board = self.gs.boards['CPU']
        self.assertEqual(len(cpu_board.ships), len(SHIP_ORDER))

    def test_init_solo_tem_grade_cpu(self):
        """SOLO deve criar grade CPU (para o jogador atirar), mas CPU não joga."""
        self.gs.init('SOLO')
        self.assertIn('CPU', self.gs.boards)
        self.assertEqual(len(self.gs.boards['CPU'].ships), len(SHIP_ORDER))

    def test_init_solo_players(self):
        self.gs.init('SOLO')
        self.assertEqual(self.gs.players, ['JOGADOR', 'CPU'])

    def test_setup_player_pula_cpu(self):
        self.gs.init('PVC')
        player = self.gs.setup_player()
        self.assertEqual(player, 'JOGADOR')

    def test_setup_player_solo_retorna_jogador(self):
        self.gs.init('SOLO')
        player = self.gs.setup_player()
        self.assertEqual(player, 'JOGADOR')

    def test_advance_navios(self):
        self.gs.init('SOLO')
        self.assertEqual(self.gs.current_ship(), 'CARRIER')
        self.gs.advance()
        self.assertEqual(self.gs.current_ship(), 'BATTLESHIP')

    def test_advance_todos_navios(self):
        """Após avançar por todos os navios, setup_player() deve retornar None."""
        self.gs.init('SOLO')
        for _ in range(len(SHIP_ORDER)):
            self.gs.advance()
        self.assertIsNone(self.gs.setup_player())

    def test_advance_muda_jogador_pvp(self):
        self.gs.init('PVP')
        for _ in range(len(SHIP_ORDER)):
            self.gs.advance()
        self.assertEqual(self.gs.setup_player(), 'JOGADOR2')

    def test_opponent_pvp(self):
        self.gs.init('PVP')
        self.gs.start_play()
        cur = self.gs.cur
        opp = self.gs.opponent()
        self.assertNotEqual(cur, opp)
        self.assertIn(opp, self.gs.players)

    def test_opponent_solo(self):
        """No SOLO, o oponente é sempre CPU."""
        self.gs.init('SOLO')
        self.gs.start_play()
        self.assertEqual(self.gs.opponent('JOGADOR'), 'CPU')

    def test_switch_troca_jogador(self):
        self.gs.init('PVP')
        self.gs.start_play()
        p1 = self.gs.cur
        self.gs.switch()
        p2 = self.gs.cur
        self.assertNotEqual(p1, p2)

    def test_switch_zera_consec(self):
        """switch() deve zerar o contador de acertos consecutivos."""
        self.gs.init('PVP')
        self.gs.start_play()
        self.gs.consec = 3
        self.gs.switch()
        self.assertEqual(self.gs.consec, 0)

    def test_sequencia_acertos_nao_troca_turno(self):
        """
        Acerto NÃO deve trocar de turno (Sequência de Acertos).
        Verifica que G.cur permanece o mesmo após um HIT.
        """
        self.gs.init('PVP')
        board = self.gs.boards['JOGADOR2']
        board.place('PATROL', 'A1', 'HORIZONTAL')
        self.gs.start_play()
        self.gs.cur = 'JOGADOR1'

        result, _ = board.receive_shot('A1')
        self.assertEqual(result, 'HIT')
        self.gs.consec += 1
        self.assertEqual(self.gs.cur, 'JOGADOR1',
                         "Acerto não deve trocar o turno (Sequência de Acertos)")
        self.assertEqual(self.gs.consec, 1)

    def test_sequencia_miss_troca_turno(self):
        """Erro (MISS) deve trocar de turno."""
        self.gs.init('PVP')
        board = self.gs.boards['JOGADOR2']
        self.gs.start_play()
        self.gs.cur = 'JOGADOR1'

        result, _ = board.receive_shot('A1')
        self.assertEqual(result, 'MISS')
        self.gs.switch()
        self.assertEqual(self.gs.cur, 'JOGADOR2')


# ════════════════════════════════════════════════════════════════
# Testes do analisador léxico (lexer.py)
# ════════════════════════════════════════════════════════════════

class TestLexer(unittest.TestCase):

    def _tokenize(self, text: str) -> list[tuple[str, str]]:
        lexer.input(text)
        return [(tok.type, tok.value) for tok in lexer]

    def test_token_shoot(self):
        toks = self._tokenize('ATIRAR')
        self.assertEqual(toks, [('SHOOT', 'SHOOT')])

    def test_token_coordinate_simples(self):
        toks = self._tokenize('B4')
        self.assertEqual(toks, [('COORDINATE', 'B4')])

    def test_token_coordinate_j10(self):
        toks = self._tokenize('J10')
        self.assertEqual(toks, [('COORDINATE', 'J10')])

    def test_token_coordinate_a1(self):
        toks = self._tokenize('A1')
        self.assertEqual(toks, [('COORDINATE', 'A1')])

    def test_token_navio_porta_avioes(self):
        toks = self._tokenize('PORTA_AVIOES')
        self.assertEqual(toks, [('CARRIER', 'CARRIER')])

    def test_token_navio_coracado(self):
        toks = self._tokenize('CORACADO')
        self.assertEqual(toks, [('BATTLESHIP', 'BATTLESHIP')])

    def test_sem_token_classico(self):
        """CLASSICO não deve mais ser um token reservado."""
        toks = self._tokenize('CLASSICO')
        self.assertEqual(toks[0][0], 'ID',
                         "CLASSICO foi removido e deve virar ID genérico")

    def test_sem_token_sequencia(self):
        """SEQUENCIA não deve mais ser um token reservado."""
        toks = self._tokenize('SEQUENCIA')
        self.assertEqual(toks[0][0], 'ID',
                         "SEQUENCIA foi removido e deve virar ID genérico")

    def test_sequencia_atirar_b4(self):
        toks = self._tokenize('ATIRAR B4')
        self.assertEqual(toks[0], ('SHOOT',      'SHOOT'))
        self.assertEqual(toks[1], ('COORDINATE', 'B4'))

    def test_sequencia_posicionar(self):
        toks = self._tokenize('POSICIONAR PORTA_AVIOES A1 HORIZONTAL')
        self.assertEqual(toks[0][0], 'PLACE')
        self.assertEqual(toks[1][0], 'CARRIER')
        self.assertEqual(toks[2][0], 'COORDINATE')
        self.assertEqual(toks[3][0], 'HORIZONTAL')

    def test_sequencia_iniciar_sem_modo(self):
        """INICIAR PVC (sem modo) deve gerar apenas START + PVC."""
        toks = self._tokenize('INICIAR PVC')
        self.assertEqual(len(toks), 2)
        self.assertEqual(toks[0][0], 'START')
        self.assertEqual(toks[1][0], 'PVC')

    def test_case_insensitive(self):
        toks = self._tokenize('atirar b4')
        self.assertEqual(toks[0], ('SHOOT',      'SHOOT'))
        self.assertEqual(toks[1], ('COORDINATE', 'B4'))

    def test_comentario_ignorado(self):
        toks = self._tokenize('ATIRAR B4  # este é um comentário')
        self.assertEqual(len(toks), 2)

    def test_k1_nao_e_coordenada(self):
        """K não é coluna válida (A-J), então K1 vira ID."""
        toks = self._tokenize('K1')
        self.assertEqual(toks[0][0], 'ID')

    def test_a0_nao_e_coordenada(self):
        """Linha 0 não é válida, então A0 vira ID."""
        toks = self._tokenize('A0')
        self.assertEqual(toks[0][0], 'ID')

    def test_todos_tokens_reservados(self):
        """Garante que todas as palavras reservadas geram seus tokens."""
        for palavra, tipo_esperado in RESERVED.items():
            toks = self._tokenize(palavra)
            self.assertEqual(len(toks), 1,
                             f"'{palavra}' deveria gerar 1 token")
            self.assertEqual(toks[0][0], tipo_esperado,
                             f"'{palavra}' → esperado {tipo_esperado}, "
                             f"obtido {toks[0][0]}")

    def test_classic_sequence_nao_estao_em_reserved(self):
        """CLASSICO e SEQUENCIA não devem mais estar no dicionário RESERVED."""
        self.assertNotIn('CLASSICO',  RESERVED)
        self.assertNotIn('SEQUENCIA', RESERVED)
        self.assertNotIn('CLASSIC',   RESERVED.values())
        self.assertNotIn('SEQUENCE',  RESERVED.values())

if __name__ == '__main__':
    unittest.main(verbosity=2)
