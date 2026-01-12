from django.contrib import admin
from .models import (
    Merchant,
    Product,
    ProductField,
    Payment,
    PaymentAttempt,
    Settlement
)


# =========================
# INLINE CONFIGS
# =========================

class ProductFieldInline(admin.TabularInline):
    model = ProductField
    extra = 0
    ordering = ("display_order",)
    fields = (
        "label",
        "key",
        "field_type",
        "required",
        "options",
        "display_order",
        "is_active",
    )


class ProductInline(admin.TabularInline):
    model = Product
    extra = 0
    fields = (
        "name",
        "amount_type",
        "amount",
        "is_active",
    )


# =========================
# MERCHANT ADMIN
# =========================

@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "merchant_type",
        "zainbox_code",
        "approved_by_bank",
        "is_active",
        "created_at",
    )

    list_filter = (
        "merchant_type",
        "approved_by_bank",
        "is_active",
    )

    search_fields = (
        "name",
        "zainbox_code",
    )

    readonly_fields = ("created_at",)

    inlines = [ProductInline]

    fieldsets = (
        ("Merchant Information", {
            "fields": (
                "name",
                "merchant_type",
            )
        }),
        ("Zainpay Configuration", {
            "fields": (
                "zainbox_code",
            )
        }),
        ("Settlement Details (ABUMFBANK)", {
            "fields": (
                "settlement_account_number",
                "settlement_bank_code",
            )
        }),
        ("Approval & Status", {
            "fields": (
                "approved_by_bank",
                "is_active",
            )
        }),
        ("Timestamps", {
            "fields": ("created_at",)
        }),
    )


# =========================
# PRODUCT ADMIN
# =========================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "merchant",
        "amount_type",
        "amount",
        "is_active",
        "created_at",
    )

    list_filter = (
        "merchant",
        "amount_type",
        "is_active",
    )

    search_fields = (
        "name",
        "merchant__name",
    )

    readonly_fields = ("created_at",)

    inlines = [ProductFieldInline]

    fieldsets = (
        ("Product Information", {
            "fields": (
                "merchant",
                "name",
                "description",
            )
        }),
        ("Pricing", {
            "fields": (
                "amount_type",
                "amount",
            )
        }),
        ("Status", {
            "fields": (
                "is_active",
            )
        }),
        ("Timestamps", {
            "fields": ("created_at",)
        }),
    )


# =========================
# PRODUCT FIELD ADMIN
# =========================

@admin.register(ProductField)
class ProductFieldAdmin(admin.ModelAdmin):
    list_display = (
        "label",
        "product",
        "field_type",
        "required",
        "display_order",
        "is_active",
    )

    list_filter = (
        "field_type",
        "required",
        "is_active",
        "product__merchant",
    )

    search_fields = (
        "label",
        "key",
        "product__name",
    )

    ordering = ("product", "display_order")


# =========================
# PAYMENT ADMIN
# =========================

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "merchant",
        "product",
        "amount",
        "status",
        "channel",
        "created_at",
    )

    list_filter = (
        "status",
        "channel",
        "merchant",
        "created_at",
    )

    search_fields = (
        "reference",
        "payer_name",
        "payer_email",
        "payer_phone",
    )

    readonly_fields = (
        "reference",
        "merchant",
        "product",
        "amount",
        "payer_name",
        "payer_email",
        "payer_phone",
        "metadata",
        "status",
        "channel",
        "created_at",
    )

    fieldsets = (
        ("Payment Reference", {
            "fields": (
                "reference",
                "status",
                "channel",
            )
        }),
        ("Merchant & Product", {
            "fields": (
                "merchant",
                "product",
                "amount",
            )
        }),
        ("Payer Information", {
            "fields": (
                "payer_name",
                "payer_email",
                "payer_phone",
            )
        }),
        ("Submitted Metadata", {
            "fields": (
                "metadata",
            )
        }),
        ("Timestamps", {
            "fields": (
                "created_at",
            )
        }),
    )

    def has_add_permission(self, request):
        # Payments must NEVER be created manually
        return False

    def has_delete_permission(self, request, obj=None):
        # Payments must NEVER be deleted
        return False


# =========================
# PAYMENT ATTEMPT ADMIN
# =========================

@admin.register(PaymentAttempt)
class PaymentAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "payment",
        "gateway_reference",
        "success",
        "created_at",
    )

    list_filter = (
        "success",
        "created_at",
    )

    search_fields = (
        "gateway_reference",
        "payment__reference",
    )

    readonly_fields = (
        "payment",
        "gateway_reference",
        "response_payload",
        "success",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# =========================
# SETTLEMENT ADMIN
# =========================

@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = (
        "merchant",
        "period_start",
        "period_end",
        "total_collected",
        "merchant_amount",
        "bank_commission",
        "settled",
        "settled_at",
    )

    list_filter = (
        "merchant",
        "settled",
    )

    readonly_fields = (
        "merchant",
        "period_start",
        "period_end",
        "total_collected",
        "merchant_amount",
        "bank_commission",
        "settled_at",
        "created_at",
    )

    def has_add_permission(self, request):
        # Settlements should be system-generated
        return False
