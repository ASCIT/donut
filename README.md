# donut-python [![Build Status][travis-image]][travis-url]
The repository for Donut. Written using Python/Flask and powered by PostgreSQL.

# Setting up your environment
- You should already have SSH access to the development server.
- Clone the repository:
```
git clone https://github.com/ASCIT/donut-python.git ~/donut
```
- Set up your virtualenv:
```
cd ~/virtualenvs
virtualenv donut
source ~/virtualenvs/donut/bin/activate
```
The last command activates the virtualenv, so that your python packages are managed on a per-project basis by the virtual environment instead of using the global python installation. You may want to create an alias in your `~/.bashrc` file since this must be executed every time you want to start development. If you want to leave the virtual environment, use the `deactivate` command.
- Install the required packages using pip:
```
pip install -r requirements.txt
```
- You will also need a separate `config.py` file that we will give you in order to access the database (it is not included in the repository for obvious reasons). Place it in the `donut/Donut` module.

# Testing
- The easiest way to set up a test site is to use SSH port forwarding, so that requests to your local computer are forwarded to the development server. For example:
```
ssh -L 9001:localhost:5000 <host>
```
This will forward your local port 9001 so that visiting [localhost:9001](localhost:9001) on your local computer is equivalent to visiting [localhost:5000](localhost:5000) on the remote server. Flask's debugging environment defaults to port 5000, but you can change that in your `config.py` file (multiple people cannot simultaneously bind to the same port through SSH port forwarding).
- Now, execute:
```
python run_server.py
```
to start the test site. You can visit the test site by going to [localhost:9001](localhost:9001) in your local browser.
- To run the automated test suite:
```
py.test .
```

[travis-url]: https://travis-ci.org/ASCIT/donut-python
[travis-image]: https://travis-ci.org/ASCIT/donut-python.svg?branch=master
