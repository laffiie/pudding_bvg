.PHONY: help install test deploy ssh logs status restart stop validate find-station

VENV_DIR = .venv
PYTHON = $(VENV_DIR)/bin/python3
PIP = $(VENV_DIR)/bin/pip

help:
	@echo "🚊 BVG Abfahrtsmonitor - Make Commands"
	@echo "======================================"
	@echo ""
	@echo "Local Commands (Mac):"
	@echo "  make install        - Create venv and install dependencies"
	@echo "  make test          - Test locally (windowed mode)"
	@echo "  make validate      - Validate config.json"
	@echo "  make find-station  - Find station IDs (usage: make find-station STATION='name')"
	@echo ""
	@echo "Deployment Commands:"
	@echo "  make deploy        - Deploy to Raspberry Pi"
	@echo "  make ssh           - SSH to Raspberry Pi"
	@echo ""
	@echo "Pi Management (run after SSH):"
	@echo "  make status        - Check service status"
	@echo "  make logs          - View live logs"
	@echo "  make restart       - Restart service"
	@echo "  make stop          - Stop service"
	@echo ""

# Local development
$(VENV_DIR)/bin/activate:
	python3 -m venv $(VENV_DIR)

install: $(VENV_DIR)/bin/activate
	$(PIP) install -r requirements.txt

test: install
	$(PYTHON) main.py ./config/config.json

validate: install
	$(PYTHON) validate_config.py ./config/config.json

find-station: install
	@if [ -z "$(STATION)" ]; then \
		echo "Usage: make find-station STATION='Station Name'"; \
		echo "Example: make find-station STATION='Alexanderplatz'"; \
		exit 1; \
	fi
	$(PYTHON) find_station.py "$(STATION)"

# Deployment
deploy:
	./deploy_to_pi.sh

ssh:
	ssh pi@raspberrypi.local

# Pi management (these work when SSH'd into Pi)
status:
	sudo systemctl status bvg-display.service

logs:
	sudo journalctl -u bvg-display.service -f

restart:
	sudo systemctl restart bvg-display.service

stop:
	sudo systemctl stop bvg-display.service

start:
	sudo systemctl start bvg-display.service

enable:
	sudo systemctl enable bvg-display.service
