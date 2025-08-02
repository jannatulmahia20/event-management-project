from django.contrib import admin
from .models import Event, Participant, Category
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import Profile

admin.site.register(Profile)


admin.site.register(Event)
admin.site.register(Participant)
admin.site.register(Category)


# Register your models here.
