fresh-install: venv pip-install

venv:
	mkdir -p ~/virtualenvs
	virtualenv -p /usr/local/bin/python3.6 ~/virtualenvs/donut-py3
	echo "# Virtualenv\nsource ~/virtualenvs/donut-py3/bin/activate" >> ~/.profile

pip-install:
	. ~/virtualenvs/donut-py3/bin/activate; \
	pip install -r requirements.txt

lint:
	yapf -i -r .

test:
	python3 -m pytest .

test-db:
	mysql -u donut_test --password=public < sql/reset.sql
