from django.contrib import admin

from apps.beverage.models import Category, Beverage


class BeverageAdmin(admin.ModelAdmin):
    list_display = (
        "__str__", "id", "price", "availability_status", "establishment"
    )


admin.site.register(Category)
admin.site.register(Beverage, BeverageAdmin)
