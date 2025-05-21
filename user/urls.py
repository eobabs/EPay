from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import ProfileViewSet

router = DefaultRouter()
router.register('profile', ProfileViewSet, basename='profile')


urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', views.DashBoardView.as_view(), name='dashboard'),
path('verify/email/send/', views.send_email_verification, name='send_email_verification'),
path('verify/email/confirm/', views.confirm_email_verification, name='confirm_email_verification'),
path('verify/documents/upload/', views.upload_verification_documents, name='upload_verification_documents'),
]