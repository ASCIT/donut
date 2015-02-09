# donut-python [![Build Status][travis-image]][travis-url]
The repository for Donut.

# Initial set-up
First, you need to set up virtualenv:
```
$ cd donut-python
$ virtualenv env
$ . env/bin/activate
```

At this point, your python and pip paths should be in this virtualenv. To verify, type `which pip`.

Install the necessary packages using pip:

```
$ pip install -r requirements.txt
```

# Quick reference instructions
- Whenever you want to work on the project, you need to start the virtualenv: `$ . env/bin/activate`
- To start the server locally: `$ python run_server.py`
- To run the test suite: `$ py.test .`

[travis-url]: https://travis-ci.org/ASCIT/donut-python
[travis-image]: https://travis-ci.org/ASCIT/donut-python.svg?branch=master
