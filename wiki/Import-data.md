# New academic year imports

## Student data from the Registrar
Ask the Registrar (Debi Tuttle) to export the list of undergrad students to import into Donut.
It is a TSV file with the following columns:
```
"FULL_NAME"	"LAST_NAME"	"FIRST_NAME"	"MIDDLE_NAME"	"UID"	"GENDER"	"BIRTH_DATE"	"OPTION"	"OPTION2"	"YOS"	"MSC"	"PHONE_NUMBER"	"EMAIL"	"LINE1"	"LINE2"	"LINE3"	"CITY"	"STATE"	"ZIP"	"COUNTRY"	"HOUSE_AFFILIATION_1"	"HOUSE_AFFILIATION_2"	"HOUSE_AFFILIATION_3"	"NICK_NAME"
```
It can be imported with the following script (supposing the file is named `ascit_200911.txt`):
```
donut/modules/directory_search/utils/import_registrar.py ascit_200911.txt
```
Check that the data (both new and existing students) looks alright in dev!
Then import the data to the prod environment by running the script again with `-e prod` added to the end.

## Update `ug-*` groups

Once the new student data is imported, update the memberships of the `ug` and `ug-*` groups with the following script:
```
donut/modules/directory_search/utils/update_ug_groups.py
```
As before, check the data in dev, and then run again with `-e prod`.

TODO: other steps

# Course list

The Registrar (Debi Tuttle) exports the course schedule for each term, as well as periodic updates before add day.
Whoever is responsible for importing the course data each year should ask her to send the exports to them.

The export is a TSV file with the following format (and sometimes additional columns):
```
"Course Number"	"Course Name"	"Department"	"Instructor"	"Grades"	"Units"	"Section Number"	"Times"	"Locations"
```
(The importer ignores the `Department` column, but imports all the others.)
Each meeting time of each section is listed in a separate row, e.g.:
```
"Ch 041A"	"Organic Chemistry"	"Ch"	"Grubbs, R"	""	"4-0-5"	"01"	"W 15:00 - 15:55"	"A"
"Ch 041A"	"Organic Chemistry"	"Ch"	"Grubbs, R"	""	"4-0-5"	"01"	"MWF 09:00 - 09:55"	"A"
"Ch 041A"	"Organic Chemistry"	"Ch"	"Grubbs, R"	""	"4-0-5"	"02"	"MWF 09:00 - 09:55"	"A"
"Ch 041A"	"Organic Chemistry"	"Ch"	"Grubbs, R"	""	"4-0-5"	"02"	"W 20:00 - 20:55"	"A"
"Ch 041A"	"Organic Chemistry"	"Ch"	"Grubbs, R"	""	"4-0-5"	"03"	"R 15:00 - 15:55"	"A"
"Ch 041A"	"Organic Chemistry"	"Ch"	"Grubbs, R"	""	"4-0-5"	"03"	"MWF 09:00 - 09:55"	"A"
"Ch 041A"	"Organic Chemistry"	"Ch"	"Grubbs, R"	""	"4-0-5"	"04"	"R 20:00 - 20:55"	"A"
"Ch 041A"	"Organic Chemistry"	"Ch"	"Grubbs, R"	""	"4-0-5"	"04"	"MWF 09:00 - 09:55"	"A"
```
It is fine if there are additional columns; the importer will ignore them.

If the export is an update of a term's course schedule, I recommend `diff`ing it against the previous version as a quick check.
For example, sometimes an export is accidentally made for the wrong term, or is clearly missing courses.
**It is especially bad if courses are missing, since they will be dropped from all students' schedules and planners on Donut.**
Here is an example `diff` command:
```
diff -u donut_courses_FA2020-21_200819.txt donut_courses_FA2020-21_200911.txt
```

If the export file looks correct, it can be imported with the following script (supposing the file is named `donut_courses_FA2020-21_200911.txt`):
```
donut/modules/courses/utils/import_registrar.py donut_courses_FA2020-21_200911.txt 2020 FA
```
(Here `FA` represents "fall term" and `2020` is the year the term is in. Note that `WI2020-21` and `SP2020-21` would use year *2021* instead.)
It will print `New course: ...` for each course from the export file that was added to the term, and `Updated course: ...` for each course in the export that already exists (even if none of its fields changed).
If any courses or course sections for the term were removed because they were not in the export, it will also print how many were removed.
It's rare for there to be more than about 10 removed courses/sections; **if your numbers seem high, double-check the export before importing to prod**.

In the dev environment, search the scheduler for a few courses that were added or updated, and check that their information is correct!
Then import the data to prod by running the script again with `-e prod` added to the end.