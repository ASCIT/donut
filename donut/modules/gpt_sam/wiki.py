"""
Donut Wiki Knowledge Base for GPT-SAM
Provides searchable documentation for developers and administrators.
"""

WIKI_PAGES = {
    "groups-and-positions": {
        "title": "Groups and Positions",
        "summary": "How groups, positions, and position holders work in Donut. Covers database schema, permissions, and relationships.",
        "tags": ["groups", "positions", "permissions", "database", "schema", "position_holders", "position_relations"],
        "content": """
# Groups and Positions

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
| control | `BOOLEAN` | Whether this position has admin control over group |
| receive | `BOOLEAN` | Whether this position receives emails sent to this group |

### position_holders
| Column | Type | Comments |
|--------|------|----------|
| hold_id | `INT` | PK |
| pos_id | `INT` | Position being held |
| user_id | `INT` | Member holding position |
| start_date | `DATE` | Inclusive. Optional; if NULL, position has been held since beginning of time. |
| end_date | `DATE` | Inclusive. Optional; if NULL, position will be held until end of time. |
| subscribed | `BOOLEAN` | Whether user receives newsgroup emails to this position |

### position_relations
This table allows certain positions to grant other positions. This is not recursive.
| Column | Type | Comments |
|--------|------|----------|
| pos_id_from | `INT` | The initial position |
| pos_id_to | `INT` | The position being granted |

### position_permissions
| Column | Type | Comments |
|--------|------|----------|
| pos_id | `INT` | Position being granted a permission |
| permission_id | `INT` | Permission being granted |
"""
    },

    "newsgroups": {
        "title": "Newsgroups (Mailing Lists)",
        "summary": "How to send emails to groups. Covers send/receive/control permissions and the newsgroup_posts table.",
        "tags": ["newsgroups", "email", "mailing", "send", "receive", "TinyMCE"],
        "content": """
# Newsgroups

## Functionality
- Send email to groups like ug-2021, ASCIT, etc.
- Checks `positions` table to see if user has position with `send, control, receive` permissions
- Column `subscribed` in `position_holders` controls whether the user is subscribed to emails to the group
- Users can post as any position with `send` permission
- Members of group can view previous messages sent
- TinyMCE account: caltech.donut.devteam@gmail.com

## SQL
In `donut.sql`:

### newsgroup_posts
| Column | Type | Comments |
| ------ | ---- | -------- |
|`newsgroup_post_id`| `INT` | PK |
|`group_id` | `INT` | References `groups.group_id` |
|`subject` | `TEXT` | email subject |
|`message` | `TEXT` | email message |
|`post_as` | `VARCHAR(32)`| email from: <group name> <position name> (<user's full name>) |
|`user_id` | `INT` | References `members.user_id`|
|`time_sent`| `TIMESTAMP` | |
"""
    },

    "permissions": {
        "title": "Permissions System",
        "summary": "How permissions work in Donut. Adding permissions, checking permissions in code, and the permissions enum.",
        "tags": ["permissions", "auth", "check_permission", "get_permissions", "enum"],
        "content": """
# Permissions

## How do permissions work?
Each permission is assigned an id and that id is associated with a position. Everyone who either:
(a) holds one of the positions linked to the permission id,
(b) holds a position linked (via `position_relations`) to a position associated with this permission, or
(c) holds the admin permission
is defined to hold the permission.

## How do I add a permission?
Permissions are added by inserting them into the database. First, create a row in `permissions`. This will assign a permission_id to the permission, and should store the type of permission, resource name, and a short description. Then assign the permission to positions by adding rows to the `position_permissions` table.

## How should I refer to permissions in my code?
To avoid littering code with 'magic numbers', use Enums to give names to permission id's. There is one global enum -- `donut.default_permissions.Permissions` for site-wide permissions. For module-specific permissions, create a permissions enum in your module.

## How should I check if the user has a permission?
```python
from donut.auth_utils import check_permission, get_permissions

# Check single permission
check_permission(username, permission_id)  # Returns True or False

# Get all permissions
get_permissions(username)  # Returns list of permission_ids
```

Note: If `default_permissions.ADMIN` (permission_id 1) is in the list, the user has all permissions. `check_permission` always returns True for site admins.

## permissions table
| Column | Type | Comments |
|--------|------|----------|
| permission_id | `INT` | PK |
| permission_type | `VARCHAR(255)` | e.g. 'View' or 'Edit' |
| resource_name | `VARCHAR(255)` | Area where permission applies |
| description | `VARCHAR(255)` | Description of the permission |
"""
    },

    "directory-search": {
        "title": "Directory Search",
        "summary": "The member directory search functionality. Covers the members table schema and search features.",
        "tags": ["directory", "search", "members", "users", "profile"],
        "content": """
# Directory Search

## Functionality
- Search by various query terms (name, email, house, graduation year, etc.)
- Support for preferred name, custom gender, and profile picture
- Click on username to see own directory page
- Scripts for exporting/importing legacy data

## SQL tables

### members
| Column | Type | Comments |
|--------|------|----------|
| user_id | `INT` | PK |
| uid | `CHAR(7)` | e.g. `1418702`, unique |
| last_name | `VARCHAR(255)` | |
| first_name | `VARCHAR(255)` | |
| preferred_name | `VARCHAR(255)` | Optional |
| middle_name | `VARCHAR(255)` | Optional |
| email | `VARCHAR(255)` | e.g. `csander@caltech.edu` |
| phone | `VARCHAR(64)` | Optional |
| gender | `TINYINT` | Overridden by gender_custom |
| gender_custom | `VARCHAR(32)` | Optional |
| birthday | `DATE` | Optional |
| entry_year | `YEAR(4)` | Optional |
| graduation_year | `YEAR(4)` | Optional |
| msc | `SMALLINT` | Optional |
| building_id | `INT` | References buildings.building_id |
| room | `VARCHAR(5)` | e.g. `200A` |
| address | `VARCHAR(255)` | Home address |
| city | `VARCHAR(64)` | Hometown |
| state | `VARCHAR(64)` | |
| zip | `VARCHAR(9)` | |
| country | `VARCHAR(64)` | |

### users
| Column | Type | Comments |
|--------|------|----------|
| user_id | `INT` | PK, references members.user_id |
| username | `VARCHAR(32)` | Unique |
"""
    },

    "database": {
        "title": "Database",
        "summary": "Database setup, users, and schema design principles. MariaDB/MySQL commands and best practices.",
        "tags": ["database", "mysql", "mariadb", "sql", "schema"],
        "content": """
# Database

## Using the Database
The database has three users with three levels of power: `ascit`, `devel`, and `root`.
There are three databases: `donut`, `donut_dev`, and `donut_test`.
- `donut` is the live database
- `donut_dev` is for development
- `donut_test` is for testing

### Command Line
```bash
mysql -u <user> -p <database>  # Login (-p prompts for password)
show databases;                 # List databases
use donut_dev;                  # Select database
show tables;                    # List tables
mysql -u <user> -p <database> < file.sql  # Run SQL script
```

## Schema Design Principles
- Design around `NATURAL JOIN`s - use same column names for same values across tables
- Avoid multiple tables with redundant info in 1-1 relationships
- Use `INT` ID columns for faster comparisons
- Be cautious with `NULL`able columns - there should be a clear reason
- Use MySQL `VIEW`s to encapsulate common queries (e.g. `current_position_holders`)
"""
    },

    "course-scheduler": {
        "title": "Course Scheduler and Planner",
        "summary": "The course scheduling and planning tools. Database schema for courses, sections, and user selections.",
        "tags": ["courses", "scheduler", "planner", "registrar", "sections"],
        "content": """
# Course Scheduler and Planner

## Purpose
The course scheduler is used to select courses for a term, showing time slots and conflicts.
The course planner is used to plan courses over multiple years and terms.
Both tools save automatically when logged in.

## SQL tables

### courses
| Column | Type | Comments |
|--------|------|----------|
| course_id | `INT` | PK |
| year | `YEAR` | e.g. 2020 |
| term | `TINYINT` | FA: 1, WI: 2, SP: 3 |
| department | `VARCHAR(30)` | e.g. `CS/IDS` |
| course_number | `VARCHAR(10)` | e.g. `150a` |
| name | `VARCHAR(150)` | |
| units_lecture | `FLOAT` | |
| units_lab | `FLOAT` | |
| units_homework | `FLOAT` | |
| units | `FLOAT` | Auto-computed total |

### sections
| Column | Type | Comments |
|--------|------|----------|
| course_id | `INT` | References courses |
| section_number | `TINYINT` | |
| instructor_id | `INT` | References instructors |
| grades_type_id | `INT` | |
| times | `VARCHAR(100)` | e.g. `MWF 13:00 - 13:55` |
| locations | `VARCHAR(100)` | |

### scheduler_sections (user selections)
| Column | Type | Comments |
|--------|------|----------|
| user_id | `INT` | |
| course_id | `INT` | |
| section_number | `TINYINT` | |
"""
    },

    "feedback": {
        "title": "Feedback System",
        "summary": "Anonymous feedback for BoD, ARC, and Devteam. Complaint tracking and email notifications.",
        "tags": ["feedback", "complaints", "bod", "arc", "anonymous"],
        "content": """
# Feedback

## Functionality
- Post feedback for BoD, ARC, Donut Devteam
- Must be logged in or on Caltech VPN to post
- Sends email notifications when complaints are posted or updated
- Resolved complaints are hidden in summary view

## Permissions
- `SUMMARY`: view summary page and all complaints
- `TOGGLE_RESOLVED`: mark complaints resolved/unresolved
- `ADD_REMOVE_EMAIL`: manage subscribed emails
- `VIEW_EMAILS`: view list of subscribed emails

## SQL Tables

### complaint_info
| Column | Type | Comments |
|--------|------|----------|
| complaint_id | `INT` | PK |
| subject | `VARCHAR(50)` | |
| resolved | `BOOLEAN` | |
| uuid | `BINARY(16)` | UK |
| org | `INT` | 1: BoD, 2: ARC, 3: devteam |
| ombuds | `BOOLEAN` | For ARC - whether poster asked ombuds |

### complaint_messages
| Column | Type | Comments |
|--------|------|----------|
| complaint_id | `INT` | FK |
| time | `TIMESTAMP` | |
| message | `TEXT` | |
| poster | `VARCHAR(50)` | Optional name |
| message_id | `INT` | PK |
"""
    },

    "server-management": {
        "title": "Managing the Production Server",
        "summary": "Server administration: Apache, logs, database backups, HTTPS, and deployment.",
        "tags": ["server", "apache", "deployment", "logs", "backup", "https", "production"],
        "content": """
# Managing the Production Server

## Where is the production code?
`/home/ascit/donut` - cloned from the repository.
Secret config files needed:
- `donut/config.py`: environment configuration, database logins
- `calendar.json`: Google Calendar API authorization

## Apache
Production uses Apache and mod_wsgi for Flask.
- Apache config: `/etc/apache2/sites-available/000-default.conf`
- mod_wsgi config: `/home/ascit/donut/donut.wsgi`
- Reload: `sudo service apache2 restart`

## Logs
- Flask/Apache logs: `/var/log/apache2/access.log`
- Error logs: `/var/log/apache2/error.log`

## Database
Production database is `donut`. See `donut/config.py` for credentials.

## virtualenv
Production virtualenv: `/home/ascit/virtualenvs/donut-py3`
Update packages:
```bash
. /home/ascit/virtualenvs/donut-py3/bin/activate
make update-packages
```

## HTTPS (Let's Encrypt)
Certificates in `/etc/letsencrypt`
Auto-renewal via cron: `sudo certbot renew --post-hook 'service apache2 restart'`

## Backups
```bash
# Create backup
sudo mysqldump -u root --password=ROOT_PASSWORD donut --single-transaction --add-drop-table --result-file=donut_backup.sql

# Restore backup
(echo "SET FOREIGN_KEY_CHECKS = 0;"; cat donut_backup.sql; echo "SET FOREIGN_KEY_CHECKS = 1;") | mysql -u root --password=ROOT_PASSWORD donut
```
"""
    },

    "aws-server": {
        "title": "AWS Server",
        "summary": "Amazon AWS EC2 instance setup and configuration for Donut.",
        "tags": ["aws", "ec2", "amazon", "server", "hosting"],
        "content": """
# AWS Server

The Amazon AWS EC2 instance is used for the site. Account: donutascit@gmail.com
Go to AWS console and reboot EC2 instance if Donut is down.

## Notable config settings
- Region: US West (Oregon) - recommended by IMSS
- SSH access only from Caltech (use VPN with "3: Tunnel All" from outside)
- Static IP configured
- Domain: ec2-35-162-204-135.us-west-2.compute.amazonaws.com

## Routine Tasks
- Obtain donut email and AWS credentials from previous Devteam lead
- Transfer 2-Factor Auth to new lead on Donut Email
- Update credit card on AWS (ASCIT reimburses charges)
"""
    },

    "onboarding": {
        "title": "Onboarding",
        "summary": "New Devteam member onboarding: accounts, privileges, and getting started.",
        "tags": ["onboarding", "new member", "setup", "accounts"],
        "content": """
# Onboarding

**Donut** refers to the production site. **Bagel** refers to projects within Donut.

Stack: Python/Flask and MariaDB (requires Python, SQL, HTML, CSS, JS knowledge)

## General Onboarding
1. Add new member to Github ASCIT organization and relevant teams
2. Add new member to Asana ASCIT organization (optional)

## New Accounts and Privileges
Create account on server:
```bash
sudo adduser rengrenghello
sudo usermod -a -G devteam rengrenghello
sudo usermod -a -G sudo rengrenghello
```

Login: `ssh username@donut.caltech.edu`
Change password: `passwd`
Add to Devteam group on donut.caltech.edu/campus_positions
Set up dev environment: https://github.com/ASCIT/donut#setting-up-your-environment
"""
    },

    "testing": {
        "title": "Testing",
        "summary": "Testing with pytest, fixtures, and Travis CI integration.",
        "tags": ["testing", "pytest", "travis", "ci", "fixtures"],
        "content": """
# Testing

We use pytest as our test framework.
`make test` searches for `test_*.py` files and runs `test_*` functions.

## Fixtures
The client fixture sets up Flask's application context and database.
Wraps each test in a transaction that rolls back after completion.

```python
from donut.testing.fixtures import client

def test_my_function(client):
    # Your test code here
    pass
```

## Database
The client fixture uses the test database. Changes to test database should be in separate PRs.

## Travis CI
Travis runs builds based on `.travis.yml` for each commit:
- Installs requirements
- Sets up database
- Runs linter
- Runs tests

Don't forget to run `make lint` before pushing!
Travis site: https://travis-ci.org/ASCIT/donut
"""
    },

    "email-setup": {
        "title": "Email Setup",
        "summary": "Incoming and outgoing email configuration with Postfix.",
        "tags": ["email", "postfix", "smtp", "aliases"],
        "content": """
# Email Setup

## Incoming
We don't receive many incoming emails. devteam@donut.caltech.edu forwards to current members.
To update aliases:
```bash
sudo vim /etc/aliases  # Change emails next to "devteam"
sudo newaliases        # Update aliases index
```

## Outgoing
Postfix server handles sending emails. Uses Python `smtplib` library.
Note: Doesn't implement modern SMTP auth/encryption. Emails may be flagged as spam by Gmail.
IMSS has special rules to avoid quarantine for emails to all undergrads.
"""
    },

    "rest-api": {
        "title": "REST API",
        "summary": "Available REST API endpoints for groups, members, and organizations.",
        "tags": ["api", "rest", "json", "endpoints"],
        "content": """
# REST API

| URL Extension | Description |
|---------------|-------------|
| /1/groups | JSON list of groups |
| /1/members | JSON of all registered members |
| /1/members/<user_id> | JSON for specific member |
| /1/organizations | JSON of all organizations |
| /1/organizations/<org_id> | JSON for specific organization |

## Examples
```
GET /1/members/
[{"first_name": "Rahul", "last_name": "Bachal", "user_id": 1, ...}, ...]

GET /1/members/1/
{"first_name": "Rahul", "last_name": "Bachal", "user_id": 1, ...}
```
"""
    },

    "import-data": {
        "title": "Import Data",
        "summary": "Scripts for importing student data and course lists from the Registrar.",
        "tags": ["import", "registrar", "students", "courses", "scripts"],
        "content": """
# Import Data

## Student data from the Registrar
Ask Registrar (Debi Tuttle) for undergrad student TSV export.
```bash
# Import to dev
donut/modules/directory_search/utils/import_registrar.py ascit_200911.txt

# Import to prod (after verification)
donut/modules/directory_search/utils/import_registrar.py ascit_200911.txt -e prod
```

## Update ug-* groups
After importing students:
```bash
donut/modules/directory_search/utils/update_ug_groups.py
donut/modules/directory_search/utils/update_ug_groups.py -e prod
```

## Course list
Registrar exports course schedule each term as TSV.
```bash
# Import courses (FA = fall, 2020 = year)
donut/modules/courses/utils/import_registrar.py donut_courses_FA2020-21_200911.txt 2020 FA

# Import to prod
donut/modules/courses/utils/import_registrar.py donut_courses_FA2020-21_200911.txt 2020 FA -e prod
```

WARNING: Missing courses will be dropped from students' schedules/planners!
"""
    },

    "making-pages": {
        "title": "Making a Simple Page",
        "summary": "How to create HTML pages in Donut using Jinja2 templates and CSS classes.",
        "tags": ["html", "templates", "jinja", "css", "frontend"],
        "content": """
# Making a Simple Page

## Basic Template
```html
{% extends "layout.html" %}

{% block page %}
    <div class="container theme-showcase" role="main">
        <div class="jumbotron">
            <!-- Your content here -->
        </div>
    </div>
{% endblock %}
```

IMPORTANT: Always wrap content in container and jumbotron divs for mobile support!

## Two-Column Layout
```html
<div class="medium-text">
    <div class="half-float-left">
        <p>Left column content</p>
    </div>
    <div class="half-float-right">
        <img src="image.jpg"/>
    </div>
</div>
```

## CSS Classes
- Text sizes: `.large-text`, `.medium-text`, `.small-text`
- Positioning: `.pos-center`, `.pos-left`, `.pos-right`
- Columns: `.half-float-left/right`, `.triple-split-left/center/right`
- Color theme: Orange (#FFA500), hover: #CD6600
"""
    },

    "css-style": {
        "title": "CSS Style Guide",
        "summary": "Donut CSS conventions: colors, buttons, containers, fonts, and mobile support.",
        "tags": ["css", "style", "design", "frontend", "mobile"],
        "content": """
# CSS Style Guide

## Color Theme
- Primary orange: `#FFA500`
- Hover orange: `#CD6600`
- Navbar background: `#222`
- Navbar border: `#080808`
- Text: `#333`
- Background/light text: `#FFF`

## Buttons
Add `.btn` class for theme-compliant buttons with opacity transition.

## Containers
Always wrap main content in jumbotron:
```html
<div class="container theme-showcase" role="main">
    <div class="jumbotron">...</div>
</div>
```

## Fonts
Primary: Google Open Sans (300, 400, 600 weights)
Title font: Custom donutfont.ttf

## Mobile
CSS is designed to be responsive. Float classes stack vertically on mobile portrait orientation.
"""
    },

    "masquerading": {
        "title": "Masquerading",
        "summary": "How devteam members can login as another user for testing.",
        "tags": ["masquerade", "testing", "login", "debug"],
        "content": """
# Masquerading

Allows devteam members to login as another user for testing.

## Instructions
To masquerade as another user:
1. Find their username in the directory
2. Login as `<your_username>:<their_username>` with YOUR password

Example: To test as user "jchen", login as "myusername:jchen" with your own password.
"""
    }
}


def get_wiki_summaries():
    """Return a list of all wiki page summaries for the system prompt."""
    summaries = []
    for page_id, page in WIKI_PAGES.items():
        summaries.append(f"- **{page['title']}** (`{page_id}`): {page['summary']}")
    return "\n".join(summaries)


def search_wiki(query):
    """
    Search wiki pages by query string.
    Returns matching pages with their full content.
    """
    query_lower = query.lower()
    results = []

    for page_id, page in WIKI_PAGES.items():
        score = 0

        # Check title
        if query_lower in page['title'].lower():
            score += 10

        # Check tags
        for tag in page['tags']:
            if query_lower in tag.lower():
                score += 5
            if tag.lower() in query_lower:
                score += 3

        # Check summary
        if query_lower in page['summary'].lower():
            score += 2

        # Check content
        if query_lower in page['content'].lower():
            score += 1

        if score > 0:
            results.append({
                'page_id': page_id,
                'title': page['title'],
                'summary': page['summary'],
                'content': page['content'],
                'score': score
            })

    # Sort by score descending
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:5]  # Return top 5 matches


def get_wiki_page(page_id):
    """Get a specific wiki page by its ID."""
    if page_id in WIKI_PAGES:
        page = WIKI_PAGES[page_id]
        return {
            'page_id': page_id,
            'title': page['title'],
            'summary': page['summary'],
            'content': page['content']
        }
    return None
