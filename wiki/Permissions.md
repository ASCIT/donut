## How do permissions work? ##
Each permission is assigned an id and that id is associated with a position. Everyone who either (a) holds one of the positions linked to the permission id, (b) holds a position linked (via `position_relations`) to a position associated with this permission, or (c) holds the admin permission is defined to hold the permission.

## How do I add a permission? ##
Permissions are added by inserting them into the database. First, you need to create a row in `permissions`. This will assign a permission_id to the permission, and should store the type of permission, resource name, and a short description of the permission. Then you need to assign the permission to positions. This is done by adding rows to the `position_permissions` table.

## How should I refer to permissions in my code? ##
To avoid littering our code with 'magic numbers' that correspond to permission id's, we use Enum's to give names to the permission id's. There is one global enum -- `donut.default_permissions.Permissions` which should be used to store id's for permissions that are general to the whole site (site admin, for instance). If a permission is module specific, then you should create a permissions enum in your module to store the permissions.  

## How should I check if the user has a permission? ##
You should pass the username (stored in Flask session) and permission_id (from a permissions enum) into 

`check_permission(username, permission_id)`

This will return True or False. 
If you want to get a list of a user's permissions, you can also call

`get_permissions(username)`

Note that if `default_permissions.ADMIN` (i.e. permission_id 1) is in this list, it is implied that the user also has all other permissions. `check_permission` takes this into account and always returns True for site admins. 
Both of these functions are defined in `donut.auth_utils`