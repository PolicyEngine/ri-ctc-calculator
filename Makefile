# Makefile for RI CTC Calculator

.PHONY: help install run test format clean

help:
	@echo "RI CTC Calculator - Make commands"
	@echo ""
	@echo "  make install    Install dependencies"
	@echo "  make run        Run the Streamlit app"
	@echo "  make test       Run tests"
	@echo "  make format     Format code with black"
	@echo "  make clean      Clean up generated files"

install:
	pip install -r requirements.txt

install-dev:
	pip install -e ".[dev]"

run:
	streamlit run app.py

test:
	pytest tests/ -v

format:
	black .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/
