MANAGE=python manage.py
APPS=account construction
BACKUP_DIR=_backup
ARCHIVE_DIR="${BACKUP_DIR}/archive"

# Makes sure that any files named as the targets won't affect the Makefile rules
.PHONY: reqs deletemigrations migrate remigrate resetdb test coverage reloadnode rebuildnode bash shell seed restoredb dumpdata loaddata backup

# If the first argument is "test"...
ifeq (test,$(firstword $(MAKECMDGOALS)))
  # use the rest as arguments for "test"
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # ...and turn them into do-nothing targets
  $(eval $(RUN_ARGS):;@:)
endif

reqs:
	@echo "Installing requirements for the backend"
	@./shell_inside_docker.sh "pip install -r requirements.txt"

deletemigrations:
	@echo "Deleting all pre-existing migrations"
	@./shell_inside_docker.sh "GLOBIGNORE='cbcommon/migrations/0*'; rm -f */migrations/0*"

migrate:
	@echo "Creating missing migrations and migrating all apps"
	@./shell_inside_docker.sh "$(MANAGE) makemigrations $(APPS) && $(MANAGE) migrate"

remigrate:
	@echo "Recreate all migrations and apply them to the existing database without affecting the actual data"
	@$(MAKE) deletemigrations
	@./shell_inside_docker.sh "$(MANAGE) makemigrations $(APPS) && $(MANAGE) migrate --fake-initial"

resetdb:
	@echo "Creating an empty database"
	@docker-compose rm -sf db
	@docker-compose up -d db
	@sleep 3
	@$(MAKE) remigrate

comparesettings:
	@echo "Backend settings\n"
	@diff src/backend/env/settings.env src/backend/env/settings.env-template || exit 0
	@echo "\nFrontend settings"
	@diff src/frontend/.env src/frontend/.env-template || exit 0

resetsettings:
	@cp src/backend/env/settings.env-template src/backend/env/settings.env
	@cp src/frontend/.env-template src/frontend/.env

test:
	@echo "Running Django test runner"
	@./shell_inside_docker.sh "./manage.py test $(RUN_ARGS)"

coverage:
	@echo "Calculating coverage"
	@./shell_inside_docker.sh "./calculate_coverage.sh"

reloadweb:
	@echo "Restarting the web container"
	@docker-compose restart -t 0 web

reloadnode:
	@echo "Restarting the node container"
	@docker-compose restart -t 0 node

rebuildweb:
	@echo "Rebuilding the web container"
	@docker-compose stop -t 0 web && docker-compose up -d --build web

rebuildnode:
	@echo "Rebuilding the node container"
	@docker-compose stop -t 0 node && docker-compose up -d --build node

bash:
	@echo "Starting a bash shell in the Django web container"
	@./shell_inside_docker.sh "bash"

shell:
	@echo "Starting a Django shell in the Django web container"
	@./shell_inside_docker.sh "$(MANAGE) shell"

seed:
	@echo "Generates user data and seeds the database"
	@./shell_inside_docker.sh "$(MANAGE) generate_user_data && $(MANAGE) seed_app"

seedsuperuser:
	@echo "Seeds the database with the superuser only"
	@./shell_inside_docker.sh "$(MANAGE) seed_app --superuser"

reseed:
	@echo "Reseeds the database"
	@./shell_inside_docker.sh "$(MANAGE) seed_app"

backup:
	@echo "Backup will be directed to 'src/backend/${BACKUP_DIR}/'"
	@./shell_inside_docker.sh "mkdir -p ${BACKUP_DIR} && mkdir -p ${ARCHIVE_DIR}"
	@-./shell_inside_docker.sh "cp -f --backup=numbered -t ${ARCHIVE_DIR}/ ${BACKUP_DIR}/git_info.txt ${BACKUP_DIR}/git_diff.txt ${BACKUP_DIR}/account.json ${BACKUP_DIR}/cbcommon.json ${BACKUP_DIR}/construction.json ${BACKUP_DIR}/private.json ${BACKUP_DIR}/media.tgz"
	@-./shell_inside_docker.sh "git log --oneline | head -n 1 > ${BACKUP_DIR}/git_info.txt"
	@-./shell_inside_docker.sh "git diff > ${BACKUP_DIR}/git_diff.txt"
	@./shell_inside_docker.sh "$(MANAGE) dumpdata account > ${BACKUP_DIR}/account.json"
	@./shell_inside_docker.sh "$(MANAGE) dumpdata construction > ${BACKUP_DIR}/construction.json"
	@-./shell_inside_docker.sh "tar -czvf ${BACKUP_DIR}/media.tgz ../../media"

restore:
	@./shell_inside_docker.sh "$(MANAGE) loaddata ${BACKUP_DIR}/account.json"
	@./shell_inside_docker.sh "$(MANAGE) loaddata ${BACKUP_DIR}/construction.json"
	@./shell_inside_docker.sh "tar -xzvf ${BACKUP_DIR}/media.tgz -C ../../"
