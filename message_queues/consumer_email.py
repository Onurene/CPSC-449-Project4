#!/usr/bin/env python
import re
import pika
import smtplib
import redis

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
r = redis.Redis()

channel.exchange_declare(exchange='enrollment_notifications', exchange_type='fanout')

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='enrollment_notifications', queue=queue_name)


def send_email_notification(toaddrs, class_id):
    server = smtplib.SMTP('localhost', 5600)
    fromaddr = "titanonline@edu.com"
    body = "You have been enrolled into class " + class_id
    server.sendmail(fromaddr, toaddrs, body)
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

        # Extract email from data
        string_data = [data.decode('utf-8') for data in student_data]
        email_string = next(s for s in string_data if 'email_id' in s)
        email = re.search(r"'email_id': '([^']+)'", email_string).group(1)
        send_email_notification(email, class_id)
        print(f" [x] Email sent to student " + student_id)


print(' [*] Waiting for enrollment_notifications. To exit press CTRL+C')
channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)
channel.start_consuming()
