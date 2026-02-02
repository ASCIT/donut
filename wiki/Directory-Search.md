Generally based on the legacy directory search.
The database is organized much more simply in the rewrite, so that single pieces of user information are stored in the `members` table, rather than requiring lots of joins to other tables.

## Functionality
- Can search by a variety of different query terms
  - Mostly the same as on legacy
  - Removed search by ZIP code because it was creepy
  - Hadn't yet gotten groups working so that is not yet implemented
  - Added search by graduation year
- Support for setting preferred name, custom gender, and profile picture, although these does have the potential to be abused, so we may want to add restrictions
- Click on your username to see your own directory page
- Scripts for exporting legacy data as CSV files and importing it into the new database (`donut/modules/directory_search/utils/export_legacy.py` and `donut/modules/directory_search/utils/import_legacy.py`)

## SQL tables
In `donut.sql`:
### members
|Column|Type|Comments|
|------|----|--------|
|user_id|`INT`|PK|
|uid|`CHAR(7)`|e.g. `1418702`, required to be unique|
|last_name|`VARCHAR(255)`|
|first_name|`VARCHAR(255)`|
|preferred_name|`VARCHAR(255)`|Optional|
|middle_name|`VARCHAR(255)`|Optional|
|email|`VARCHAR(255)`|e.g. `csander@caltech.edu`|
|phone|`VARCHAR(64)`|e.g. `6261112222`, optional|
|gender|`TINYINT`|Overridden by `gender_custom`, specified in `donut/constants.py`, optional|
|gender_custom|`VARCHAR(32)`|Optional|
|birthday|`DATE`|Optional|
|entry_year|`YEAR(4)`|Optional|
|graduation_year|`YEAR(4)`|Optional|
|msc|`SMALLINT`|Optional|
|building_id|`INT`|References `buildings.building_id`, optional|
|room|`VARCHAR(5)`|Non-numeric to allow for things like `200A`, optional|
|address|`VARCHAR(255)`|Home street address, optional|
|city|`VARCHAR(64)`|Hometown, optional|
|state|`VARCHAR(64)`|Home state, not sure why we allow more than 2 chars, optional|
|zip|`VARCHAR(9)`|Home zip code, optional|
|country|`VARCHAR(64)`|Home country, optional (if unknown or USA)|
|create_account_key|`CHAR(32)`|Unused by directory search|

### buildings
|Column|Type|Comments|
|------|----|--------|
|building_id|`INT`|PK|
|building_name|`VARCHAR(100)`|e.g. `Ruddock House` or `Chester Housing [150 S. Chester Ave.]`|, required to be unique

### options (majors and minors)
|Column|Type|Comments|
|------|----|--------|
|option_id|`INT`|PK|
|option_name|`VARCHAR(50)`|Required to be unique|

### users
|Column|Type|Comments|
|------|----|--------|
|user_id|`INT`|PK, references `members.user_id`|
|username|`VARCHAR(32)`|Required to be unique|
|...|...|Unused by directory search|

### groups (so far only used for houses)
|Column|Type|Comments|
|------|----|--------|
|group_id|`INT`|PK|
|group_name|`VARCHAR(32)`|Required to be unique|
|type|`VARCHAR(255)`|`house` for houses|
|...|...|Unused by directory search|

In `directory.sql`:
### images
|Column|Type|Comments|
|------|----|--------|
|user_id|`INT`|References `members.user_id`, required to be unique (i.e. one pic per user)|
|extension|`VARCHAR(5)`|E.g. `jpg`, used for setting `Content-Type` header|
|image|`MEDIUMBLOB`|File contents|