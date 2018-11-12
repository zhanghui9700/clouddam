# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('transactionId', models.CharField(max_length=255, verbose_name='Transaction ID')),
                ('transactionType', models.IntegerField(default=0, verbose_name='Transaction Type', choices=[(0, 'New Transaction'), (1, 'Delete Transaction'), (2, 'Update Transaction'), (3, 'Update Cert'), (4, 'Add IP'), (5, 'Delete IP'), (6, 'Update Domain'), (7, 'Register')])),
                ('message', jsonfield.fields.JSONField(default=dict, max_length=65535, verbose_name='MQ Message')),
                ('response', jsonfield.fields.JSONField(default=dict, max_length=65535, verbose_name='Response Message')),
                ('deleted', models.BooleanField(default=False, verbose_name='Deleted')),
                ('completed', models.BooleanField(default=False, verbose_name='Completed')),
                ('createDate', models.DateTimeField(auto_now_add=True, verbose_name='Create Date')),
            ],
            options={
                'db_table': 'transaction',
                'verbose_name': 'Transaction',
                'verbose_name_plural': 'Transaction',
            },
        ),
    ]
