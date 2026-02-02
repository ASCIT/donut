The concepts of groups, positions, and position holders are used in many of Donut's features. For example, newsgroup emails are sent to all members who have a position that receives mail in the newsgroup. There is also a public "Campus Positions" page that lists all current position holders and allows users to manage the positions in the groups they control.

Groups represent campus organizations, mainly houses and committees. There is no interface currently to add new groups; this requires running a SQL query on the database.

Positions are the ways in which undergrads can belong to these groups, e.g. "Chair" or "Representative" for committees, "Full Member" or "President" for houses. Positions also grant different permissions, e.g. Devteam members have admin permissions and house secretaries can manage the list of house members for the directory. On the "Administrate" tab of the positions page, group admins (those with a `control` position) can add positions to their groups and add or remove position holders.

Position holders are undergrads that hold a position. Each hold has optional start and end dates, and multiple undergrads can hold the same position at the same time.

## SQL tables

The general relationship between the tables is:
```
                         position_relations
                               |   |
members - position_holders - positions - groups
                                 |
                         position_permissions
                                 |
                            permissions
```

We have tried to make this as general as possible. For example:
- All permissions come from positions, whereas the legacy database allowed members to have permissions directly
- All memberships in groups come from particular positions in the group
- House memberships are represented as held positions, e.g. `(group_name, pos_name) = ("Avery", "Full Member")`
- The `position_relations` table allows for "indirect" positions, e.g. the ASCIT president position also gives the administration position for all `ug-*` groups
- `position_holders` stores a historical record of all positions; usually `current_position_holders` will be used instead to get currently held positions
- `groups` is used for both campus positions and sending out emails, whereas the legacy database distinguished between "organizations" and "newsgroups"

### groups

| Column | Type | Comments |
|--------|------|----------|
| group_id | `INT` | PK |
| group_name | `VARCHAR(64)` | Distinct |
| group_desc | `VARCHAR(255)` | Optional |
| type | `VARCHAR(255)` | Currently, we have "house", "committee", and "ug-auto" |
| newsgroups | `BOOLEAN` | Can emails be sent to this group? |
| anyone_can_send | `BOOLEAN` | Can non-members send to this group? Currently only ASCIT allows this |
| visible | `BOOLEAN` | Can non-members see that this group exists? |

### positions

| Column | Type | Comments |
|--------|------|----------|
| pos_id | `INT` | PK |
| group_id | `INT` | Group this position belongs to |
| pos_name | `VARCHAR(64)` | Unique per group |
| send | `BOOLEAN` | Whether this position can send emails to group |
| control | `BOOLEAN` | Whether this position has admin control over group (e.g. adding/removing positions) |
| receive | `BOOLEAN` | Whether this position receives emails sent to this group |

### position_holders

| Column | Type | Comments |
|--------|------|----------|
| hold_id | `INT` | PK |
| pos_id | `INT` | Position being held |
| user_id | `INT` | Member holding position |
| start_date | `DATE` | Inclusive. Optional; if `NULL`, position has been held since beginning of time. |
| end_date | `DATE` | Inclusive. Optional; if `NULL`, position will be held until end of time. We set this to yesterday's date to terminate this position hold so that we keep the history of position holders. |
| subscribed | `BOOLEAN` | Whether user receives newsgroup emails to this position (`receive` must also be `TRUE` for the position). Used so individual users can unsubscribe. |

### position_relations

This table allows certain positions to grant other positions. This is not recursive; for example, if position `A` gives position `B` and position `B` gives position `C`, position `A` does *not* give position `C`.

We debated whether to support this for the new Donut, since it adds a bit of complexity, but ultimately decided that it was necessary to cleanly represent certain relationships. Currently, it is used to grant campuswide positions the ability to send from and control the `ug-*` groups:
```
MariaDB [donut]> SELECT groups1.group_name group_from, positions1.pos_name pos_from, groups2.group_name group_to, positions2.pos_name pos_to FROM groups groups1 JOIN positions positions1 ON groups1.group_id = positions1.group_id JOIN position_relations ON positions1.pos_id = pos_id_from JOIN positions positions2 ON pos_id_to = positions2.pos_id JOIN groups groups2 ON positions2.group_id = groups2.group_id WHERE groups2.group_name NOT LIKE 'ug-%';
+----------------------------------------+----------------------------+----------+--------+
| group_from                             | pos_from                   | group_to | pos_to |
+----------------------------------------+----------------------------+----------+--------+
| ASCIT                                  | Treasurer                  | ug       | Admin  |
| ASCIT                                  | VP of Academic Affairs     | ug       | Admin  |
| ASCIT                                  | VP of Non-Academic Affairs | ug       | Admin  |
| ASCIT                                  | Director of Operations     | ug       | Admin  |
| Interhouse Committee (IHC)             | Chair                      | ug       | Admin  |
| The Tech                               | Editor                     | ug       | Admin  |
| ASCIT                                  | President                  | ug       | Admin  |
| Devteam                                | Member                     | ug       | Admin  |
| Academics and Research Committee (ARC) | Secretary                  | ug       | Admin  |
| Board of Control (BoC)                 | Chair                      | ug       | Admin  |
| Board of Control (BoC)                 | Secretary                  | ug       | Admin  |
| Conduct Review Committee (CRC)         | Co-Chair                   | ug       | Admin  |
| ASCIT                                  | Secretary                  | ug       | Admin  |
| Big T                                  | Editor-in-Chief            | ug       | Admin  |
| Big T                                  | Business Manager           | ug       | Admin  |
| Interhouse Committee (IHC)             | Secretary                  | ug       | Admin  |
| ASCIT                                  | Social Director            | ug       | Admin  |
| Academics and Research Committee (ARC) | Chair                      | ug       | Admin  |
| Review Committee                       | Chair                      | ug       | Admin  |
| Review Committee                       | Secretary                  | ug       | Admin  |
| Conduct Review Committee (CRC)         | Chair                      | ug       | Admin  |
+----------------------------------------+----------------------------+----------+--------+
```

| Column | Type | Comments |
|--------|------|----------|
| pos_id_from | `INT` | The initial position |
| pos_id_to | `INT` | The position being granted |

### permissions

| Column | Type | Comments |
|--------|------|----------|
| permission_id | `INT` | PK. These values are referred to in code by permissions enums, so new permissions needed to be added to both the table and the code. |
| permission_type | `VARCHAR(255)` | What kind of permission is being granted on this `resource_name`, e.g. `'View'` or `'Edit'. |
| resource_name | `VARCHAR(255)` | Area where permission applies (usually one of the Donut modules in the code). Optional. |
| description | `VARCHAR(255)` | Description of what the permission provides. Optional. |

### position_permissions

| Column | Type | Comments |
|--------|------|----------|
| pos_id | `INT` | Position being granted a permission |
| permission_id | `INT` | Permission being granted |

### house_groups (view)

Filters groups that represent houses

### house_positions (view)

Filters positions that represent full or social memberships in house groups

### current_direct_position_holders (view)

Filters position holders (not including "indirect positions" given by position relations) that are currently active

### current_position_holders (view)

All currently active position holds (both direct and indirect positions). Queries about held positions should generally use this view rather than `position_holders` or `current_direct_position_holders`.