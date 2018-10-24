fresh-install: venv pip-install

update-packages:
	pip install --upgrade pip
	pip install -r requirements.txt

venv:
	mkdir -p ~/virtualenvs
	virtualenv -p /usr/local/bin/python3.6 ~/virtualenvs/donut-py3
	echo "# Virtualenv" >> ~/.profile
	echo "source ~/virtualenvs/donut-py3/bin/activate" >> ~/.profile

pip-install:
	. ~/virtualenvs/donut-py3/bin/activate; \
	pip install -r requirements.txt

lint:
	yapf -i -r .

test: init-test-db
	python -m pytest .

init-test-db:
	mysql -u donut_test --password=public < sql/reset.sql
