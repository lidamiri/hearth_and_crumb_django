from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "unit_price", "quantity")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("reference", "customer_name", "email", "pickup_slot", "total", "status", "created_at")
    list_filter = ("status", "pickup_slot")
    search_fields = ("reference", "customer_name", "email", "phone")
    readonly_fields = ("reference", "total", "created_at")
    inlines = [OrderItemInline]
    actions = ("mark_confirmed", "mark_ready", "mark_completed", "mark_cancelled")

    def _set_status(self, request, queryset, status):
        updated = queryset.update(status=status)
        self.message_user(request, f"{updated} orders marked as {status}.")

    @admin.action(description="Mark selected orders as confirmed")
    def mark_confirmed(self, request, queryset):
        self._set_status(request, queryset, Order.Status.CONFIRMED)

    @admin.action(description="Mark selected orders as ready for pickup")
    def mark_ready(self, request, queryset):
        self._set_status(request, queryset, Order.Status.READY)

    @admin.action(description="Mark selected orders as completed")
    def mark_completed(self, request, queryset):
        self._set_status(request, queryset, Order.Status.COMPLETED)

    @admin.action(description="Mark selected orders as cancelled")
    def mark_cancelled(self, request, queryset):
        self._set_status(request, queryset, Order.Status.CANCELLED)
