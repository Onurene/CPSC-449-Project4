#!/usr/bin/env python
import os
import pika
import sys
import httpx
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='enrollment_notifications', exchange_type='fanout')

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='enrollment_notifications', queue=queue_name)

def send_webhook(body, url):
    r = httpx.post(url, data={'key': body})
    print(r.text)
    return

def callback(ch, method, properties, body):
    #print(f" [x] {body.decode()}")
    # the url provided should be user sent and not hardcode
    url = 'https://httpbin.org/post'
    send_webhook(body.decode(), url)
    ch.basic_ack(delivery_tag = method.delivery_tag)

print(' [*] Waiting for enrollment_notifications. To exit press CTRL+C')
channel.basic_consume(
    queue=queue_name, on_message_callback=callback)

channel.start_consuming()
