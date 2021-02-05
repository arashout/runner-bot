sync:
	echo "Move files"
	scp -i ~/.ssh/fitpets.pem .envrc run.sh ${SERVER_ADDRESS}:/home/ubuntu/runner-bot

	echo "Stopping runner-bot"
	ssh -i ~/.ssh/fitpets.pem ${SERVER_ADDRESS} 'sudo supervisorctl stop runner-bot'

	echo "Pulling any new changes"
	git pull origin main

	echo "Starting runner-bot"
	ssh -i ~/.ssh/fitpets.pem ${SERVER_ADDRESS} 'sudo supervisorctl start runner-bot'

stop:
	echo "Stopping runner-bot"
	ssh -i ~/.ssh/fitpets.pem ${SERVER_ADDRESS} 'sudo supervisorctl stop runner-bot'

start:
	echo "Starting runner-bot"
	ssh -i ~/.ssh/fitpets.pem ${SERVER_ADDRESS} 'sudo supervisorctl start runner-bot'

install-python:
	sudo apt install python3-pip -y

	echo "Installing poetry"
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
