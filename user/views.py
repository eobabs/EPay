from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from wallet.models import Transaction
from .models import Profile
from .serializers import ProfileSerializer, TransactionSerializer
from .services import send_verification_email, check_verification_code


class ProfileViewSet(ModelViewSet):
    serializer_class = ProfileSerializer

    def get_queryset(self):
        try:
            return Profile.objects.filter(user=self.request.user)
        except Profile.DoesNotExist:
            return Profile.objects.none()

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdminUser()]
        else:
            return [IsAuthenticated()]


class DashBoardView(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request):
        try:
            transactions = Transaction.objects.filter(Q(sender=request.user) | Q(receiver=request.user)).order_by('-transaction_time')[:5]
            serializer = TransactionSerializer(transactions, many=True)
            return Response({"transactions": serializer.data}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_email_verification(request):
    user = request.user
    if user.is_verified:
        return Response({"message": "User is already verified"}, status=status.HTTP_200_OK)

    try:
        send_verification_email(user)
        return Response({"message": "Verification code sent to your email"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": f"Failed to send verification email: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_email_verification(request):
    user = request.user
    code = request.data.get('code')

    if not code:
        return Response({"message": "Verification code is required"}, status=status.HTTP_400_BAD_REQUEST)

    if user.is_verified:
        return Response({"message": "User is already verified"}, status=status.HTTP_200_OK)

    if check_verification_code(user, code):
        return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)
    else:
        return Response({"message": "Invalid or expired verification code"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_verification_documents(request):
    user = request.user

    try:
        try:
            profile = Profile.objects.get(user=user)
            created = False
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=user)
            created = True

        id_document = request.FILES.get('id_document')
        address_document = request.FILES.get('address_document')

        if id_document:
            profile.id_document = id_document
            profile.id_verification_status = 'pending'

        if address_document:
            profile.address_document = address_document
            profile.address_verification_status = 'pending'

        profile.save()

        return Response({
            "message": "Documents uploaded successfully and pending verification",
            "id_status": profile.id_verification_status,
            "address_status": profile.address_verification_status
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": f"Failed to upload documents: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)