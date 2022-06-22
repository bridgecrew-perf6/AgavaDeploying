from celery import shared_task
import pika
import logging
import time


class Subscriber:
    def __init__(self, config):
        self.config = config
        self.connection = self._create_connection()

    def _create_connection(self):
        parameters = pika.ConnectionParameters(host=self.config['host'],
                                               port=self.config['port'])
        return pika.BlockingConnection(parameters)

    def request(self, routing_key_request, request):
        logging.warning("create request channel")
        channel = self.connection.channel()

        logging.warning("create in point")
        channel.exchange_declare(exchange=self.config['exchange'], exchange_type='topic')

        logging.warning("publish request")
        channel.basic_publish(exchange=self.config['exchange'], routing_key=routing_key_request, body=request)

    def on_message_callback(self, channel, method, properties, body):
        binding_key = method.routing_key

    def setup(self, queue_name, binding_key, routing_key_request, request):
        self.request(routing_key_request, request)
        channel = self.connection.channel()
        channel.exchange_declare(exchange=self.config['exchange1'],
                                 exchange_type='topic')
        channel.queue_declare(queue=queue_name)
        channel.queue_bind(queue=queue_name, exchange=self.config['exchange1'], routing_key=binding_key)
        channel.basic_consume(queue=queue_name,
                              on_message_callback=self.on_message_callback, auto_ack=True)
        while True:
            channel.start_consuming()
            channel.stop_consuming()
            time.sleep(1)

    def __del__(self):
        self.connection.close()


@shared_task
def test_msg(config, queue_name, binding_key, routing_key_request, request):
    logging.warning("create Subscriber")
    subscriber = Subscriber(config)
    logging.warning("launch subscriber")
    subscriber.setup(queue_name, binding_key, routing_key_request, request)
