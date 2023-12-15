
enrollment_service: uvicorn enrollment_service.enrollment_service:app --port $PORT --reload

login_service_primary: ./bin/litefs mount -config etc/primary.yml
login_secondary: ./bin/litefs mount -config etc/secondary.yml
login_tertiary: ./bin/litefs mount -config etc/tertiary.yml

worker: echo ./etc/krakend.json | krakend run --config etc/krakend.json --port $PORT

dynamodb: java -Djava.library.path=./dynamodb_local_latest/DynamoDBLocal_lib -jar ./dynamodb_local_latest/DynamoDBLocal.jar -sharedDb --port $PORT

smtp: python -m aiosmtpd -n -l:$PORT

consumer_email: python ./message_queues/consumer_email.py

consumer_webhooks: python ./message_queues/consumer_webhooks.py
