#!/usr/bin/env bash
# Executa a suíte de validação do DegeHub ERP sem usar o banco operacional.
# Prioriza o interpretador da .venv do projeto (Linux). Se ela não existir
# ou tiver sido criada no Windows, usa python3 ou python do sistema.
set -euo pipefail

raiz_projeto="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$raiz_projeto"

python_venv="$raiz_projeto/.venv/bin/python"
python=""

if [[ -x "$python_venv" ]]; then
  python="$python_venv"
else
  if [[ -d "$raiz_projeto/.venv" && -f "$raiz_projeto/.venv/Scripts/python.exe" && ! -x "$python_venv" ]]; then
    echo "A .venv do projeto foi criada no Windows e não funciona no Linux." >&2
    echo "Recrie-a com: python3 -m venv --clear .venv" >&2
    echo "Enquanto isso, os testes serão executados com o Python do sistema." >&2
  fi
  if command -v python3 >/dev/null 2>&1; then
    python="$(command -v python3)"
  elif command -v python >/dev/null 2>&1; then
    python="$(command -v python)"
  fi
fi

if [[ -z "$python" ]]; then
  echo "Python 3.10+ não foi encontrado. Instale o Python e, na raiz do projeto, execute: python3 -m venv .venv && source .venv/bin/activate && ./scripts/verificar.sh" >&2
  exit 1
fi

if ! "$python" --version; then
  if [[ "$python" == "$python_venv" ]]; then
    echo "A .venv do projeto não consegue iniciar. Recrie-a com python3 -m venv --clear .venv e execute ./scripts/verificar.sh novamente." >&2
  else
    echo "O Python não conseguiu iniciar. Instale Python 3.10+ e crie a .venv com python3 -m venv .venv." >&2
  fi
  exit 1
fi

"$python" -m unittest discover -s tests -v
