|URL Extension|Description|
|-------------|-----------|
|/1/groups|Returns a JSON of the list of groups|
|/1/members|Returns a JSON of all registered members|
|/1/members/<user_id>|Returns a JSON object describing the member whose ID is the specified id|
|/1/organizations|Returns a JSON object describing all organizations|
|/1/organizations/<org_id>|Returns a JSON describing the organization whose id is the specified ID|

## Examples
http://localhost:9001/1/members/  Returns a JSON of all members:

[{"first_name": "Rahul", "last_name": "Bachal", "user_id": 1, "uid": "1957722", "entry_year": null, "graduation_year": null, "email": " rbachal@caltech.edu"}, {"first_name": "Robert", "last_name": "Eng", "user_id": 2, "uid": "1984853", "entry_year": null, "graduation_year": null, "email": " reng@caltech.edu"}, ...]

If we want to look at a particular member, we find their id for example:

http://localhost:9001/1/members/1/ Will give you a page with just member with ID 1:

{"first_name": "Rahul", "last_name": "Bachal", "user_id": 1, "uid": "1957722", "entry_year": null, "graduation_year": null, "email": " rbachal@caltech.edu"}