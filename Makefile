sync:
	echo "Move files"
	scp -i ~/.ssh/fitpets.pem .envrc ${SERVER_ADDRESS}:/home/ubuntu/runner-bot

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

setup:
	sudo apt install python3-pip -y
	sudo pip3 install --target=/usr/local/lib/python3.8/dist-packages -r requirements.txt 

requirements:
	poetry export -f requirements.txt --output requirements.txt