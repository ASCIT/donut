PasswordChangedEmail = \
"""Hi {0},\n
Your password has been successfully changed. If you did not request a password
change, please let us know immediately at devteam@donut.caltech.edu.\n
Thanks!
Donut Devteam
"""

ResetPasswordEmail = \
"""Hi {0},\n
We have received a request to reset this account's password. If you didn't
request this change, let us know immediately at devteam@donut.caltech.edu. Otherwise, 
you can use this link to change your password:
{1}
Your link will expire in {2}.\n
Thanks!
Donut Devteam
"""

ResetPasswordSuccessfulEmail = \
"""Hi {0},\n
Your password has been successfully reset. If you did not request a password
reset, please let us know immediately at devteam@donut.caltech.edu.\n
Thanks!
Donut Devteam
"""

AddedToWebsiteEmail = \
"""Hi {0},\n
You have been added to the Donut website. In order to access private
areas of our site, please complete registration by creating an account here:
{1}
If you have any questions or concerns, please find us or email us at devteam@donut.caltech.edu.\n
Thanks!
Donut Devteam
"""

CreateAccountRequestEmail = \
"""Hi {0},\n
To create an account on the Donut website, please use this link:
{1}
If you did not initiate this request, please let us know immediately at devteam@donut.caltech.edu.\n
Thanks!
Donut Devteam
"""

CreateAccountSuccessfulEmail = \
"""Hi {0},\n
Your Donut account with the username "{1}" has been created. If this
was not you, please let us know immediately.\n
Thanks!
Donut Devteam
"""

MembersAddedEmail = \
"""The following members have been added to the Donut website:
{0}
and the following members were skipped (they were already in the database):
{1}
You should run the email update script to add the new members.
Thanks!
Donut Devteam
"""

ErrorCaughtEmail = \
"""An exception was caught by the website. This is probably a result of a bad
server configuration or bugs in the code, so you should look into this. This
was the exception:
{0}
"""
