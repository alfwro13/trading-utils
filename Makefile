# Define where our tools are located inside the virtual environment
VENV_BIN=./venv/bin
PYTHON=$(VENV_BIN)/python3
PIP=$(VENV_BIN)/pip

.SILENT: ;

setup: ## Create environment and install everything
	# 1. Create the virtual environment if it doesn't exist
	test -d venv || python3 -m venv venv
	# 2. Upgrade the basic tools
	$(PYTHON) -m pip install --upgrade pip setuptools wheel
	# 3. Install the project requirements
	$(PIP) install -r requirements/dev.txt
	$(PIP) install -r requirements.txt
	echo "Setup complete! Use 'source venv/bin/activate' to start."

deps: ## Update dependencies
	$(PIP) install -r requirements.txt

ftplist: ## Download stock list
	$(PYTHON) download_stocklist.py

stocksohlcv: ## Download stock data
	$(PYTHON) download_stocks_ohlcv.py

etfsohlcv: ## Download ETF data
	$(PYTHON) download_macro_etfs.py

enrich: ## Calculate indicators
	$(PYTHON) stocks_data_enricher.py

weekend: ftplist stocksohlcv etfsohlcv enrich ## Run full weekend analysis

clean: ## Remove temporary files
	find . -type d -name '__pycache__' | xargs rm -rf
	rm -rf venv build dist

.PHONY: help setup deps weekend clean
.DEFAULT_GOAL := help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
