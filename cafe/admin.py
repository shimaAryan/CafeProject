from django.contrib import admin
from .models import *


@admin.register(Items)
class ItemsAdmin(admin.ModelAdmin):
    list_display = ['title']


@admin.register(CategoryMenu)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title']


admin.site.register(Like)
admin.site.register(Order)
admin.site.register(Receipt)
