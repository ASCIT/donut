We use [pytest](https://docs.pytest.org/en/3.2.2/) as our test framework. <br/>
`make test` searches for files in the form `test_*.py` and runs functions
in the form `test_*` <br/>
(You can have helper functions not named test).

## Fixtures
Pytest allows for fixtures that reduce the amount of boilerplate code.
The [client fixture](https://github.com/ASCIT/donut/blob/master/donut/testing/fixtures.py)
sets up Flask's application context, and sets up the database so functions will run.
It also wraps each test function in a transaction that is rolled back after the function
completes.

To use the client fixture simply import it and write your function as `test_my_function(client)`.

## Database
The client fixture above is set up to use the test database. <br/> Changes to the test database
should be made in a separate PR, like [this](https://github.com/ASCIT/donut/pull/52)

## Travis
We use [Travis](https://docs.travis-ci.com/user/for-beginners/) for continuous integration.
This means that Travis will run a build based on `.travis.yml` (see [here](https://github.com/ASCIT/donut/blob/master/.travis.yml)) for each
commit and check that all tests pass. Each time it does this it does a clean build from scratch.
Currently it installs requirements, sets up the database, runs the linter, and then runs tests.
If it fails, you will get a red x that will prevent you from merging in the PR. <br/>
You can click on the the x to link to the Travis logs to see what happened. Don't
forget to run the linter (`make lint`).

Our Travis site is [here](https://travis-ci.org/ASCIT/donut)

## Examples
- [test_core](https://github.com/ASCIT/donut/blob/master/tests/modules/core/test_core.py)