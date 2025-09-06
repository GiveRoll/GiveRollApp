from django.db import models
# from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# from GiveRoll import DrawApp
# Create your models here.

class User(AbstractUser):
    brand_name = models.CharField(max_length=150, blank=True, null=True)
    industry = models.CharField(max_length=250, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    block_status = models.BooleanField(default=False)
    full_name = models.CharField(max_length=200, null=True, blank=True)
    phone_number = models.PositiveBigIntegerField(null=True, blank=True)
    DOB = models.DateField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.full_name}"
    

class Draw(models.Model):

    STATUS_CHOICES = [
        ('active', 'active'),
        ('completed', 'completed'),
        ('draft', 'draft'),
    ]
    
    created_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=500)
    action= models.IntegerField(default=0)
    number_participants = models.IntegerField(default=20)
    generate_link = models.CharField(max_length=500, null=True, blank=True)
    embed_link = models.CharField(max_length=500, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    last_drafted = models.DateTimeField(null=True, blank=True)
    ended_date = models.DateTimeField(null=True, blank=True)
    active_till = models.DurationField(null=True, blank=True)
    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    facebook = models.BooleanField(default=False)
    x = models.BooleanField(default=False)
    tiktok = models.BooleanField(default=False)
    instagram = models.BooleanField(default=False)
    youtube = models.BooleanField(default=False)
    number_winners = models.IntegerField(default=1)
    description = models.TextField(blank=True, null=True)
    terms_of_condition = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices= STATUS_CHOICES, default='active')
    created_at = models.TimeField(auto_now=True)

    def __str__(self):
        return f"draw{self.id}"

def save(self, *args, **kwargs):
        if self.start_date and self.end_date:
            self.active_till = self.end_date - self.start_date
        super().save(*args, **kwargs)

class Prize(models.Model):
    name = models.CharField(max_length=250)
    value = models.IntegerField()
    image = models.ImageField(upload_to='prize_images/', blank=True, null=True)
    number_winners = models.IntegerField(default=1)
    draw = models.ForeignKey(Draw, related_name='prizes', on_delete=models.CASCADE, blank=True, null=True,)


class Participants(models.Model):
    name = models.CharField(max_length=100) 
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=7, null=True)
    platform_s = models.CharField(max_length=100, null=True)
    social_handle = models.CharField(max_length=100, blank=True, null=True, unique=True)
    platform_f = models.CharField(max_length=200, null=True)
    draw = models.ForeignKey(Draw, on_delete=models.CASCADE)
    joined_at = models.TimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['draw', 'email'], name='unique_draw_email'),
            models.UniqueConstraint(fields=['draw', 'ip_address'], name='unique_draw_ip'),
            models.UniqueConstraint(fields=['draw', 'social_handle'], name='unique_draw_social_handle'),
        ]

class Winners(models.Model):

    STATUS_CHOICES = [
        ('sent', 'sent'),
        ('not sent', 'not sent'),
        ('pending', 'pending'),
    ]

    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True, null= True)
    social_handle = models.CharField(max_length=100, blank=True, null=True)
    chosen_at = models.DateTimeField(null=False, blank=False) 
    draw = models.ForeignKey(Draw, on_delete=models.CASCADE)
    email_status = models.CharField(max_length=10, choices= STATUS_CHOICES, default='not sent')
    prize_status = models.BooleanField(default=False)
    contact_number = models.PositiveIntegerField(default=0)
    state = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    street_address = models.CharField(max_length=200, null=True, blank=True)

