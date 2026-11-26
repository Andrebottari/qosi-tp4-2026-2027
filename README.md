# QoSI — Trabalho Prático 4 · Grupo 7

**Universidade do Minho · 2026/2027**

Entrega para avaliação e reprodução do estudo de DropTail, RED e DiffServ em NS-2.35. Inclui **oito cenários × cinco sementes = 40 execuções**, com os dados efetivamente obtidos.

## Organização

- `Relatorio_Grupo7.pdf`: relatório final LNCS, com sete páginas; conteúdo científico preservado.
- `Dockerfile`: ambiente Debian 12 com NS-2.35, gawk e Tcl 8.6.
- `scripts/`: TCL, AWK, programas Python, comandos shell, Makefile e dependências Python.
- `originais/`: enunciado e ficheiros fornecidos pelo docente, usados na preparação das simulações e na análise AWK. Esta pasta é necessária para reproduzir as experiências.
- `resultados/`: traces, séries, resumos, saídas AWK, contadores e logs das execuções.
- `figuras/`: gráficos completos e compactos, em PDF e PNG.
- `relatorio/`: fontes LaTeX, preâmbulo e dependências LNCS específicas.

O relatório existe apenas na raiz. As figuras existem apenas em `figuras/`. Não estão incluídos o manual privado, histórico Git, imagens Docker, ambientes instalados, caches ou auxiliares de compilação. Resultados iguais entre algumas sementes determinísticas são evidência de execuções distintas, não cópias adicionais de entrega.

## Requisitos e instalação

Para consultar a entrega basta um leitor de PDF. Para verificar os dados compactos basta Python 3.10 ou superior. Para reproduzir: Linux/POSIX, Bash, GNU Make, Docker com o serviço ativo e acessível ao utilizador, Python 3 com Matplotlib e Tectonic para compilar o LaTeX.

Foram utilizados Python 3.14.4, Matplotlib 3.10.7, Tectonic 0.17.0 e NS-2 `2.35+dfsg-5`. As versões dos pacotes do contentor estão em `resultados/versoes.txt`.

Na raiz extraída:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r scripts/requirements.txt
docker build -t tp4-qos-ns2 -f Dockerfile .
```

Instalar Docker, Make, Python e Tectonic previamente pelos mecanismos adequados ao sistema. É necessária ligação à Internet na primeira instalação/construção para descarregar pacotes Debian, a imagem-base e recursos LaTeX. Não é necessário clonar ou consultar qualquer repositório GitHub. O digest fixa a imagem-base; o APT não é um arquivo temporal congelado dos pacotes.

## Verificar a entrega existente

Sem executar novas simulações:

```bash
python3 scripts/verificar_entrega.py
python3 scripts/verificar.py
python3 scripts/validar_submissao.py
```

O último comando verifica os hashes da entrega, a integridade dos ficheiros comprimidos e recalcula as métricas das 40 execuções a partir dos traces, comparando-as com os resultados incluídos. Pode demorar mais do que a verificação dos resumos. Não altera os resultados.

O relatório completo da validação da submissão está em `resultados/validacao/VALIDACAO.md`; a lista integral de ficheiros, em `resultados/validacao/ESTRUTURA_COMPLETA.txt`.

## Reproduzir integralmente, preservando os resultados entregues

A reprodução deve decorrer numa cópia de trabalho sem os resultados anteriores. O comando seguinte cria-a numa pasta temporária e executa as mesmas 40 configurações, sem acrescentar cenários nem sementes:

```bash
TP4_REPRO=$(mktemp -d)
cp -a Dockerfile scripts originais figuras relatorio "$TP4_REPRO/"
mkdir "$TP4_REPRO/resultados"
(
  cd "$TP4_REPRO"
  make -f scripts/Makefile reproduzir
)
printf 'Reprodução guardada em: %s\n' "$TP4_REPRO"
```

O ambiente virtual, se utilizado, deve continuar ativo. A execução cria traces volumosos, mas não modifica a rede real do computador. Reserve espaço para a entrega extraída e a cópia de reprodução. A pasta temporária não é removida automaticamente, permitindo inspecionar os resultados.

Etapas equivalentes, **dentro dessa cópia de trabalho**:

```bash
bash scripts/executar.sh
bash scripts/awk_oficiais.sh
python3 scripts/multissementes.py
python3 scripts/figuras_compactas.py
python3 scripts/relatorio.py
tectonic --keep-logs relatorio/main.tex
mv relatorio/main.pdf Relatorio_Grupo7.pdf
python3 scripts/verificar.py
python3 scripts/verificar_entrega.py
```

`multissementes.py` reutiliza traces existentes. A cópia sem resultados garante uma repetição efetiva de todas as execuções. Não misturar resultados de configurações diferentes. O texto analítico do relatório é específico dos ensaios entregues; não é automaticamente reinterpretado quando se alteram parâmetros.

## Recompilar apenas o relatório

Também numa cópia de trabalho, para preservar o PDF final:

```bash
make -f scripts/Makefile relatorio
```

O alvo usa os dados já existentes, regenera as figuras compactas e o LaTeX e compila o PDF na raiz. Não requer simular novamente. Alternativamente, após gerar o LaTeX, executar `pdflatex main.tex` duas vezes dentro de `relatorio/`, com os pacotes TeX adequados. Os ficheiros LNCS específicos estão incluídos; os pacotes TeX comuns são fornecidos pela instalação TeX/Tectonic.

## Cenários, sementes e medição

| Cenário | Configuração |
|---|---|
| `A_droptail` | Seis CBR/UDP a 3 Mbps; DropTail |
| `A_red` | Mesma carga; RED nas entradas do backbone |
| `B_referencia` | CBR, FTP e voz; janela TCP original de 20 pacotes |
| `B_misto` | Mesmas aplicações; janela TCP de 128 pacotes |
| `C_diffserv` | Política original de `qos1.tcl` |
| `C4_normal` | Token Bucket/WRR; três clientes a 3 Mbps por lado |
| `C4_livre` | Mesma política; um cliente ativo a 5 Mbps por lado |
| `C4_abuso` | Mesma política; ofertas 4,5/1,5/1,5 Mbps por lado |

Sementes: **7, 11, 23, 41 e 97**. Os oito diretórios de primeiro nível em `resultados/` contêm a semente 7, com `out.tr`, CSV e log. As restantes sementes estão em `resultados/multissementes/<semente>/<cenário>/`, com `out.tr.gz` e log. Todos os 40 traces estão presentes; os NAM são incluídos nos cenários que os geraram. O cenário C original não produz NAM.

As médias usam `[2,14[` s; as séries usam intervalos de 1 s. `resumo.csv/json` refere-se à semente 7; `multissementes/metricas.csv/json`, às 40 execuções; `estatisticas.csv/json`, às cinco sementes. Um log vazio é normal nos cenários sem impressão de contadores. Ausência de uma chave de métrica corresponde a zero nessa janela.

`bw_bps` mede receção numa interface, `dest_bps` na ligação final e `loss_pps` descartes por segundo. TCP inclui cabeçalhos e eventuais retransmissões; não é goodput. ACKs entram na utilização da ligação e estão separados pelo tipo no CSV. O intervalo mínimo–máximo da tabela de robustez não é um intervalo de confiança. A coluna t de Student nos dados é exploratória, não uma garantia.

As cópias de trabalho corrigem o nome `packetSize_` do CBR, atribuem FIDs próprios aos FTP e explicitam buffers de 50 pacotes. A cópia `scripts/awk/bw.awk` evita divisão por zero numa janela final vazia; o AWK original está intacto. `loss.awk` é usado diretamente de `originais/files/`, evitando uma cópia idêntica. Os AWK agregam/janelam de forma ligeiramente diferente dos gráficos Python; as interfaces e fronteiras devem ser consideradas ao comparar valores.

A fonte dos gráficos é o trace NS-2. Não se mediram atraso/jitter. As limitações científicas, escolhas de parâmetros e análise constam do relatório, que não foi alterado nesta preparação. A validação informa separadamente qualquer limitação de ambiente ou inconsistência.
