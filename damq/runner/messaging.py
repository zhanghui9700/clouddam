import logging
import json

from django.db import close_old_connections
from api.models import Transaction

LOG = logging.getLogger(__name__)

class ClientTransaction(object):

    def new_site(self, data):
        tx = Transaction.create_and_send_mail(data)
        LOG.info('Create new site %s', tx)


class Endpoint(object):

    def on_acknowledge(self, message, options):
        options.ack()


class RpcEndpoint(Endpoint):

    def on_message(self, message, options, ctx):
        # RPC method, need to return func result
        data = json.loads(message)
        tx = ClientTransaction()
        tx.new_site(data)


class Receiver(object):

    def process(self, message, options, ctx):
        processer = RpcEndpoint()
        processer.on_message(message, options, ctx)
        processer.on_acknowledge(message, options)
