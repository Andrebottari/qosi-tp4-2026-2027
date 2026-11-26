# Validação final da submissão — QoSI TP4, Grupo 7

## Resultado

**Validação do conteúdo concluída sem ficheiros obrigatórios em falta, divergências experimentais ou falhas de reprodução.** O PDF de submissão não foi modificado. Os scripts e fontes foram adaptados apenas aos caminhos da estrutura solicitada.

## Verificações efetuadas

| Verificação | Resultado e evidência |
|---|---|
| Relatório final | Sete páginas, classe LNCS. PDF na raiz idêntico em SHA-256 à versão final aprovada. |
| Conteúdo científico | LaTeX difere apenas na localização relativa das figuras (`../figuras/`); texto e tabelas preservados. |
| Originais do docente | Enunciado e cinco TCL/AWK fornecidos preservados byte a byte face aos originais locais. |
| Completude experimental | Oito cenários × sementes 7, 11, 23, 41, 97: 40 traces e 40 logs de execução presentes. |
| Traces e tabelas | Recálculo independente das métricas dos 40 traces, comparação com JSON/CSV e séries da semente 7: coincidência. |
| Conservação UDP | Gerados = recebidos + descartados em todas as execuções; comparação com as contagens guardadas. |
| Capacidade/quotas | Capacidade dos enlaces, quotas e empréstimo C.4 verificados; ausência de descartes conformes em normal/abuso. |
| Valores do relatório | Padrão DropTail, débitos FTP, mínimo C.4 e contadores por CP de C conferidos com os dados. |
| Reprodução integral | Cópia separada sem resultados; execução do procedimento documentado com as mesmas 40 configurações. |
| Equivalência da reprodução | SHA-256 dos 40 traces descomprimidos idêntico ao das execuções entregues. Resumos e estatísticas também idênticos. |
| Compilação | LaTeX compilado no novo esquema de pastas; sete páginas; sem referências indefinidas, rótulos duplicados ou caixas a ultrapassar margens. |
| Apresentação | Sete páginas renderizadas idênticas píxel a píxel após recompilação; 12 PDFs e 12 PNGs de gráficos legíveis e revistos. |
| Sintaxe/dependências | Python e shell verificados; TCL executados na reprodução; classe e bibliografia LNCS incluídas. |
| Ficheiros gzip | Todos os traces e NAM comprimidos lidos integralmente, verificando a integridade gzip. |
| Organização | Uma cópia do relatório, um Dockerfile e uma pasta de figuras. Sem Git, caches, dependências instaladas, imagens Docker ou material privado. |

## Registos

- `reproducao_integral.log`: construção/execução/análise/compilação/verificação na cópia limpa.
- `reproducao_comparacao.json`: hashes dos 40 traces e equivalência com os resultados entregues.
- `auditoria_traces.log`: recálculo independente, sem alteração dos dados.
- `consistencia_relatorio.json`: verificações de valores concretos apresentados no relatório.
- `visualizacao.json`: páginas e figuras verificadas.
- `MANIFESTO_SHA256.json`: hashes relativos de todos os ficheiros finais, exceto o próprio manifesto.
- `ESTRUTURA_COMPLETA.txt`: lista hierárquica integral da entrega.

Após criar o ZIP, são adicionalmente verificados o CRC dos seus membros, a extração efetiva e os hashes dos ficheiros extraídos. O tamanho e SHA-256 do ZIP são registados no comprovativo final exterior ao arquivo, evitando uma referência circular do arquivo ao seu próprio hash.

## Ausências esperadas e limitações declaradas

- O cenário C oficial não gera NAM. Estão incluídos os 35 NAM das outras sete configurações e todos os 40 traces de eventos.
- Alguns logs são vazios porque o respetivo cenário não imprime contadores; não são execuções em falta.
- Alguns resultados determinísticos coincidem entre sementes. Os ficheiros permanecem associados às respetivas execuções para preservar a evidência das 40 repetições.
- O sistema de instalação requer Internet na primeira obtenção da imagem/pacotes e dos recursos TeX. O arquivo não inclui imagens Docker nem bibliotecas instaladas, conforme solicitado.
- A imagem-base está fixada por digest; os repositórios APT não estão congelados temporalmente. A reprodução foi validada com as versões documentadas em Linux x86_64.
- As limitações científicas existentes (duração, pacotes iguais em C.4, ausência de atraso/jitter) continuam explicitadas no relatório e não foram alteradas nesta preparação.
