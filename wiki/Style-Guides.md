# Python - YAPF
- We use YAPF, an automatic code formatter. We use the default PEP-8 setting.
- https://github.com/google/yapf
- cd to the donut directory with the Makefile (`~/donut`) and run with `make lint`.

# Javascript
- TODO

# SQL
### DDL
#### Enums
- Use Python 3 enums in backend, populate with Python script if necessary
- Use `VARCHAR` in SQL and back with string `enum` in Python
    ```python
    '''constants.py'''
    from enum import Enum
    class Color(Enum):
        RED = 'Red'
        GREEN = 'Green'
    ```

### Creating SQL statements
- TODO

### Transactions
- TODO