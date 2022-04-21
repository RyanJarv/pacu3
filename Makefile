
mypy:
	mypy --show-error-codes --show-error-context pacu

test:
	python -m pytest .
