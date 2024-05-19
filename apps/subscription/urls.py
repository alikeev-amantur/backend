from django.urls import path

from apps.subscription.views import CreatePaymentView, ExecutePaymentView, CancelPaymentView

urlpatterns = [
    path('create-payment/<int:plan_id>/', CreatePaymentView.as_view(), name='create_payment'),
    path('execute-payment/', ExecutePaymentView.as_view(), name='execute_payment'),
    path('cancel-payment/', CancelPaymentView.as_view(), name='cancel_payment'),
]
