#!/usr/bin/env bash
# Vigila una corrida del pipeline AgroGenIA en tiempo real.
# Uso: ./vigilar.sh v46_profunda_all
BASE="${1:-v46_profunda_all}"
while true; do
  clear
  echo "================ $(date '+%H:%M:%S') ================"
  echo "--- ULTIMO ESTADO (.estado) ---"
  tail -n 14 "${BASE}.estado" 2>/dev/null || echo "(aun no hay archivo .estado)"
  echo
  echo "--- PROCESOS ACTIVOS ---"
  ps -ef | grep -E "pipeline_v4.6|hmmscan|efetch|esearch" | grep -v grep \
    || echo "(ningun proceso del pipeline activo -> ya termino o murio)"
  echo
  echo "--- ARCHIVOS DE SALIDA ---"
  ls -lh ${BASE}.* 2>/dev/null || echo "(aun sin informes)"
  echo
  echo "  [Ctrl+C para salir de la vigilancia; NO mata la corrida]"
  sleep 10
done