.PHONY: setup demo generate analyze report test clean

setup:
	python -m pip install --upgrade pip
	pip install -e .

generate:
	python -m careroute.cli generate --referrals 6000 --days 180 --seed 42

analyze:
	python -m careroute.cli analyze

report:
	python -m careroute.cli report

demo:
	python -m careroute.cli demo --referrals 6000 --days 180 --seed 42

test:
	python -m unittest discover -s tests

clean:
	python -m careroute.cli clean
