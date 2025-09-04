from rest_framework import serializers
from .models import Draw, Prize


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
    prize = serializers.PrimaryKeyRelatedField(queryset=Prize.objects.all())
    class Meta:
        model = Draw
        fields = ["title", "description", "terms_of_condition", "start_date", "end_date", "number_participants", "prize", "facebook", "x", "tiktok", "instagram", "youtube"]

    def validate_number_participants(self, value):
        if value > 20:
            raise serializers.ValidationError("Number of participants cannot be more than 20")
        return value
    
    def create(self, validated_data):
        prizes_data = validated_data.pop('prize', [])
        draw = Draw.objects.create(prize=prizes_data, **validated_data)

        # draw.prize.set(prizes_data)

        # for prize_data in prizes_data:
        #     Prize.objects.create(draw=draw, **prize_data)

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