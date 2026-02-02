## Functionality
- Send email to groups like ug-2021, ASCIT, etc.
- Checks `positions` table to see if user has position with `send, control, receive` permissions
- column `subscribed` in `position_holders` controls whether the user is subscribed to emails to the group
- Users can post as any position with `send` permission
- members of group can view previous messages sent
- TinyMCE account: caltech.donut.devteam@gmail.com

## SQL
In `donut.sql`
### `newsgroup_posts`
| Column | Type | Comments |
| ------ | ---- | -------- |
|`newsgroup_post_id`| `INT` | PK |
|`group_id` | `INT` | References `groups.group_id` |
|`subject` | `TEXT` | email subject |
|`message` | `TEXT` | email message |
|`post_as` | `VARCHAR(32)`| email from:  \<group name\> \<position name\> (\<user's full name\>) |
|`user_id` | `INT` | References `members.user_id`|
|`time_sent`| `TIMESTAMP` | |
 