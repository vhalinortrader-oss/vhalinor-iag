#!/usr/bin/env bash
set -euo pipefail

cd /home/alexmsales/Desktop/vhalinor_IAG

# ativa venv
if [ -f .venv/bin/activate ]; then
  . .venv/bin/activate
fi

# instala dependências do web se ainda não existir
pip -q install fastapi uvicorn

uvicorn interface_web:app --host 0.0.0.0 --port 8000 --reload

