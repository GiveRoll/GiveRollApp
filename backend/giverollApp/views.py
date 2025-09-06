from django.shortcuts import render
from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import DrawSerializer, linkSerializer, dashboardSerializer, WinnerSerializer, ParticipantSerializer, SupportSerializer
from .models import Draw, Participants
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
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction

User = get_user_model()

# Create your views here.


class SupportView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=SupportSerializer)
    def post(self, request):
        serializer = SupportSerializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        sender_email = serializer.validated_data['email']
        subject = serializer.validated_data['subject']
        message = serializer.validated_data['message']

        try:
            email = EmailMessage(
            subject=subject, 
            body=message,
            to=["hellogiveroll@gmail.com"],
            from_email=settings.EMAIL_HOST_USER,
            reply_to=[sender_email]

            )
        
            email.send(fail_silently=False)
            return Response({"message": "Mail successfully sent"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ParticipantsView(APIView):

    permission_classes = [permissions.AllowAny]
    serializer_class = ParticipantSerializer

    @swagger_auto_schema(request_body=ParticipantSerializer)
    def post(self, request, draw_id):
        # draw_id = request.data.get("id")
        if not draw_id:
            return Response({"error": "Draw ID required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            draw = Draw.objects.get(id=draw_id)
        except Draw.DoesNotExist:
            return Response({"error": "Draw not found"}, status=status.HTTP_404_NOT_FOUND)
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        if draw.end_date < timezone.now():
            return Response({"error":"Draw entry has ended"}, status=status.HTTP_403_FORBIDDEN)
        if not draw.is_active:
                return Response ({"error": "Draw is not active, please wait for the next draw"}, status=status.HTTP_403_FORBIDDEN)
        
        with transaction.atomic():
            paricipants = Participants.objects.filter(draw=draw)
            length_p = paricipants.count()
            if length_p == draw.number_participants:
                return Response({"error":"Number of participants limit has been reached"}, status=status.HTTP_403_FORBIDDEN)
        
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            try:
                serializer.save(draw=draw, ip_address=ip)
                return Response({"message":"Entry submitted successfully!"}, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({"error": "You have already joined this draw"}, status=status.HTTP_400_BAD_REQUEST)

        
        
class WinnersPrizeInfo(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=WinnerSerializer)
    def post(self, request):

        serializer = WinnerSerializer(data=request.data)
        draw_id = request.data.get("id")
        email = request.data.get("email")

        if not draw_id:
            return Response({"error": "Draw ID required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            draw = Draw.objects.get(id=draw_id)
        except Draw.DoesNotExist:
            return Response({"error": "Draw not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer.is_valid(raise_exception=True)
        serializer.save(draw=draw)
        email = serializer.validated_data['email']
        send_mail(
            "I just won a giveaway on GiveRoll!",
            f"I just won a giveaway on GiveRoll!\nE-mail:{email}. You can reach me through this email.",
            settings.EMAIL_HOST_USER,
            ["hellogiveroll@gmail.com"],
            fail_silently=False,
        )
        return Response({"message":"Successful submission!"}, status=status.HTTP_200_OK)

class DownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, draw_id):
        # draw_id = request.query_params.get("id")
        if not draw_id:
            return Response({"error": "Draw ID required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            draw = Draw.objects.get(id=draw_id, host=request.user)
        except Draw.DoesNotExist:
            return Response({"error": "Draw not found"}, status=status.HTTP_404_NOT_FOUND)
        
        participants = Participants.objects.filter(draw=draw).order_by("-joined_at")
        if not participants.exists():
            return Response({"error": "no participants yet, share your giveaway draw entry link"}, status=status.HTTP_204_NO_CONTENT)
        
        data = [
            {
            "name": p.name,
            "email": p.email,
            "platform_s": p.platform_s,
            "joined_at": p.joined_at, 
        } for p in participants
        ]

        return Response({"participants": data}, status=status.HTTP_200_OK)

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
        user = request.user
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(host=user)
            generate_link = serializer.validated_data.get('generate_link')
            embed_link = serializer.validated_data.get('embed_link')
            email = user.email
            send_mail(
            "You just created a draw on GiveRoll!",
            f"You just created a Draw on GiveRoll.\nHere is your draw link: {generate_link}, where your participants make entries to your draw. \nHere is your embed link: {embed_link}, you can embed this on OBS. \n Best Regards, \nGiveRoll Team.",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
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
        serializer.is_valid(raise_exception=True)
        start_date = serializer.validated_data.get('start_date')
        end_date = serializer.validated_data.get('end_date')
        if start_date < timezone.now() or end_date < timezone.now():
            return Response({"error":"mistake in your date selection"}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(host=user)
        return Response({"message":"draw created successfully"},
                             status=status.HTTP_201_CREATED)
    
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
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
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
