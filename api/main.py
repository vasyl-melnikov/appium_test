import pika

# RabbitMQ connection parameters
rabbitmq_host = 'localhost'
rabbitmq_port = 5672
rabbitmq_user = 'guest'
rabbitmq_pass = 'guest'
rabbitmq_virtual_host = '/'
rabbitmq_queue_name = 'my_tasks_queue'

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

# Declare a queue
channel.queue_declare(queue=rabbitmq_queue_name)

# Publish tasks to the queue
for task_id in range(1, 6):
    task_message = f'Task {task_id}'
    channel.basic_publish(
        exchange='',
        routing_key=rabbitmq_queue_name,
        body=task_message
    )
    print(f"Published: {task_message}")

# Close the connection
connection.close()
