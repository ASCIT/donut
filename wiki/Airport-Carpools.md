## Functionality
- Previously during breaks an email with a link to a google spreadsheet would get circulated for people to put their flight times to coordinate ride shares to the airport
- This page embeds the google sheet on Donut
- To embed a google sheet: 
1. File → Publish to the Web → Embed (ignore this link!)
2. File → Share → Copy link
3. Paste link in Donut
- ASCIT members can access settings to update the link or toggle visibility

# SQL tables

In `flights.sql`:

## `flights`
| Column | Type | Comments |
| ------ | ---- | -------- |
|`link` | `TEXT` | link to google spreadsheet |
|`visible` | `BOOLEAN` | whether the sheet is visible |
There's no PK since there is max 1 row in the table