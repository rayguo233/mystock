from django.db import models
from django.contrib.auth.models import User

class ModelWithTime(models.Model):
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class Transaction(ModelWithTime):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    ticker = models.CharField(max_length=20)
    num_shares = models.IntegerField()
    currency = models.CharField(max_length=20)
    total_cost = models.DecimalField(max_digits=20, decimal_places=6)
    transaction_fee = models.DecimalField(max_digits=10, decimal_places=6)
    transaction_time = models.DateTimeField()

    class Meta:
        unique_together = ['user', 'transaction_time']


class DepositAndWithdrawal(ModelWithTime):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    currency = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=20, decimal_places=6)
    transaction_fee = models.DecimalField(max_digits=10, decimal_places=6)
    transaction_time = models.DateTimeField()


class Holding(ModelWithTime):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    ticker = models.CharField(max_length=20)
    num_shares = models.IntegerField()
    total_cost = models.DecimalField(max_digits=20, decimal_places=6)

    class Meta:
        unique_together = ['user', 'ticker']