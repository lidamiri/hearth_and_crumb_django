from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order", "product_count")
    list_editable = ("sort_order",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}

    @admin.display(description="Products")
    def product_count(self, obj):
        return obj.products.count()


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "is_available", "is_featured")
    list_editable = ("price", "stock", "is_available", "is_featured")
    list_filter = ("category", "is_available", "is_featured")
    search_fields = ("name", "summary", "description", "allergens")
    readonly_fields = ("slug", "created_at", "updated_at")
    actions = ("mark_sold_out", "mark_available")

    @admin.action(description="Mark selected products as sold out")
    def mark_sold_out(self, request, queryset):
        updated = queryset.update(stock=0)
        self.message_user(request, f"{updated} products set to zero stock.")

    @admin.action(description="Make selected products available")
    def mark_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f"{updated} products made available.")
