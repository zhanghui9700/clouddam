import logging
import json

from django.db import close_old_connections
from api.models import Transaction

LOG = logging.getLogger(__name__)

class ClientTransaction(object):

    def new_site(self, data):
        Transaction.create_and_send_mail(data)
        tx_type = data.pop('transactionType')
        tx_id = data.pop('transactionId')
        tx = Transaction.objects.create(
            transactionId = tx_id,
            transactionType = tx_type,
            message = json.dumps(data, sort_keys=True, indent=4, separators=(', ', ': '))
        )
        LOG.info('Create new site %s', tx)


class Endpoint(object):

    def on_acknowledge(self, message, options):
        options.ack()


class RpcEndpoint(Endpoint):
    routing = 'op'

    def on_message(self, message, options, ctx):
        LOG.info('Receive result body=%s', message)
        # RPC method, need to return func result
        data = json.loads(message)
        #tx_type = data.pop('transactionType')
        #tx_id = data.pop('transactionId')
        tx = ClientTransaction()
        tx.new_site(data)

        result = {}


class Receiver(object):

    def __init__(self):
        self.endpoints = [RpcEndpoint]

    def process(self, message, options, ctx):

        close_old_connections()
        for endpoint in self.endpoints:
            if options.delivery_info['routing_key'] == endpoint.routing:
                processer = endpoint()
                processer.on_message(message, options, ctx)
                processer.on_acknowledge(message, options)
                break
        else:
            LOG.error('Message topic %s not supported',
                     options.delivery_info['routing_key'])
