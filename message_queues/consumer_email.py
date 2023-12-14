#!/usr/bin/env python
import os
import pika
import sys

import smtplib
from email.message import EmailMessage



connection = pika.BlockingConnection(
pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='enrollment_notifications', exchange_type='fanout')

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='enrollment_notifications', queue=queue_name)

def send_email_notification(body):
    server = smtplib.SMTP('localhost',8025)
    server.set_debuglevel(1)
    fromaddr = "titanonline@edu.com"
    toaddrs  = "student@g.com"
    server.sendmail(fromaddr, toaddrs, body)
    #server.quit()
    return

def callback(ch, method, properties, body):
    #print(f" [x] {body.decode()}")
    send_email_notification(body.decode())
    

print(' [*] Waiting for enrollment_notifications. To exit press CTRL+C')
channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)
channel.start_consuming()

