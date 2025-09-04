from django.shortcuts import render
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib import auth
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import userManagerSerializer, ManagerLoginSerializer
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from rest_framework.exceptions import NotFound, PermissionDenied
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from django.utils.translation import gettext_lazy as _



class UserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = userManagerSerializer

    def put(self, request, pk=None): 
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise NotFound("User not found")
        if user != request.user:
            raise PermissionDenied("Access denied")
        serializer = self.serializer_class(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise NotFound("Access denied")

        if user != request.user:
            raise PermissionDenied("Access denied")

        user.delete()
        return Response({"message": "Your account has been deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class SocialLogin(SocialLoginView):

    def post(self, request, *args, **kwargs):
        provider = request.data.get("provider")

        if not provider:
            return Response({"error": "Provider is required."}, status=status.HTTP_400_BAD_REQUEST)


        if provider == "google":
            self.adapter_class = GoogleOAuth2Adapter
        else:
            return Response(
                {"error": "Social media platform not supported"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # allauth handle the social login first
            response = super().post(request, *args, **kwargs)
        except Exception as e:
            return Response({"error": "Social login failed. Please try again."}, status=status.HTTP_400_BAD_REQUEST)

        # JWT token generation
        if request.user and request.user.is_authenticated:
            refresh = RefreshToken.for_user(request.user)
            access = str(refresh.access_token)
            return Response(
                {
                    "access": access,
                    "refresh": str(refresh),
                    "user": {
                        "id": request.user.id,
                        "email": request.user.email,
                        "username": request.user.username,
                    },
                },
                status=status.HTTP_200_OK,
            )

        return response
       
    
class LoginView(APIView):

    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=ManagerLoginSerializer)
    def post(self, request):
        serializer = ManagerLoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        user = auth.authenticate(email=email, password=password)

        if user:
            # if not user.is_active:
            #     return Response({"error": "Account is inactive. Please verify your email."}, status=status.HTTP_403_FORBIDDEN)
            
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "email": user.email,
                },
            })
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    


