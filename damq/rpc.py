# -*- coding: utf-8 -*-
import os
import logging
import json
import traceback

from kombu import Connection, Exchange, Queue, uuid, Producer, Consumer
from kombu.mixins import ConsumerMixin
import amqp.exceptions as amqp_exceptions
from django.conf import settings

LOG = logging.getLogger(__name__)

exec_exchange = Exchange(
    'hiddos',
    'topic',
    durable=False
)

message_queue = Queue(
    'transMessage',
    exchange=exec_exchange,
    routing_key='transMessage'
)

response_queue = Queue(
    'transResponse',
    exchange=exec_exchange,
    routing_key='transResponse'
)


class ConsumerProducerMixin(ConsumerMixin):
    """
    This class is copied from kombu.mixins
    see https://github.com/celery/kombu/issues/530
    """
    _producer_connection = None

    def on_consume_end(self, connection, channel):
        if self._producer_connection is not None:
            self._producer_connection.close()
            self._producer_connection = None

    @property
    def producer(self):
        return Producer(self.producer_connection)

    @property
    def producer_connection(self):
        if self._producer_connection is None:
            conn = self.connection.clone()
            conn.ensure_connection(self.on_connection_error,
                                   self.connect_max_retries)
            self._producer_connection = conn
        return self._producer_connection


def notify(message, routing='transResponse'):
    LOG.info("Send msg `%s`, route=%s", message, routing)

    with Connection(settings.WORKER_CONNECTTION) as conn:
        with conn.Producer(serializer='json') as producer:
            try:
                producer.publish(message,
                                 exchange=exec_exchange,
                                 routing_key=routing,
                                 declare=[response_queue])
            except amqp_exceptions.PreconditionFailed as e:
                LOG.exception("Send message failed")


class RPCConsumer(ConsumerProducerMixin):

    def __init__(self, connection, receiver):
        self.connection = connection
        self.receiver = receiver

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=[message_queue],
                         callbacks=[self.on_message])]

    def on_message(self, body, msg):
        callback = getattr(self.receiver, 'process')
        try:
            LOG.info('Receive msg body=%s routing=%s', body, msg.delivery_info['routing_key'])
            callback(body, msg, self)
        except KeyboardInterrupt:
            LOG.error("Receiverd interrupted.")
            msg.requeue()
            raise
        except Exception:
            LOG.error(traceback.format_exc())

    def on_precondition_failed(self, error_msg):
        LOG.warning(error_msg)

    def run(self, *args, **kwargs):
        try:
            super(RPCConsumer, self).run(*args, **kwargs)
        except amqp_exceptions.PreconditionFailed as e:
            self.on_precondition_failed(str(e))
            self.run(*args, **kwargs)
