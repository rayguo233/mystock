from django.contrib.auth.models import User
from portfolio.models import SplitTransaction, Transaction, Holding
from rest_framework import serializers


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['user']


class HoldingSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['user'] = User.objects.get(pk=ret['user'])\
            .get_full_name()
        return ret

    class Meta:
        model = Holding
        fields = '__all__'
        read_only_fields = ['user']


class SplitTransactionSerializer(serializers.Serializer):
    
    class Meta:
        model = SplitTransaction
        exclude = ['to_transaction']
    
    def validate(self, data):
        if data['num_shares_transferred'] < 1:
            raise serializers.ValidationError(
                "Field 'num_shares_transferred' must be greater "
                "than 0.")
        if data['num_shares_transferred'] > Transaction.objects.get(
        pk=data['from_transaction_id']).num_shares:
            raise serializers.ValidationError("Field "
                "'num_shares_transferred' must be smaller than "
                "'num_shares' of the source transaction.")
        return data