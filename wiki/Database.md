> "Hello noobs and doobs. It is I, Sir Rahul of Donut. It is my utmost dismality to welcome you to the team of devs and of masters of artful literature. Please feel free to ping me anytime regarding sweet bagels with a hole." - Rahul Bachal, December 17, 2017

## Using the Database
The database has three users with three levels of power `ascit`, `devel`, and `root`. There are three databases: `donut`, `donut_dev`, and `donut_test`. `donut` is the live database used by the site. `donut_dev` is used by the devteam for development purposes. `donut_test` is used during testing.

### Command Line

* ```mysql -u <user> -p <database>``` to log in (`-p` denotes prompt for password)
* ```show databases;``` to show the databases.
* ```use donut_dev;``` to use the donut_dev database.
* ```show tables;``` to show all the tables in a database.
* ```mysql -u <user> -p <database> < file.sql``` to run the SQL script file.sql

## Legacy Site command line (server is no longer accessible as of 03/2020)
```psql ascit devel```

## Schema Design

[Schema Outline](https://docs.google.com/document/d/102fWgrVsm817Eku9y5tGiYJSIoTTcDzX9vIy3sSGPFc/edit?usp=sharing)

There are several principles underlying the schema design which we would like to maintain for new tables/columns:
- Design around `NATURAL JOIN`s. Because of the schema design, most queries that require combining entries in multiple tables can be written by simply `NATURAL JOIN`ing the tables involved. This requires that (1) the same column names are used for the same values in different tables and (2) tables do not otherwise have conflicting column names. For example, we would avoid a column name like `id` or `name`, as many tables are likely to have similar columns. Instead, it is preferable to prefix these names with the type of data stored in the row, e.g. use `option_id` and `option_name`.
- Avoid using multiple tables with redundant information in 1-one-1 relationships. For example, the legacy database spread the data now stored in the `members` table across several tables linked together by user ID (`inum`) or UID. This made simple queries of member data cumbersome to write because they required several (often un`NATURAL`) joins.
- Use `INT` ID columns (rather than `VARCHAR`) to make ID comparisons faster
- Be cautious when adding `NULL`able columns. There should be a clear reason why the column could be `NULL` that is not just a lack of data. This means we don't have to handle as many cases of whether data is present when querying the database.
- Use MySQL `VIEW`s to encapsulate common queries, e.g. `current_position_holders` for (in)direct position holders that are currently active, or `house_positions` for positions that represent house memberships.