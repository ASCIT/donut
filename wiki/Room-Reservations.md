Essentially a clone of the legacy service.
If you want to change the room list, you have to manually insert or delete in the `rooms` table.

## Functionality
- Can view a list of SAC rooms that can be reserved
- Can reserve a room between two times on a specific day with an optional reason
- Prevents users from making overlapping reservations
- Can view a list of your own reservations and delete them
- Can view all reservations between specified dates for specified rooms

## SQL tables
(In `rooms.sql`)
### rooms
|Column|Type|Comments|
|------|----|--------|
|room_id|`INT`|PK|
|location|`VARCHAR(50)`|e.g. `SAC 23`|
|title|`VARCHAR(50)`|e.g. `ASCIT Screening Room`|
|description|`VARCHAR(255)`|e.g. `A room for watching DVDs and videos`; some rooms don't have descriptions|

### room_reservations
|Column|Type|Comments|
|------|----|--------|
|reservation_id|`INT`|PK|
|room_id|`INT`|References `rooms.room_id`|
|user_id|`INT`|References `members.user_id`|
|reason|`TEXT`|Optional|
|start_time|`DATETIME`|
|end_time|`DATETIME`|Form requires `start_time` and `end_time` to be on the same day|