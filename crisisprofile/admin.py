from django.contrib import admin
from .models import Profile, UserHasAccessTo

admin.site.register(Profile)
admin.site.register(UserHasAccessTo)
