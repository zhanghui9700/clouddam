#-*- coding=utf-8 -*-
from __future__ import unicode_literals
import json

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from .models import Transaction

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'transactionId', 'transactionType', 'completed', 'createDate')
    list_filter = ('completed', "transactionType")

    change_form_template = "admin/custom_change_template.html"

    def response_change(self, request, obj):
        if "_make_completed" in request.POST:
            response = request.POST.get("response")
            print response
            try:
                from rpc import notify
                _json = json.loads(response)
                _mq_notify = json.dumps(_json, ensure_ascii=False, sort_keys=True)
                print _mq_notify
                #notify(_mq_notify, routing="transResponse")
                obj.response = response
                obj.completed = True
                obj.save()
            except Exception as e:
                raise e

            self.message_user(request, _("Make Completed And Send RPC"))
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)
    
    def has_add_permission(self, request, obj=None):
        return False

    class Meta:
        model = Transaction

admin.site.register(Transaction, TransactionAdmin)
