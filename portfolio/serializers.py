from django.contrib.auth.models import User
from rest_framework import serializers
from portfolio.models import Transaction, Holding


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['user']

class HoldingSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['user'] = User.objects.get(pk=ret['user']).get_full_name()
        return ret

    class Meta:
        model = Holding
        fields = '__all__'
        read_only_fields = ['user']
