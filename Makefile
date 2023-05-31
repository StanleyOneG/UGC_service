service_up:
	docker-compose -f kafka/docker-compose.yaml up --build -d
	docker-compose -f etl-kafka-ch/docker-compose.yaml up --build -d
	docker-compose -f mongodb/docker-compose.yaml up --build -d
	./mongodb/configuration.sh
	docker-comopse -f ugc_api/docker-compose.yaml up --build -d
