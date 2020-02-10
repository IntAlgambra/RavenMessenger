# Raven Messenger

## Table of Contents

- [About](#about)
- [Installing](#installing)
- [Usage](#usage)

## About <a name = "about"></a>

Raven Messenger is an instant messaging app written in Python as programming practice. Raven messenger's features:

1. Written in Python, fully open-source

2. Doesn't have GUI - everything works in command line tui

3. Uses RSA encryption to ensure privacy

4. Doesn't save message history anywhere

5. Easy to deploy on server to have your own private messenger

ATTENTION! Raven Messenger was written to practice python programming, so it's full of bugs and was not properly tested (but I hope I'll fix it in the future). 

## Installing <a name = "installing"></a>

Clone project and cd into project directory

```
git clone https://github.com/IntAlgambra/Raven.git
cd Raven
```

create virtual enviroment (use python 3.7 or 3.8)

```
virtualenv venv
#on linux:
source venv/bin/activate
#on Windows:
venv\Scripts\activate
```
install all required libraries:

```
#on linux:
pip install -r requirements-l.txt
#on windows:
pip install -r requirements-w.txt
```

## Usage <a name = "usage"></a>

### Usage of server

To start server run in terminal.

```
python server.py start-server -p [server port] -h [server ip]
```

To add new client to server database

```
python server.py add-account -l [login] -p [temporary password]
```

### Usage of client

before launching a client open client_backend.py and change HOST variable to your server ip adress.

To launch a client run:

```
python client_tui.py
```
