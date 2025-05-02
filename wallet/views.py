from uuid import uuid4
from decimal import Decimal
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import responses, Response
from django.shortcuts import render, get_object_or_404
import requests
from .models import Transaction, Wallet
from .serializers import FundSerializer, TransferSerializer


# Create your views here.
#
# def welcome(request):
#     return HttpResponse("Welcome to Eazi Pay")
#
# def greeting(request, name):
#     return HttpResponse(f"Greetings from Eazi Pay, {name}")
#
# def new_greeting(request, name):
#     return render(request, 'hello.html', {'name': name})
#
# @api_view()
# def welcome_New(request):
#     return Response("Welcome to EaziPay")

@permission_classes([IsAuthenticated])
@api_view(['POST'])
def fund_wallet(request):
    if not request.data:
        return Response({"message": "No data provided"},status=status.HTTP_400_BAD_REQUEST)
    data = FundSerializer(data=request.data)
    data.is_valid(raise_exception=True)
    amount = data.validated_data['amount']
    amount *= 100
    email = request.user.email
    reference = f"ref_{uuid4().hex}"
    Transaction.objects.create(
        amount=(amount/100),
        reference=reference,
        sender=request.user,
        transaction_type='D'
    )
    url = 'https://api.paystack.co/transaction/initialize'
    secret = settings.PAYSTACK_SECRET_KEY
    headers = {
        "Authorization": f"Bearer {secret}",
    }
    data = {
        "amount": amount,
        "reference": reference,
        "email": email,
        "callback_url": "http://localhost:8000/wallet/fund/verify",
    }
    try:
        response_str = requests.post(url=url, json=data, headers=headers)
        response = response_str.json()
        if response['status']:
            return Response(data=response['data'], status=status.HTTP_200_OK)
        return Response({"message": "Unable to initialize transaction"}, status=status.HTTP_400_BAD_REQUEST) #None
    except requests.exceptions.RequestException as e:
        return Response({"message": f"Unable to complete transaction. {e}"}, status=status.HTTP_302_FOUND)

@api_view()
def verify_fund(request):
    reference = request.GET.get('reference')
    secret = settings.PAYSTACK_SECRET_KEY
    headers = {
        "Authorization": f"Bearer {secret}",
    }
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    response_str = requests.get(url=url, headers=headers)
    response = response_str.json()
    if response['status'] and response['data']['status'] == "success":
        amount = (response['data']['amount'] / 100)
        try:
            transaction = Transaction.objects.get(reference=reference, verified=False)
        except Transaction.DoesNotExist:
            return Response({"message": "Transaction does not exist"}, status=status.HTTP_404_NOT_FOUND)
        wallet = get_object_or_404(Wallet, user=transaction.sender)
        wallet.deposit(Decimal(amount))
        transaction.verified = True
        transaction.save()

        subject = "Wallet System Transaction Alert"
        message = f"""Deposit transaction occurred on your wallet
        You received: {amount} 
        from {transaction.sender.first_name} {transaction.sender.last_name}
        *****thank you for using Wallet System***"""
        from_email = settings.EMAIL_HOST_USER
        recipient_email = transaction.sender.email

        send_mail(
            subject=subject,
            recipient_list=[recipient_email],
            message=message,
            from_email=from_email
        )

        return Response({"message": "Deposit successful"}, status=status.HTTP_200_OK)
    return Response({"message": "Transaction not successful"}, status=status.HTTP_404_NOT_FOUND)


@permission_classes([IsAuthenticated])
@api_view(['POST'])
def transfer(request):
    data = TransferSerializer(data=request.data)
    data.is_valid(raise_exception=True)
    amount = data.validated_data['amount']
    account_number = data.validated_data['account_number']
    sender = request.user
    sender_wallet = get_object_or_404(Wallet, user=sender)
    receiver_wallet = get_object_or_404(Wallet, account_number=account_number)
    receiver = receiver_wallet.user
    with transaction.atomic():
        reference = f"ref_{uuid4().hex}"
        try:
            sender_wallet.withdraw(amount)
        except ValueError:
            return Response({"message": "Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST)
        Transaction.objects.create(
        amount=amount,
        sender=sender,
        reference=reference,
        transaction_type="T",
        verified=True,
        )
        subject = "Wallet System Transaction Alert"
        message = f"""Debit transaction occurred on your wallet
                You transferred: {amount} 
                to {receiver.first_name} {receiver.last_name}
                *****thank you for using Wallet System***"""
        from_email = settings.EMAIL_HOST_USER
        recipient_email = sender.email

        send_mail(
            subject=subject,
            recipient_list=[recipient_email],
            message=message,
            from_email=from_email
        )
        receiver_wallet.deposit(amount)
        reference = f"ref_{uuid4().hex}"
        Transaction.objects.create(
        amount=amount,
        sender=sender,
        receiver=receiver,
        reference=reference,
        transaction_type="D",
        verified=True,
        )
        subject = "Wallet System Transaction Alert"
        message = f"""Credit transaction occurred on your wallet
                You received: {amount} 
                from {sender.first_name} {sender.last_name}
                *****thank you for using Wallet System***"""
        from_email = settings.EMAIL_HOST_USER
        recipient_email = receiver.email

        send_mail(
            subject=subject,
            recipient_list=[recipient_email],
            message=message,
            from_email=from_email
        )
        return Response({"message": "Transfer successful"}, status=status.HTTP_200_OK)

