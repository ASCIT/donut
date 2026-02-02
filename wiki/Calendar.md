This is only loosely based off of the legacy system. 

If something fails -- it's possible that Google changed their API's. 

### Functionality

* Add events
* Update events
* Delete events
* Add a calendar as a read-only or editable calendar to your email (based on one's permissions)
* Search for an event based on the description or name. 

### DB

#### calendar_logs
|Column|Type|Comments|
|------|----|--------|
|log_id|`INT`||
|user_id|`INT`|Who did what action|
|calendar_id|`VARCHAR(25)`|Unique id for a calendar from google cal API|
|calendar_gmail|`VARCHAR(50)`|Unique gmail from google cal API|
|user_gmail|`VARCHAR(50)`|Who is shared this|
|acl_id|`VARCHAR(50)`|The control rule id from google cal API|
|request_time|`DATETIME`||
|request_permission|`CHAR(6)`|writer or reader|

#### 
|Column|Type|Comments|
|------|----|--------|
|event_id |`INT`| |
|user_id|`INT`| Who created this -- may be empty if people makes changes through their own google calendar|
|calendar_tag |`VARCHAR(25)`|e.g: `Avery`, `Dabney`|
| google_event_id |`VARCHAR(80)`|Unique id from google calendar API|
| summary |`TEXT `|Event Name|
| description |`TEXT `||
| location |`TEXT `||
| begin_time |`DATETIME`||
| end_time |`DATETIME `||


### Linked with Google calendars

In general, the use of donut calendars has been pretty minimal. Due to the popularity of google calendar, it was decided that there would be full google calendar integration. 

Tags do not exist in google calendars. Instead, there are just separate calendars. There are currently 12 calendars -- add more will require generating a new calendar using google calendar's api, and hardcoding them in the backend. 

Because donut would be requesting large amounts of data from 12 separate calendars, and because this is a very expensive (time-wise) process, donut also has a local version of all the events that are also in the google calendars account. Whenever the calendar page is accessed, donut directly get information from donut's DB. Users can also manually request a sync from google calendars to our db. The issue here is that google calendar throttles us if we have too many requests at the same time, and there's some type of exponential backoff :')

The calendars in caltech.donut.devteam@gmail.com are owned by a project in the google cloud account for the Gmail. The password is on the Asana.

