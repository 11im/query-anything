postgres:
	docker-compose -f ./infra/postgres.yml up -d

load_postgres:
	docker exec -it postgres psql -U bigbase -a -f /scripts/createdb.sql
	docker exec -it postgres psql -U bigbase -d testdb -a -f /scripts/test_table.sql