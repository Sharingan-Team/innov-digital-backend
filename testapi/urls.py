# testapi/urls.py
from django.urls import path
from .views import TestAPIView, AdminOnlyAPIView, Test

urlpatterns = [
    path('test/', Test.as_view(), name='test'),
    path('authenticated-only/', TestAPIView.as_view(), name='test-api'),
    path('admin-only/', AdminOnlyAPIView.as_view(), name='admin-api'),
]
