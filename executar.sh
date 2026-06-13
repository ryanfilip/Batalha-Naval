#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
#  executar.sh — Batalha Naval PLY
# ═══════════════════════════════════════════════════════════════

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "[1/2] Instalando dependências..."
pip install -r requirements.txt -q

echo ""
echo "  O que deseja executar?"
echo "  1) Jogo                     (main.py)"
echo "  2) Árvores de derivação     (docs/arvore_derivacao.py)"
echo "  3) Tabela de produções      (docs/tabela_producoes.py)"
echo "  4) Testes automatizados     (tests/test_batalha_naval.py)"
echo ""
read -rp "  Escolha [1-4, padrão=1]: " opcao
opcao="${opcao:-1}"

echo ""
case "$opcao" in
  1) python main.py ;;
  2) python docs/arvore_derivacao.py ;;
  3) python docs/tabela_producoes.py ;;
  4) python -m pytest tests/ -v ;;
  *) echo "Opção inválida. Execute: python main.py" ;;
esac
