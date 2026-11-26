#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker build -q -t tp4-qos-ns2 -f Dockerfile .
python3 scripts/preparar.py
for cenario in A_droptail A_red B_misto B_referencia C_diffserv C4_normal C4_livre C4_abuso; do
 mkdir -p "resultados/$cenario"
 if [[ "$cenario" == C4_* ]]; then
  comando=(scripts/cenario.tcl "$cenario" "resultados/$cenario")
  pasta=/work
 else
  comando=("/work/scripts/gerados/$cenario.tcl")
  pasta="/work/resultados/$cenario"
 fi
 docker run --rm --entrypoint stdbuf -w "$pasta" --user "$(id -u):$(id -g)" -v "$PWD:/work" tp4-qos-ns2 -oL ns "${comando[@]}" > "resultados/$cenario/execucao.log" 2>&1
 echo "OK: $cenario"
done
python3 scripts/analisar.py
