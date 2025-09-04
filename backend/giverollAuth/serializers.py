from rest_framework import serializers
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.utils.translation import gettext_lazy as _


User = get_user_model()

class userManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "full_name", "phone_number", "DOB", "profile_image", "brand_name", "industry", ]

class EntryManagerSerializer(RegisterSerializer):
    
    full_name = serializers.CharField(required=True)

    def custom_signup(self, request, user):
        user.full_name = self.validated_data.get('full_name', '')
        # user.is_active = False
        user.save()
        return user
        
class ManagerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True, required=True)

    def validate(self, attrs):

        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError(_("Both email and password are required."))

        if not EmailAddress.objects.filter(email=email, verified=True).exists():
            raise serializers.ValidationError(_("Email is not verified."))
        
        return attrs