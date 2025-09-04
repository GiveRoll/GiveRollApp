from django.shortcuts import render
from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import DrawSerializer, linkSerializer, dashboardSerializer
from .models import Draw
from rest_framework import permissions, status, generics
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from django.db import IntegrityError
from django.db.models import Count
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your views here.

class ActiveView(generics.ListAPIView):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = dashboardSerializer
    http_method_names = ['get']
    
    def get_queryset(self):
        
        active = Draw.objects.filter(host= self.request.user, status='active').order_by("-created_at")
        return active
    
class CommpletedView(generics.ListAPIView):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = dashboardSerializer
    http_method_names = ['get']
    
    def get_queryset(self):
        
        completed = Draw.objects.filter(host= self.request.user, status='completed').order_by("-created_at")
        return completed
    
class DraftViewset(generics.ListAPIView):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = dashboardSerializer
    http_method_names = ['get']
    
    def get_queryset(self):
        
        draft = Draw.objects.filter(host= self.request.user, status='draft').order_by("-created_at")
        return draft


class DrawLinkView(APIView):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = linkSerializer

    @swagger_auto_schema(request_body=linkSerializer)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(host=request.user)
            return Response({"message":"draw link saved successfully!"},
                             status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk=None): 
        try:
            draw = Draw.objects.get(pk=pk)
        except Draw.DoesNotExist:
            raise NotFound("Draw not found")
        if draw.host != request.user:
            raise PermissionDenied("Access denied")
        if draw.status == "completed":
            return Response({"error":"You can not edit a completed draw!"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(draw, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DraftView(APIView):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DrawSerializer

    @swagger_auto_schema(request_body=DrawSerializer)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(host=request.user, status="draft", last_drafted=timezone.now())
            return Response({"message":"draft created successfully"},
                             status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateDrawView(APIView):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DrawSerializer

    @swagger_auto_schema(request_body=DrawSerializer)
    def post(self, request):
        user = request.user

        if user.block_status == True:
                return Response({"error": "It seems you did not deliver the prize to your winner(s) in the last draw, contact the support for more updates"}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            start_date = serializer.validated_data.get('start_date')
            end_date = serializer.validated_data.get('end_date')
            if start_date < timezone.now() or end_date > timezone.now():
                return Response({"error":"mistake in your date selection"}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(host=user)
            return Response({"message":"draw created successfully"},
                             status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ManageDrawView(APIView):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DrawSerializer
    
    @swagger_auto_schema(request_body=DrawSerializer)
    def put(self, request, pk=None): 
        try:
            draw = Draw.objects.get(pk=pk)
        except Draw.DoesNotExist:
            raise NotFound("Draw not found")
        if draw.host != request.user:
            raise PermissionDenied("Access denied")
        if draw.status == "completed":
            return Response({"error":"You can not edit a completed draw!"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(draw, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk=None):
        try:
            draw = Draw.objects.get(pk=pk)
        except Draw.DoesNotExist:
            raise NotFound("Draw not found!")

        if draw.host != request.user:
            raise PermissionDenied("Access denied")
        
        if draw.status == "completed":
            return Response({"error":"You can not edit a completed draw!"}, status=status.HTTP_400_BAD_REQUEST)

        draw.delete()
        return Response({"message": "Draw deleted"}, status=status.HTTP_204_NO_CONTENT)
