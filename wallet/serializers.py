from rest_framework import serializers


class FundSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=1000, max_value=100000000)


class TransferSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=1000, max_value=100000000)
    account_number = serializers.CharField(max_length=10, min_length=10)

class WithdrawSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=1000, max_value=100000000)
    # account_number = serializers.CharField(max_length=10, min_length=10)

