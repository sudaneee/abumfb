import uuid
from django.db import models
from decimal import Decimal


# =========================
# MERCHANT
# =========================
class Merchant(models.Model):
    MERCHANT_TYPES = (
        ("PRIMARY", "Primary School"),
        ("SECONDARY", "Secondary School"),
        ("COLLEGE", "College"),
        ("UNIVERSITY", "University"),
        ("OTHER", "Other"),
    )

    name = models.CharField(max_length=255)
    merchant_type = models.CharField(max_length=20, choices=MERCHANT_TYPES)

    # Zainpay
    zainbox_code = models.CharField(max_length=50, unique=True)

    # Settlement (ABUMFBANK)
    settlement_account_number = models.CharField(max_length=20)
    settlement_bank_code = models.CharField(max_length=10)

    approved_by_bank = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# =========================
# PRODUCT
# =========================
class Product(models.Model):
    AMOUNT_TYPES = (
        ("FIXED", "Fixed Amount"),
        ("VARIABLE", "Variable Amount"),
    )

    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE,
        related_name="products"
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    amount_type = models.CharField(
        max_length=10,
        choices=AMOUNT_TYPES,
        default="FIXED"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Required if amount_type is FIXED"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.merchant.name})"


# =========================
# PRODUCT FIELD (DYNAMIC FORM)
# =========================
class ProductField(models.Model):
    FIELD_TYPES = (
        ("TEXT", "Text"),
        ("NUMBER", "Number"),
        ("EMAIL", "Email"),
        ("SELECT", "Select"),
        ("DATE", "Date"),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="fields"
    )

    label = models.CharField(max_length=255)
    key = models.SlugField(
        max_length=50,
        help_text="Used as metadata key e.g matric_number"
    )

    field_type = models.CharField(
        max_length=10,
        choices=FIELD_TYPES
    )

    required = models.BooleanField(default=True)

    options = models.JSONField(
        null=True,
        blank=True,
        help_text="Only for SELECT fields"
    )

    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order"]
        unique_together = ("product", "key")

    def __str__(self):
        return f"{self.label} ({self.product.name})"


# =========================
# PAYMENT
# =========================






class Payment(models.Model):
    PAYMENT_STATUS = (
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("SUCCESS_WITH_ADJUSTMENT", "Success With Adjustment"),
        ("FLAGGED", "Flagged"),
        ("FAILED", "Failed"),
    )

    PAYMENT_METHODS = (
        ("CARD", "Card"),
        ("TRANSFER", "Transfer"),
    )

    reference = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    merchant = models.ForeignKey(
        "Merchant",
        on_delete=models.PROTECT
    )

    product = models.ForeignKey(
        "Product",
        on_delete=models.PROTECT
    )

    # -----------------------
    # AMOUNTS & CHARGES
    # -----------------------
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Base amount (product amount)"
    )

    fee_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Bank / platform charge"
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Total amount paid by customer (amount + fee)",
        blank=True,
        null=True,
    )

    adjustment_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Difference when payment method or amount mismatch occurs"
    )

    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHODS,
        help_text="User-selected payment method",
        blank=True,
    )

    # -----------------------
    # PAYER DETAILS
    # -----------------------
    payer_name = models.CharField(max_length=255, blank=True)
    payer_email = models.EmailField(blank=True)
    payer_phone = models.CharField(max_length=20, blank=True)

    # -----------------------
    # DYNAMIC METADATA
    # -----------------------
    metadata = models.JSONField(
        help_text="Dynamic data collected per product"
    )

    # -----------------------
    # PAYMENT RESULT
    # -----------------------
    status = models.CharField(
        max_length=30,
        choices=PAYMENT_STATUS,
        default="PENDING"
    )

    channel = models.CharField(
        max_length=20,
        blank=True,
        help_text="Actual payment channel used (card, bank_transfer, ussd)"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.reference)



# =========================
# PAYMENT ATTEMPT (RETRIES, GATEWAY LOGS)
# =========================
class PaymentAttempt(models.Model):
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="attempts"
    )

    gateway_reference = models.CharField(max_length=100)
    response_payload = models.JSONField()

    success = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.gateway_reference} - {self.payment.reference}"


# =========================
# SETTLEMENT (BANK SIDE)
# =========================
class Settlement(models.Model):
    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.PROTECT
    )

    period_start = models.DateField()
    period_end = models.DateField()

    total_collected = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    bank_commission = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    merchant_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    settled = models.BooleanField(default=False)
    settled_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Settlement {self.merchant.name} ({self.period_start} - {self.period_end})"
