#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENV_DIR="${SKILL_DIR}/.venv"
PYTHON_BIN="${VENV_DIR}/bin/python"

if command -v uv >/dev/null 2>&1; then
  UV_BIN="$(command -v uv)"
elif [ -x "${HOME}/.local/bin/uv" ]; then
  UV_BIN="${HOME}/.local/bin/uv"
elif [ -x "${HOME}/Library/Python/3.9/bin/uv" ]; then
  UV_BIN="${HOME}/Library/Python/3.9/bin/uv"
else
  echo "uv is required. Install it first, for example: python3 -m pip install --user uv" >&2
  exit 1
fi

if [ ! -x "${PYTHON_BIN}" ]; then
  "${UV_BIN}" python install 3.13 >/dev/null
  "${UV_BIN}" venv --python 3.13 "${VENV_DIR}" >/dev/null
fi

if ! "${PYTHON_BIN}" -c 'import google.genai, yt_dlp' >/dev/null 2>&1; then
  "${UV_BIN}" pip install --python "${PYTHON_BIN}" google-genai yt-dlp >/dev/null
fi

exec "${PYTHON_BIN}" "${SCRIPT_DIR}/video_analysis.py" "$@"
