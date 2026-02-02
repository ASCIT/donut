The new Donut Marketplace will function much like the current one, but it will be written in Python and Flask (and probably a little bit of JavaScript).

## Functionality

 * Searching by categories and specific queries
 * A nice interface to display the current available items, pictures, etc.
 * Ability to add items to sell, edit their details, add pictures or comments, etc.
     * Also to delete items, if they're bought or the seller decides not to sell the thing after all

## Would be nice to have

 * Chat-like thing between buyer and seller that can also easily take down the item when the buyer buys it
 * Integration with online payment APIs to smooth the process of buying an item
 * Possibly adding the option to put items up for bidding on, instead of just buying directly
 * Results or autocomplete options being displayed as the user types into the search box

## SQL tables (shamelessly copied from the current marketplace.sql)
### marketplace_items
|Key|Type|Comments|
|---|----|--------|
|item_id | int | Unique item ID (also a PRIMARY KEY)|
|cat_id | int | Unique category ID (also a FOREIGN KEY to marketplace_categories)|
|user_id | int | Which user? (FK to members)|
|item_title | string | Title of item|
|item_details | string | Details of item|
|item_condition | string | Condition of item, from Poor to New (or can be blank)|
|item_price | numeric(6, 2) | Price of item, in dollars and cents, max 999999.99|
|item_timestamp | int | Time posted; UNIX timestamp|
|item_active | boolean | Whether or not the item is active|
|textbook_id | int | If it's a textbook, which one? (FK to marketplace_textbooks)|
|textbook_edition | string | Which edition?|
|textbook_isbn | string | Depends on version and so is not stored in the textbook table|

Additional rows, if we decide to implement bidding:

|Key|Type|Comments|
|---|----|--------|
|item_bidding | boolean | Whether or not the item is up for bidding|
|time_left | int | How much longer before the bidding ends|
|bid_amount | int | The current winning bid amount (and final, if the bidding's over)|
|bid_winner | int | The user id of the winning bidder (FK to members)|


### marketplace_textbooks
|Key|Type|Comments|
|---|----|--------|
|textbook_id | int | Which textbook? (PK)|
|textbook_title | string | Name of the textbook|
|textbook_author | string | Author or authors|

### marketplace_categories
|Key|Type|Comments|
|---|----|--------|
|cat_id | int | Which category? (PK)|
|cat_title | string | Name of the category|
|cat_active | bool | Whether or not the category is currently active|
|cat_order | int | Where does it go in the order of categories?|

### marketplace_images
|Key|Type|Comments|
|---|----|--------|
|img_id | int | Which image belonging to the item is it? (PK)|
|item_id | int | To which item do the images belong? (FK to marketplace_items)|
|img_link | string | URL of the image, probably on imgur unless we change our hosting too|