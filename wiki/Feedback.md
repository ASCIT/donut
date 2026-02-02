## Functionality
- Post feedback for BoD, ARC, Donut Devteam
- Must be logged in or on Caltech VPN to post
- Sends an email with link to the complaint when complaint is posted or an email is added
- Sends an update email to all subscribed emails when a message is added to a complaint
- Resolved complaints are hidden in summary view

## Permissions
- `SUMMARY`: can view summary page and all complaints 
- `TOGGLE_RESOLVED`: can edit whether the complaint was resolved
- `ADD_REMOVE_EMAIL` : can add/remove emails subscribed
- `VIEW_EMAILS` : can view list of subscribed emails 

## SQL Tables
In `feedback.sql`:
### `complaint_info`
|Column|Type|Comments|
|------|----|--------|
|`complaint_id` | `INT(11)`| PK |
|`subject` | `VARCHAR(50)`| |
|`resolved` | `BOOLEAN` | Whether the complaint was resolved |
|`uuid` | `BINARY(16)` | UK |
|`org` | `INT(11)` | 1: Bod, 2: ARC, 3: devteam|
|`ombuds` | `BOOLEAN` | For ARC complaints only - whether the poster has asked the ombuds person|

### `complaint_messages` : messages that have been added to a complaint
|Column|Type|Comments|
|------|----|--------|
|`complaint_id` | `INT(11)` | references `complaint_info.complaint_id` |
|`time` | `TIMESTAMP` | |
|`message` | `TEXT` | |
|`poster` | `VARCHAR(50)` | Name of the poster (optional) |
|`message_id` | `INT(11)` | PK |

### `complaint_emails` : emails that are subscribed to a complaint
|Column|Type|Comments|
|------|----|--------|
|`complaint_id` | `INT(11)` | references `complaint_info.complaint_id` |
|`email` | `VARCHAR(255)` | |
`(complaint_id, email)` is used as the primary key.

## Cascading Deletes
Deleting from `complaint_info` will delete the corresponding rows from `complaint_messages` and `complaint_emails`