#!/bin/bash

# Caminho base
PROJETO_DIR=$(pwd)

echo "🔧 Criando ambiente virtual isolado: oraculo-venv..."
python3 -m venv oraculo-venv

echo "✅ Ativando ambiente..."
source oraculo-venv/bin/activate

echo "📦 Instalando dependências..."
pip install --upgrade pip
pip install multiversx-sdk requests rich

echo "✅ Ambiente preparado!"
echo "📂 Diretório do projeto: $PROJETO_DIR"
echo "🚀 Rodando: register_policy.py"

python "$PROJETO_DIR/oracle-backend/register_policy.py"
