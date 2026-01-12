from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("pay/", views.payment_page, name="payment_page"),
    path("pay/submit/", views.submit_payment, name="submit_payment"),

    # AJAX endpoints
    path("ajax/products/<int:merchant_id>/", views.products_by_merchant),
    path("ajax/fields/<int:product_id>/", views.fields_by_product),

    # Callback
    path("callback/", views.zainpay_callback, name="zainpay_callback"),
    path("receipt/<uuid:reference>/", views.payment_receipt, name="payment_receipt"),



    path("cancelled/<uuid:reference>/", views.payment_cancelled, name="payment_cancelled"),
    path("failed/<uuid:reference>/", views.payment_failed, name="payment_failed"),


]
