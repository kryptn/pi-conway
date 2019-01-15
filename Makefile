put-on-pi:
	scp Makefile *.py pi@192.168.1.146:proj/code/
run-pi-server:
	sudo env/bin/python pi_server.py
run-pi-runner:
	sudo env/bin/python pi_runner.py