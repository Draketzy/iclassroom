from django.contrib import admin
from .models import User, Institution

# Register your models here.
admin.site.register(User)
admin.site.register(Institution)