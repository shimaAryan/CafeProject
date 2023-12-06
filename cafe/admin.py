from django.contrib import admin
from .models import *

admin.site.register(Like)
admin.site.register(Receipt)
@admin.register(Items)
<<<<<<< HEAD
class ItemsAdmin(admin.ModelAdmin):
    list_display = ['title' ]


@admin.register(CategoryMenu)
class CategoryMenuAdmin(admin.ModelAdmin):
    list_display = ['title']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = []
=======
class ItemAdmin(admin.ModelAdmin):
    list_display = ['title']


@admin.register(CategoryMenu)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title']


admin.site.register(Order)
>>>>>>> 91d24123217ce67702e7574603d5bca1bd6a4d87
