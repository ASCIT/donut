# donut [![Build Status](https://github.com/ASCIT/donut/workflows/Python%20CI/badge.svg?branch=master)](https://github.com/ASCIT/donut/actions)
The repository for Donut. Written using Python/Flask and powered by MariaDB.

# Setting up your environment
- You must be on Caltech wifi or use a VPN (http://imss.sites.caltech.edu/services/wired-wireless-remote-access/Virtual-Private-Network-VPN)
- Gain SSH access to the server:

   AWS Domain:

   1. https://help.github.com/articles/generating-an-ssh-key/

   2. Email the public key to the Directly Responsible Individual for the Getting Started section of the Site rewrite project.

   3. The .ssh config file lets you configure a ssh connection so you don't have to
   Example `~/.ssh/config` on your personal machine:
      ```
      Host donut-dqu
          HostName donut.caltech.edu
          User dqu
          LocalForward 9000 127.0.0.1:50XX
              (Where 50XX is a unique port number on the server we should each use)
      ```
   4. Now to SSH into the server, we can type from terminal `ssh donut-dqu`

- Clone the repository:
```
git clone https://github.com/ASCIT/donut.git ~/donut
```
- Set up your virtualenv and install requirements in that virtualenv
```
make fresh-install
```
This (see `Makefile`)
1. Creates a virtualenv in `~/virtualenvs/donut-py3`
2. Installs the requirements given  in `requirements.txt` into the virtualenv.
3. Adds a line to your `~/.profile` to automatically activate the virtualenv when you login.

   To deactivate the virtualenv (which you shouldn't need to do), simply type `deactivate`


- You will also need a separate config file that we will give you in order to access the database.

# Testing
## Linting
- `make lint`

## Unit Testing
- `make test`

## Test Site
The easiest way to set up a test site is to use SSH port forwarding, so that requests to your local computer are forwarded to the development server. For example:
```
ssh -L 9000:localhost:5000 <host>
```
This will forward your local port 9000 so that visiting [localhost:9000](http://localhost:9000) on your local computer is equivalent to visiting [localhost:5000](http://localhost:5000) on the remote server. Flask's debugging environment defaults to port 5000, but you can change that in your `config.py` file (multiple people cannot simultaneously bind to the same port through SSH port forwarding).

To start the test site:
```
python run_server.py -e dev -p 50XX
```
You can visit the test site by going to [localhost:9000](http://localhost:9000) (or whichever port you decided to forward) in your local browser.

# Development Workflow
1. Create a new branch
2. Create a PR
3. After your PR approved and merged with `master`, you must refresh the server to update the site. After sshing, run 
```
cd /home/ascit/donut
sudo git pull
sudo apachectl restart
```
