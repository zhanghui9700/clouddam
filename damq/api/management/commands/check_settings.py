#!/usr/bin/env python
# coding=utf-8
from smtplib import SMTPException

from django.conf import settings
from django.core.management import BaseCommand
from django.core.mail import send_mail


class Command(BaseCommand):

    def _log(self, tag, result):
        label = self.style.ERROR("XXX")
        if result:
            label = self.style.MIGRATE_SUCCESS(":-)")

        self.stdout.write("{:<30}{:<5}".format(tag, label))

    def _check_mail(self):
        if len(settings.ADMINS) < 1:
            self._log("CHECK_MAIL No Admin", False)
            return

        try:
            title = "%sCheck Settings" % settings.EMAIL_SUBJECT_PREFIX
            msg = "This message used for checking email settings."
            result = send_mail(title, msg,
                        settings.EMAIL_FROM, [settings.ADMINS[0]])
        except SMTPException as e:
            result = False
            raise e

        self._log("CHECK_MAIL", result)
    
    def _check_rpc_send(self):
        try:
            from rpc import notify
            msg = "{'test': 'This message used for checking email settings.'}"
            notify(msg, routing="transResponse")
        except Exception as e:
            raise e

        self._log("CHECK_RPC_SEND", True)

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("************CHECK START************"))
        self._check_mail()
        self._check_rpc_send()
        self.stdout.write(self.style.WARNING("************CHECK  END*************"))
