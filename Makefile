IMAGE_NAME=aggregator-api:production

docker-build:
	docker build --platform=linux/x86_64 -t $(IMAGE_NAME) .

build:
	docker-compose -f docker-compose.yml build

run:
	docker-compose -f docker-compose.yml --env-file=./.env up -d

run\:debug:
	docker-compose -f docker-compose.yml up

down:
	docker-compose -f docker-compose.yml down

restart:
	make down && make run

lint:
	docker-compose -f docker-compose.yml run --no-deps --rm aggregator black --check --line-length=80 aggregator 
	docker-compose -f docker-compose.yml run --no-deps --rm aggregator autoflake --recursive --check aggregator
	docker-compose -f docker-compose.yml run --no-deps --rm aggregator isort --line-length 80 --profile black --project aggregator --check aggregator

format:
	autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place aggregator --exclude=__init__.py
	black aggregator --line-length 80
	isort --profile black aggregator --line-length 80