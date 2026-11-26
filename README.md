# QoSI — TP4 | Grupo 7

Universidade do Minho · 2026/2027

Neste trabalho usámos o NS-2 para estudar o que acontece quando vários clientes partilham uma ligação sem capacidade para todo o tráfego. Comparámos DropTail, RED e DiffServ e implementámos uma política para dar a cada cliente 30% da capacidade, permitindo aproveitar o que estiver livre.

Testámos tráfego CBR, FTP e voz. No total, corremos oito cenários com cinco sementes diferentes, ou seja, 40 simulações. Os resultados e a análise estão no [relatório](Relatorio_Grupo7.pdf).

## Ficheiro para submeter no Blackboard

[Descarregar QoSI_TP4_Grupo7.zip](https://github.com/Andrebottari/qosi-tp4-2026-2027/releases/download/entrega-tp4/QoSI_TP4_Grupo7.zip)

## Organização

```text
Relatorio_Grupo7.pdf   Relatório final
Dockerfile            Ambiente com NS-2.35
scripts/              Simulações, análise dos dados e verificações
originais/            Enunciado e scripts fornecidos pelo professor
resultados/           Traces, tabelas e logs das simulações
figuras/              Gráficos completos e os usados no relatório
relatorio/            Código LaTeX do relatório
```

A pasta `originais/` é usada pelos scripts, por isso deve ser mantida.

## Como executar

É preciso ter Docker, Python 3 e Make instalados. O Docker deve estar a correr. Para gerar o PDF também é necessário ter o Tectonic.

Na raiz do projeto, instalamos as dependências Python:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r scripts/requirements.txt
```

Para repetir tudo sem substituir os resultados que estão no repositório, criamos uma pasta de trabalho:

```bash
TP4_REPRO=$(mktemp -d)
cp -a Dockerfile scripts originais figuras relatorio "$TP4_REPRO/"
mkdir "$TP4_REPRO/resultados"
(
  cd "$TP4_REPRO"
  make -f scripts/Makefile reproduzir
)
printf 'Resultados da reprodução: %s\n' "$TP4_REPRO"
```

Este comando prepara o ambiente Docker, executa as 40 simulações, trata os dados, gera os gráficos e compila o relatório. Na primeira execução é necessária ligação à Internet para descarregar as dependências. Os traces ocupam algumas centenas de MB.

Dentro da cópia de trabalho, para voltar a gerar apenas o relatório:

```bash
make -f scripts/Makefile relatorio
```

## Cenários

- **A:** seis fontes CBR, primeiro com DropTail e depois com RED.
- **B:** CBR, FTP e voz, com janelas TCP de 20 e 128 pacotes.
- **C:** DiffServ com a configuração fornecida pelo professor.
- **C.4:** a nossa política Token Bucket/WRR, testada com carga normal, um único cliente ativo e um cliente a enviar acima da taxa contratada.

Usámos as sementes 7, 11, 23, 41 e 97. As médias foram calculadas entre os 2 e os 14 segundos. Os dados da semente 7 estão nas pastas de cada cenário; as restantes estão em `resultados/multissementes/`.

## Verificar os resultados

Para conferir os resumos e as estatísticas já guardados, sem repetir as simulações:

```bash
python3 scripts/verificar_entrega.py
```

Para verificar também a integridade dos ficheiros e recalcular as métricas a partir dos 40 traces:

```bash
python3 scripts/validar_submissao.py
```
