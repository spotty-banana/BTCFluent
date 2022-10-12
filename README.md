# BTCFluent

Really fluent BTC experience.

## Technologies

* Server OS: Linux (Ubuntu 20.04?)
* Backend (Python django)
* Web Server: (nginx / uwsgi) ?
* Database: MariaDB
* task processing: redis
* Frontend ?


## Wallet technologies

* BTC: Electrum

## Test Environment Setup

1. Clone the git repo

		git clone git@github.com:spotty-banana/BTCFluent.git
		cd BTCFluent

2. Setup Virtual environment and install required python packaged


		python3 -m venv venv # creates virtual environment in folder "venv"
		source venv/bin/activate
		pip install -r requirements.txt

3. By default sqlite is used, run the database migrations to get the initial schema

		python manage.py migrate

4. Setup local_settings.py to suit your local needs

		cp BTCFluent/local_settings.py.template BTCFluent/local_settings.py

5. Install redis

		apt install redis

6. Run the app

		python manage.py runserver_plus
