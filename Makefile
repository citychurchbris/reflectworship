# Django development makefile
default: dev

# Build dev environment
dev: venv requirements.txt
	./venv/bin/pip install -r requirements.txt --upgrade

# Set up virtualenv
venv:
	@python3 -m venv venv
	./venv/bin/pip install --upgrade pip

# Update requirements.txt pins
freeze: venv
	./venv/bin/pip freeze > requirements.txt

# Run tests
test: venv
	./venv/bin/python manage.py test
	./venv/bin/coverage html

# Watch for file changes and repeat tests
# Requires 'ack' and 'entr' tools
test-repeat: venv
	ack -f --python | entr ./venv/bin/python manage.py test -k

# Generate HTML coverage
coverage:
	./venv/bin/python -m webbrowser file://$$PWD/htmlcov/index.html

# Start a browsersync server for the coverage files
coverage-server:
	browser-sync start --server htmlcov --files "htmlcov/*.html"

# Add heroku remotes for deployment
heroku-setup:
	#git remote add heroku https://git.heroku.com/reflectworship.git
	heroku git:remote -a reflectworship-free

# Deploy and run migrations on heroku
deploy:
	@git push heroku master

# Remove venv
clean:
	rm -rf venv

# Phony targets
.PHONY: dev hooks check config-check freeze test coverage deploy clean heroku-setup
