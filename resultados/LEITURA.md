# Resultados experimentais incluídos

## Execuções

- Semente 7: oito pastas `A_droptail`, `A_red`, `B_misto`, `B_referencia`, `C_diffserv`, `C4_normal`, `C4_livre`, `C4_abuso`. Cada uma tem `out.tr`, `execucao.log`, `series.csv` e saídas AWK. Os cenários com geração NAM têm também `out.nam`.
- Sementes 11, 23, 41 e 97: as mesmas oito pastas em `multissementes/<semente>/`, com `out.tr.gz`, `execucao.log` e, quando gerado, `out.nam.gz`.

São **40 traces de eventos**, sem omissão de sementes determinísticas. O TCL oficial de C não gera NAM; a ausência de NAM nesses cinco casos é esperada. Logs vazios nos cenários sem impressão de contadores também são esperados. Existem 35 ficheiros NAM, um por execução dos outros sete cenários.

## Tabelas e unidades

- `resumo.csv/json`: médias da semente 7 no intervalo `[2,14[` s.
- `<cenário>/series.csv`: séries por segundo usadas nos gráficos.
- `multissementes/metricas.csv/json`: médias individuais das 40 execuções.
- `multissementes/estatisticas.csv/json`: média, desvio-padrão amostral e extremos das cinco sementes por métrica/fluxo/interface.
- `multissementes/validacao.csv/json`: contagem UDP gerada, recebida e descartada em cada execução e resultado das verificações.
- `awk_oficial/*.gr`: valores extraídos pelos AWK do docente, usando a proteção contra divisão por zero na cópia de `bw.awk`.

`bw_bps` e `dest_bps` usam bits/s; `loss_pps` usa pacotes/s. `fid` identifica o fluxo e `type=ack` distingue confirmações TCP. Uma chave ausente equivale a zero nessa métrica/janela. Não se somam receções em vários saltos para calcular entrega fim a fim.

`ci95_halfwidth` em `estatisticas` é um cálculo t exploratório com 4 graus de liberdade. O relatório apresenta desvio-padrão e mínimo–máximo observado, sem confundir esse intervalo com um intervalo de confiança.

## Registos e integridade

- `versoes.txt`: versões observadas no contentor.
- `compilacao.log`, `verificacao.log`, `multissementes_execucao.log`: registos da preparação experimental anterior à submissão.
- `equivalencia_c4.log`: confirmação de que a simplificação do código C.4 preservou os 15 traces medidos.
- `validacao/VALIDACAO.md`: síntese da auditoria final.
- `validacao/reproducao_integral.log`: execução independente das mesmas 40 configurações durante a validação da entrega.
- `validacao/reproducao_comparacao.json`: comparação dos traces e resultados originais com a reprodução.
- `validacao/auditoria_traces.log`: recálculo independente dos dados a partir dos 40 traces incluídos.
- `validacao/visualizacao.json`: validação do PDF e das figuras.
- `validacao/MANIFESTO_SHA256.json`: hashes dos ficheiros finais, excluindo o próprio manifesto.
- `validacao/ESTRUTURA_COMPLETA.txt`: árvore integral da entrega.

Os ficheiros experimentais fornecidos foram copiados sem alterar os seus bytes. As novas verificações guardam registos separados e não substituem as medições. Para repetir sem sobrescrever a evidência entregue, seguir o procedimento do README numa cópia sem a pasta de resultados.
