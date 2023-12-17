#!/usr/bin/env python
import re
import pika
import httpx
import redis

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='enrollment_notifications', exchange_type='fanout')

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='enrollment_notifications', queue=queue_name)

r = redis.Redis()


def send_webhook(body, url):
    try:
        # Try to send message to webhook
        res = httpx.post(url, data={'key': body})
        res.raise_for_status()
    except httpx.HTTPError as http_err:
        print(f" [x] HTTP error occurred: {http_err}")
        return
    except Exception as err:
        print(f" [x] An error occurred: {err}")
        return
    else:
        print(res.status_code)

    return


def callback(ch, method, properties, body):
    print(f" [x] {body.decode()}")

    # Define a regular expression to find numbers in the string from the producer
    pattern = re.compile(r'\d+')
    numbers = pattern.findall(body.decode())

    student_id = numbers[2]
    class_id = numbers[1]

    subscription_key = f'student{student_id}:sub{class_id}'

    # Check if student is subscribed to notifications
    if r.exists(subscription_key):
        student_data = r.smembers(subscription_key)

        # Extract webhook url
        json_string = ''.join(data.decode('utf-8') for data in student_data)
        webhook_match = re.search(r"'webhook_url': '([^']+)'", json_string)
        webhook_url = webhook_match.group(1) if webhook_match else None
        send_webhook(body.decode(), webhook_url)


print(' [*] Waiting for enrollment_notifications. To exit press CTRL+C')
channel.basic_consume(
    queue=queue_name, on_message_callback=callback)

channel.start_consuming()
