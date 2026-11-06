#!/usr/bin/env bash
# Push del estado del kernel Marce-AGI como versión nueva del dataset de estado.
# Detalle del workflow en training/README.md.
#
# Uso:
#   bash kaggle_push_state.sh "slice 3: router calibrado"  [dir_estado]
set -euo pipefail

MSG="${1:-actualización de estado del kernel}"
DIR="${2:-${MA_STATE_DIR:-/kaggle/working/state}}"

if [ ! -d "$DIR" ]; then
  echo "ERROR: no existe el directorio de estado $DIR" >&2
  exit 1
fi

if [ ! -f "$DIR/dataset-metadata.json" ]; then
  kaggle datasets init -p "$DIR"
  echo "Primer uso: kaggle datasets init generó $DIR/dataset-metadata.json." >&2
  echo "Editalo (title: Marce-AGI state, id: <usuario>/marce-agi-state) y volvé a correr este script." >&2
  exit 2
fi

kaggle datasets version -p "$DIR" -m "$MSG" --dir-mode zip
echo "OK: Estado versionado como nueva versión del dataset -> $MSG"
