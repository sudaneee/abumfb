import requests
from django.conf import settings


def initialize_payment(payment, amount_override=None):
    url = f"{settings.ZAINPAY_BASE_URL}/zainbox/card/initialize/payment"

    payload = {
        "amount": str(amount_override or payment.total_amount),
        "txnRef": str(payment.reference),
        "mobileNumber": payment.payer_phone or "08000000000",
        "emailAddress": payment.payer_email or "no-reply@abumfbank.ng",
        "zainboxCode": payment.merchant.zainbox_code,
        "callBackUrl": settings.ZAINPAY_CALLBACK_URL,
        
    }

    headers = {
        "Authorization": f"Bearer {settings.ZAINPAY_PUBLIC_KEY}",
        "Content-Type": "application/json",

    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    result = response.json()
    data = result.get("data")

    if isinstance(data, str):
        return data

    if isinstance(data, dict):
        return data.get("redirectUrl") or data.get("paymentUrl")

    raise ValueError(f"Unexpected Zainpay response: {result}")


def verify_payment(txn_ref):
    """
    Verifies a payment (CARD or TRANSFER).
    This is the CORRECT endpoint for card payments.
    """

    url = f"{settings.ZAINPAY_BASE_URL}/zainbox/transactions/{txn_ref}"

    headers = {
        "Authorization": f"Bearer {settings.ZAINPAY_PUBLIC_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()
