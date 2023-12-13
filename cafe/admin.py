from django.contrib import admin
from .models import *


@admin.register(Items)
class ItemsAdmin(admin.ModelAdmin):
    list_display = ['title']


@admin.register(CategoryMenu)
class CategoryMenuAdmin(admin.ModelAdmin):
    list_display = ['title']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['title']


admin.site.register(Like)
admin.site.register(ServingTime)
admin.site.register(Receipt)