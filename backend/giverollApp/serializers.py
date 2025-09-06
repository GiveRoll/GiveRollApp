from rest_framework import serializers
from .models import Draw, Prize, Winners, Participants


class SupportSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254, required=True)
    subject = serializers.CharField(max_length=250, required=True)
    message= serializers.CharField(max_length=2000, required=True)

class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participants
        fields = ['name', 'email', 'gender', 'platform_s', 'social_handle', 'platform_f']
        # read_only_fields = ['draw', 'joined_at']

class WinnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Winners
        fields = ['name', 'email', 'social_handle', 'contact_number', 'state', 'city', 'street_address']

class dashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Draw
        fields = ["id", "title", "description", "number_participants", "end_date", "status"]

class prizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prize
        fields = ['name', 'value', 'image', 'number_winners']

class linkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Draw
        fields = ["generate_link", "embed_link"]

class DrawSerializer(serializers.ModelSerializer):
    prizes = prizeSerializer(many=True)
    class Meta:
        model = Draw
        fields = ["title", "description", "terms_of_condition", "start_date", "end_date", "number_participants", "prizes", "facebook", "x", "tiktok", "instagram", "youtube"]

    def validate_number_participants(self, value):
        if value > 20:
            raise serializers.ValidationError("Number of participants cannot be more than 20")
        return value
    
    def create(self, validated_data):
        prizes_data = validated_data.pop('prizes', [])
        draw = Draw.objects.create(**validated_data)
        for prize_data in prizes_data:
            Prize.objects.create(draw=draw, **prize_data)

        return draw

    def update(self, instance, validated_data):
        prizes_data = validated_data.pop('prize', [])

        # Update draw fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Merge prizes instead of replacing
        for prize_data in prizes_data:
            prize_id = prize_data.get("id", None)
            if prize_id:
                # Update existing prize
                prize = Prize.objects.filter(id=prize_id, draw=instance).first()
                if prize:
                    for attr, value in prize_data.items():
                        setattr(prize, attr, value)
                    prize.save()
            else:
                # Create new prize
                Prize.objects.create(draw=instance, **prize_data)

        return instance