#!/usr/bin/env python
import logging
import logging.config
import os
import signal
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from django.conf import settings
from kombu import Connection
from runner.messaging import Receiver
from rpc import RPCConsumer


def start_receive():

    with Connection(settings.WORKER_CONNECTTION) as conn:
        try:
            receiver = Receiver()
            RPCConsumer(conn, receiver).run()
        except (KeyboardInterrupt, SystemExit):
            print("Stopping task consumer ...")


if __name__ == "__main__":
    start_receive()
