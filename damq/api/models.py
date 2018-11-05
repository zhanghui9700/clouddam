#-*- coding=utf-8 -*-

import json
import logging

from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from jsonfield import JSONField
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


TRANSACTION_TYPE_CHOICES = (
    (0, _("New Transaction")),
    (1, _("Delete Transaction")),
    (2, _("Update Transaction")),
    (3, _("Update Cert")),
    (4, _("Add IP")),
    (5, _("Delete IP")),
    (6, _("Update Domain")),
)


class Transaction(models.Model):

    transactionId = models.CharField(_("Transaction ID"), max_length=255)
    transactionType = models.IntegerField(_("Transaction Type"), default=0,
                        choices=TRANSACTION_TYPE_CHOICES)
    """
    clientName = models.CharField(_("Client Name"), max_length=255, blank=True)
    alias = models.CharField(_("Alias"), max_length=255, blank=True)
    isBGP = models.BooleanField(_("IsBGP"), default=False)
    isWebSite = models.BooleanField(_("IsWeb"), default=False)
    custIp = models.CharField(_("Custome IP"), max_length=255, blank=True)
    ipVol = models.IntegerField(_("IP Volume"))
    domain = models.CharField(_("Client Domain"), max_length=255, blank=True)
    sourceIp = models.CharField(_("Source IP"), max_length=255, blank=True)
    sourcePortMapping = JSONField(_("Source Port Mapping"), default=[],
                        blank=True)
    registry = models.CharField(_("Registry"), max_length=255, blank=True)
    sslConfig = JSONField(_("SSL Config"), default={}, blank=True)
    """
    message = JSONField(_("MQ Message"), max_length=65535, blank=False)
    deleted = models.BooleanField(_("Deleted"), default=False)
    completed = models.BooleanField(_("Completed"), default=False)
    createDate = models.DateTimeField(_("Create Date"), auto_now_add=True)

    class Meta:
        db_table = 'transaction'
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transaction')
    
    @classmethod
    def create_and_send_mail(cls, mq_message):
        data = mq_message
        tx_type = data.pop('transactionType')
        tx_id = data.pop('transactionId')
        msg = json.dumps(data, sort_keys=True, indent=4, separators=(', ', ': '))
        
        try:
            title = "New Transaction: %s, type: %s" % (tx_id, tx_type)
            result = send_mail(title, msg,
                    settings.EMAIL_FROM, settings.CLOUDDAM_NOTIFY_EMAIL)

            tx = cls.objects.create(
                transactionId = tx_id,
                transactionType = tx_type,
                message = msg
            )
        except Exception as ex:
            logger.exception("Transaction create and save raise exception")

    def __unicode__(self):
        return u'%s:%s' % (self.transactionId, self.transactionType)