> "Donuts, what are they? What are donuts? Are they just a misinterpretation of a bagel? What are bagels? Why the hole? You see, someone must have put the hole there for a reason. Was it so they could make a kebab? So they could stick sticks through and make donut kebabs?" - Rahul Bachal

## "What is Donut?"

Some terminology, **Donut** refers to the production site and **Bagel** refers to projects within Donut.

**Donut Rewrite Site:** Our stack is Python/Flask and MariaDB. This means you need to know Python, SQL, HTML, CSS, and JS. These languages were chosen because they are universally taught (CS1, CS121) and won't be disappearing in the near future. Donut is hosted on an Amazon AWS instance. 

**Donut Legacy Site:** No longer active. Our stack was a PHP backend with a PostgreSQL database. A majority of scripting was in Perl, with a smaller amount in Python and bash.


## General Onboarding
 * Add new member to Github ASCIT organization and the relevant teams
 * Add new member to Asana ASCIT organization (optional)

## ~New Accounts and Privileges - Donut Legacy~

~Setup your account and dev environment for the legacy site by following the README on that repo: [New Accounts and Privileges - Donut Legacy](https://github.com/ASCIT/donut-legacy#new-accounts-and-privileges---donut-legacy)~

## New Accounts and Privileges - Donut Rewrite
 * Similar to the legacy site, create an account on the server, set a temporary password, add to usergroups (gives privileges). The following is with the fictitious new user `rengrenghello`.
    ```bash
    sudo adduser rengrenghello
    sudo usermod -a -G devteam rengrenghello
    sudo usermod -a -G sudo rengrenghello
    ```
 * Try logging in using the correct hostname with `ssh rengrenghello@donut.caltech.edu`.
 * Change your password with the `passwd` command.
 * Add the new member to the Devteam group [on Donut](https://donut.caltech.edu/campus_positions).
 * Set up your dev environment: https://github.com/ASCIT/donut#setting-up-your-environment
 