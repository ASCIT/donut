# donut-python [![Build Status][travis-image]][travis-url]
The repository for Donut.

# Instructions
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

Finally, you can start the server:

```
$ python run_server.py
```

[travis-url]: https://travis-ci.org/ASCIT/donut-python
[travis-image]: https://travis-ci.org/ASCIT/donut-python.svg
