service_up:
	docker compose -f ../Auth_sprint_1/docker-compose.yaml up --build -d
	docker compose -f kafka/docker-compose.yaml up --build -d
	docker compose -f etl-kafka-ch/docker-compose.yaml up --build -d
	docker compose -f mongodb/docker-compose.yaml up --build -d
	./mongodb/configuration.sh
	docker compose -f ugc_api/docker-compose.yaml up --build -d

service_reup:
	docker stop `docker ps -a -q`
	docker container prune -f
	docker volume prune -f
	rm -rf  /tmp/mongo_cluster/data1 /tmp/mongo_cluster/data2 /tmp/mongo_cluster/data3 \
	/tmp/mongo_cluster/data4 /tmp/mongo_cluster/data5 /tmp/mongo_cluster/data6 /tmp/mongo_cluster/config1 \
	/tmp/mongo_cluster/config2 /tmp/mongo_cluster/config3
	docker compose -f ../Auth_sprint_1/docker-compose.yaml up --build -d
	docker compose -f kafka/docker-compose.yaml up --build -d
	docker compose -f etl-kafka-ch/docker-compose.yaml up --build -d
	docker compose -f mongodb/docker-compose.yaml up --build -d
	./mongodb/configuration.sh
	docker compose -f ugc_api/docker-compose.yaml up --build -d

service_api_restart:
	docker stop ugc_api
	docker compose -f ugc_api/docker-compose.yaml up --build -d ugc_api

service_stop:
	docker stop `docker ps -a -q`

service_prune:
	docker stop `docker ps -a -q`
	docker container prune -f
	docker volume prune -f
	rm -rf  /tmp/mongo_cluster/data1 /tmp/mongo_cluster/data2 /tmp/mongo_cluster/data3 \
	/tmp/mongo_cluster/data4 /tmp/mongo_cluster/data5 /tmp/mongo_cluster/data6 /tmp/mongo_cluster/config1 \
	/tmp/mongo_cluster/config2 /tmp/mongo_cluster/config3
	docker compose -f ../Auth_sprint_1/docker-compose.yaml down -v
