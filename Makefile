fresh-install: venv pip-install

venv:
	mkdir -p ~/virtualenvs
	virtualenv -p /usr/local/bin/python3.6 ~/virtualenvs/donut-py3
	echo "# Virtualenv\nsource ~/virtualenvs/donut-py3/bin/activate" >> ~/.profile

pip-install:
	pip install -r requirements.txt

test:
	python -m pytest .
