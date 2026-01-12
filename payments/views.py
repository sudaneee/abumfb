import json
import decimal
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import Merchant, Product, ProductField, Payment, PaymentAttempt
from .services.zainpay import initialize_payment, verify_payment
from decimal import Decimal
from payments.services.fees import calculate_fees
from django.utils import timezone


def payment_page(request):
    merchants = Merchant.objects.filter(
        is_active=True,
        approved_by_bank=True
    ).order_by("name")

    return render(request, "payments/payment_page.html", {
        "merchants": merchants
    })

def products_by_merchant(request, merchant_id):
    products = Product.objects.filter(
        merchant_id=merchant_id,
        is_active=True
    ).values("id", "name", "amount_type")

    return JsonResponse(list(products), safe=False)

def fields_by_product(request, product_id):
    fields = ProductField.objects.filter(
        product_id=product_id,
        is_active=True
    ).order_by("display_order")

    data = []
    for f in fields:
        data.append({
            "label": f.label,
            "key": f.key,
            "type": f.field_type,
            "required": f.required,
            "options": f.options or []
        })

    return JsonResponse(data, safe=False)

@require_POST
def submit_payment(request):
    merchant_id = request.POST.get("merchant")
    product_id = request.POST.get("product")
    payment_method = request.POST.get("payment_method")

    if not payment_method:
        return HttpResponseBadRequest("Payment method required")

    merchant = get_object_or_404(Merchant, id=merchant_id, is_active=True)
    product = get_object_or_404(Product, id=product_id, is_active=True)

    # Base amount
    if product.amount_type == "FIXED":
        base_amount = Decimal(product.amount)
    else:
        base_amount = Decimal(request.POST.get("amount"))

    # Calculate fees
    fee = calculate_fees(base_amount, payment_method)
    total_amount = base_amount + fee

    # Metadata
    metadata = {}
    for field in product.fields.filter(is_active=True):
        value = request.POST.get(field.key)
        if field.required and not value:
            return HttpResponseBadRequest(f"{field.label} is required")
        metadata[field.key] = value

    payment = Payment.objects.create(
        merchant=merchant,
        product=product,
        amount=base_amount,
        fee_amount=fee,
        total_amount=total_amount,
        payment_method=payment_method,
        payer_name=request.POST.get("payer_name", ""),
        payer_email=request.POST.get("payer_email", ""),
        payer_phone=request.POST.get("payer_phone", ""),
        metadata=metadata,
        status="PENDING",
        channel="zainpay",
    )

    redirect_url = initialize_payment(
        payment=payment,
        amount_override=payment.total_amount
    )

    return redirect(redirect_url)




def payment_receipt(request, reference):
    payment = get_object_or_404(
        Payment,
        reference=reference,
        status__in=["SUCCESS", "SUCCESS_WITH_ADJUSTMENT", "FLAGGED"]
    )

    return render(request, "payments/receipt.html", {
        "payment": payment,
        "generated_at": timezone.now()
    })

@csrf_exempt
def zainpay_callback(request):
    """
    Handles Zainpay redirect after payment attempt.
    Uses redirect status directly:
    - success  -> SUCCESS
    - cancel   -> CANCELLED
    - others   -> FAILED
    """

    txn_ref = request.GET.get("txnRef")
    status = request.GET.get("status")

    if not txn_ref:
        return HttpResponse("Invalid callback")

    payment = get_object_or_404(Payment, reference=txn_ref)

    # Log attempt (raw callback data)
    PaymentAttempt.objects.create(
        payment=payment,
        gateway_reference=txn_ref,
        response_payload=dict(request.GET),
        success=(status == "success"),
    )

    # ✅ SUCCESSFUL PAYMENT
    if status == "success":
        payment.status = "SUCCESS"
        payment.channel = request.GET.get("channel", "")
        payment.save()
        return redirect(
            "payments:payment_receipt",
            reference=payment.reference
        )

    # ⚠️ USER CANCELLED
    if status == "cancel":
        payment.status = "CANCELLED"
        payment.save()
        return redirect(
            "payments:payment_cancelled",
            reference=payment.reference
        )

    # ❌ ALL OTHER CASES = FAILED
    payment.status = "FAILED"
    payment.save()
    return redirect(
        "payments:payment_failed",
        reference=payment.reference
    )



def payment_cancelled(request, reference):
    payment = get_object_or_404(Payment, reference=reference)
    return render(request, "payments/payment_cancelled.html", {
        "payment": payment
    })


def payment_failed(request, reference):
    payment = get_object_or_404(Payment, reference=reference)
    return render(request, "payments/payment_failed.html", {
        "payment": payment
    })
