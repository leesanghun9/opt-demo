# .PHONY: venv run clean test setup help locust test_cov

VENV := venv
PYTHON := $(VENV)/bin/python3
PORT := 8080
TEST_PATH = ./testing


setup: requirements.txt
	python3 -m venv $(VENV)
	. $(VENV)/bin/activate && \
	./$(VENV)/bin/pip install --upgrade pip && \
	./$(VENV)/bin/pip install -r requirements.txt

run: setup
	. $(VENV)/bin/activate && \
	streamlit run main.py --server.port $(PORT) --server.address=0.0.0.0 --logger.level=info

# pytest-deploy: setup
# 	. $(VENV)/bin/activate && \
# 	python -m pytest -v -s

# test_cov: setup
# 	. $(VENV)/bin/activate && \
# 	pytest --cov --cov-report html --cov-report term

# locust: setup
# 	. $(VENV)/bin/activate && \
# 	cd $(TEST_PATH) && \
# 	locust --host=http://localhost:$(PORT)

kill_port:
	kill -9 $(lsof -ti tcp:$(PORT))

clean:
	find . -name "__pycache__" -o -name "*.pyc" | xargs rm -rf
	rm -rf $(VENV)

lint:
	black src/*

help:
	@echo "make setup"
	@echo "       >> creates virtual environment and install dependencies"
	@echo "make run"
	@echo "       >> runs app"
	@echo "make pytest"
	@echo "       >> runs pytest"
	@echo "make pytest-deploy"
	@echo "       >> runs pytest for continuous integration pipeline"
	@echo "make test_cov"
	@echo "       >> runs test coverage"
	@echo "make locust"
	@echo "       >> runs locust for stress testing"
	@echo "make lint"
	@echo "       >> run pylint and mypy (to be done)"
	@echo "make kill_port"
	@echo "       >> kills app port (5000 by default, add '-e PORT= ' to set another port)"
	@echo "make clean"
	@echo "       >> deletes temportary files and virtual enviornments"
	@echo "make lint"
	@echo "       >> Reformats code via Black"