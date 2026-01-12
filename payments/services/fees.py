from decimal import Decimal, ROUND_HALF_UP

MAX_FEE = Decimal("1900.00")


def calculate_fees(amount, payment_method):
    amount = Decimal(amount)

    if payment_method == "TRANSFER":
        if amount <= 5000:
            fee = Decimal("50.00")
        else:
            fee = Decimal("550.00")

    elif payment_method == "CARD":
        fee = (amount * Decimal("0.012")) + Decimal("300.00")

    else:
        raise ValueError("Invalid payment method")

    # Apply cap
    if fee > MAX_FEE:
        fee = MAX_FEE

    return fee.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
