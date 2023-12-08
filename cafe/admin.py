from django.contrib import admin
from .models import *

admin.site.register(Like)
admin.site.register(Receipt)
@admin.register(Items)
class ItemsAdmin(admin.ModelAdmin):
    list_display = ['title' ]


@admin.register(CategoryMenu)
class CategoryMenuAdmin(admin.ModelAdmin):
    list_display = ['title']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = []
