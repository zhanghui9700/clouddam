from django.contrib import admin
from .models import Transaction

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'transactionId', 'transactionType', 'completed')
    list_filter = ('completed', )

    class Meta:
        model = Transaction

admin.site.register(Transaction, TransactionAdmin)
