from django.shortcuts import render

# Create your views here.
# testapi/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

class Test(APIView):
    def get(self, request):
        return Response({"message": f"Hello "})

class TestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": f"Hello {request.user.username}, you're authenticated!"})


class AdminOnlyAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        return Response({"message": f"Hello Admin {request.user.username}"})
