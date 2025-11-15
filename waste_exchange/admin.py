from django.contrib import admin
from .models import Business, BusinessImage, Category

admin.site.register(Category)
admin.site.register(Business)
admin.site.register(BusinessImage)
