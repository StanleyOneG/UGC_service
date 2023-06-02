#!/bin/bash

while [ "`docker inspect -f {{.State.Health.Status}} mongors1n1`" != "healthy" ]; do sleep 2; done
echo "mongors1n1 ready"
while [ "`docker inspect -f {{.State.Health.Status}} mongors1n2`" != "healthy" ]; do sleep 2; done
echo "mongors1n2 ready"
while [ "`docker inspect -f {{.State.Health.Status}} mongors1n3`" != "healthy" ]; do sleep 2; done
echo "mongors1n3 ready"
while [ "`docker inspect -f {{.State.Health.Status}} mongors2n1`" != "healthy" ]; do sleep 2; done
echo "mongors2n1 ready"
while [ "`docker inspect -f {{.State.Health.Status}} mongors2n2`" != "healthy" ]; do sleep 2; done
echo "mongors2n2 ready"
while [ "`docker inspect -f {{.State.Health.Status}} mongors2n3`" != "healthy" ]; do sleep 2; done
echo "mongors2n3 ready"

echo "MONGODB CLUSTER IS READY"

docker exec -it mongocfg1 bash -c 'echo "rs.initiate({_id: \"mongors1conf\", configsvr: true, members: [{_id: 0, host: \"mongocfg1\"}, {_id: 1, host: \"mongocfg2\"}, {_id: 2, host: \"mongocfg3\"}]})" | mongosh'

docker exec -it mongocfg1 bash -c 'echo "rs.status()" | mongosh'

sleep 5

docker exec -it mongors1n1 bash -c 'echo "rs.initiate({_id: \"mongors1\", members: [{_id: 0, host: \"mongors1n1\"}, {_id: 1, host: \"mongors1n2\"}, {_id: 2, host: \"mongors1n3\"}]})" | mongosh'

docker exec -it mongors1n1 bash -c 'echo "rs.status()" | mongosh'

sleep 5

docker exec -it mongos1 bash -c 'echo "sh.addShard(\"mongors1/mongors1n1\")" | mongosh'

sleep 5

docker exec -it mongors2n1 bash -c 'echo "rs.initiate({_id: \"mongors2\", members: [{_id: 0, host: \"mongors2n1\"}, {_id: 1, host: \"mongors2n2\"}, {_id: 2, host: \"mongors2n3\"}]})" | mongosh'

docker exec -it mongos1 bash -c 'echo "sh.addShard(\"mongors2/mongors2n1\")" | mongosh'

docker exec -it mongos1 bash -c 'echo "sh.status()" | mongosh'
