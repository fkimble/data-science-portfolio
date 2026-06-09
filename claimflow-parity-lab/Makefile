.PHONY: setup demo generate analyze report test clean

setup:
	python -m pip install --upgrade pip
	pip install -e .

generate:
	python -m claimflow.cli generate --patients 5000 --days 180 --seed 42

analyze:
	python -m claimflow.cli analyze

report:
	python -m claimflow.cli report

demo:
	python -m claimflow.cli demo --patients 5000 --days 180 --seed 42

test:
	python -m unittest discover -s tests

clean:
	python -m claimflow.cli clean
