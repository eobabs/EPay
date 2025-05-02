from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers
from wallet.models import Transaction
from .models import Profile, User


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['first_name', 'last_name', 'email', 'username', 'password', 'phone_number']


class ProfileSerializer(serializers.ModelSerializer):
    bvn = serializers.CharField(max_length=11, min_length=11)
    class Meta:
        model = Profile
        fields = ['user', 'image', 'address', 'bvn', 'nin']


class WalletSerializer(serializers.Serializer):
    balance = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    account_number = serializers.CharField(max_length=10)

class UserSerializer(serializers.ModelSerializer):
    wallet = WalletSerializer()
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'phone_number', 'wallet']


class TransactionSerializer(serializers.ModelSerializer):
    sender = UserSerializer()

    class Meta:
        model = Transaction
        fields = [
            'id',
            'sender',
            'receiver',
            'amount',
            'transaction_type',
            'transaction_time',
        ]

#
#
# class DashBoardSerializer(serializers.ModelSerializer):
#     balance = serializers.SerializerMethodField()
#     recent_transactions = serializers.SerializerMethodField()
#     full_name = serializers.SerializerMethodField()
#
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'email', 'phone_number', 'full_name', 'balance', 'recent_transactions']
#
#     def get_balance(self, obj):
#         try:
#             wallet = obj.wallet
#             return wallet.balance
#         except:
#             return 0
#
#     def get_full_name(self, obj):
#         return f"{obj.first_name} {obj.last_name}"
#
#     def get_recent_transactions(self, obj):
#         transactions = Transaction.objects.filter(
#             models.Q(sender=obj) | models.Q(receiver=obj)
#         ).order_by('-transaction_time')[:5]
#
#         data = {
#             'username': obj.username,
#             'email': obj.email,
#             'wallet': obj.wallet,
#             'balance': self.get_balance(obj),
#             'recent_transactions': transactions
#         }
#
#         return data
#
#         return TransactionSerializer(transactions, many=True).data