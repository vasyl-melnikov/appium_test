import pika

# RabbitMQ connection parameters
rabbitmq_host = 'localhost'
rabbitmq_port = 5672
rabbitmq_user = 'guest'
rabbitmq_pass = 'guest'
rabbitmq_virtual_host = '/'
rabbitmq_queue_name = 'my_tasks_queue'

# Callback function to process received tasks
def process_task(ch, method, properties, body):
    print(f"Received Task: {body.decode()}")

    # Simulate task processing (you can replace this with your actual task processing logic)
    import time
    time.sleep(5)

    # Acknowledge the message to RabbitMQ (mark it as processed)
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Create a connection to RabbitMQ server
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=rabbitmq_host,
        port=rabbitmq_port,
        virtual_host=rabbitmq_virtual_host,
        credentials=pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
    )
)

# Create a channel
channel = connection.channel()

# Declare a queue (in case it does not exist)
channel.queue_declare(queue=rabbitmq_queue_name)

# Set the prefetch count to 1 (allowing only one unacknowledged message at a time)
channel.basic_qos(prefetch_count=1)

# Set up a consumer to receive messages from the queue
channel.basic_consume(queue=rabbitmq_queue_name, on_message_callback=process_task)

# Start consuming messages
print("Waiting for tasks. To exit, press CTRL+C")
channel.start_consuming()
