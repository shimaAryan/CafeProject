from django.contrib import admin
from core.models import Image
from .models import *


@admin.register(Items)
class ItemsAdmin(admin.ModelAdmin):
    list_display = ['title']



@admin.register(CategoryMenu)
class CategoryMenuAdmin(admin.ModelAdmin):
    list_display = ['title']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_time']


# class OrderAdmin(admin.ModelAdmin):
#     list_display = ['id', 'user', 'status', 'order_time', 'order_count_by_season']
#     search_fields = ['user__username', ]
#     list_filter = ['order_time']
#
#
#     def(self, obj):
#         order_counts_by_season = (
#             Order.objects
#             .filter(user=obj.user)
#             .annotate(month=TruncMonth('order_time'))
#             .values('month__month')
#             .annotate(order_count=Count('id'))
#             .order_by('month__month')
#         )
#
#         data = {
#             'labels': [entry['month__month'] for entry in order_counts_by_season],
#             'series': [[entry['order_count'] for entry in order_counts_by_season]],
#         }
#
#         obj.chart_data = data
#         obj.save()
#
#         return Chart(
#             datasource=DataPool(series=[{'options': {'source': obj.chart_data}, 'terms': ['labels', 'series']}]),
#             series_options=[{'options': {'type': 'line', 'stacking': False}, 'terms': {'labels': ['series']}}],
#             chart_options={'title': {'text': 'Order Count by Season'}}
#         )
#
#     order_count_by_season_chart.short_description = 'Order Count by Season (Chart)'
#
# admin.site.register(Order, OrderAdmin)

admin.site.register(Like)
admin.site.register(OrderItem)
admin.site.register(ServingTime)
admin.site.register(Receipt)
