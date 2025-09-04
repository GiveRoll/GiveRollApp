from django.contrib import admin
from .models import Draw, Participants, Winners, User, Prize

# Register your models here.
admin.site.register(Draw)
admin.site.register(Participants)
admin.site.register(Winners)
admin.site.register(User)
admin.site.register(Prize)
