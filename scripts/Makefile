PYTHON ?= python3
TECTONIC ?= tectonic

.PHONY: help ambiente simular awk sementes figuras relatorio verificar verificar-dados reproduzir

help:
	@echo 'make -f scripts/Makefile relatorio       Recompila o PDF a partir dos dados compactos entregues'
	@echo 'make -f scripts/Makefile verificar-dados Confere a consistência dos resultados entregues (sem traces)'
	@echo 'make -f scripts/Makefile reproduzir      Executa as 40 simulações, análises e compilação completas'
	@echo 'make -f scripts/Makefile verificar       Verifica também os traces locais da semente 7'

ambiente:
	docker build -t tp4-qos-ns2 -f Dockerfile .

simular:
	bash scripts/executar.sh

awk:
	bash scripts/awk_oficiais.sh

sementes:
	$(PYTHON) scripts/multissementes.py

figuras:
	$(PYTHON) scripts/figuras_compactas.py

relatorio: figuras
	$(PYTHON) scripts/relatorio.py
	$(TECTONIC) --keep-logs relatorio/main.tex
	mv relatorio/main.pdf Relatorio_Grupo7.pdf

verificar-dados:
	$(PYTHON) scripts/verificar_entrega.py

verificar:
	$(PYTHON) scripts/verificar.py
	$(PYTHON) scripts/verificar_entrega.py

# Dependências sequenciais: evitar misturar leituras/escritas mesmo com make -j.
reproduzir:
	$(MAKE) -f scripts/Makefile simular
	$(MAKE) -f scripts/Makefile awk
	$(MAKE) -f scripts/Makefile sementes
	$(MAKE) -f scripts/Makefile relatorio
	$(MAKE) -f scripts/Makefile verificar
