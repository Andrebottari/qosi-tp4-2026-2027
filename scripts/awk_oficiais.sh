#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
for cenario in A_droptail A_red B_misto B_referencia C_diffserv C4_normal C4_livre C4_abuso; do
 mkdir -p "resultados/$cenario/awk_oficial"
 docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/work" -w "/work/resultados/$cenario/awk_oficial" --entrypoint sh tp4-qos-ns2 -c 'gawk -f /work/originais/files/loss.awk ../out.tr; gawk -f /work/scripts/awk/bw.awk ../out.tr'
done
