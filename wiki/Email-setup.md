# Incoming

For the most part, we don't receive incoming emails. We do have an alias configured for `devteam@donut.caltech.edu` that forwards emails to the current Devteam members. To update it, run the following commands:
```sh
sudo vim /etc/aliases # change the emails listed next to "devteam"
sudo newaliases # update the aliases index from /etc/aliases
```

Legacy Donut could receive emails and forward them to newsgroups, but the new Donut has a web interface to send these emails instead.

# Outgoing

There is a Postfix server running on the EC2 instance for both sending and receiving emails. We use the [`smtplib` Python library](https://docs.python.org/3/library/smtplib.html) to send emails from it.

We haven't really messed with the configuration, so it doesn't implement modern SMTP authentication and encryption protocols. It would be great to fix this. Currently, Donut emails are flagged as spam by some email providers (e.g. Gmail) and I think IMSS has special rules in place to avoid the mail quarantine catching Donut emails sent to all undergrads.