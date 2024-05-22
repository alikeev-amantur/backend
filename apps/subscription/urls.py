from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.subscription.views import CreatePaymentView, ExecutePaymentView, CancelPaymentView, FreeTrialView, \
    SubscriptionPlanViewSet, UserSubscriptionsView, DeactivateSubscriptionView

router = DefaultRouter()
router.register(r'subscription-plans', SubscriptionPlanViewSet, basename='subscriptionplan')

urlpatterns = [
    path('create-payment/<int:plan_id>/', CreatePaymentView.as_view(), name='create_payment'),
    path('execute-payment/', ExecutePaymentView.as_view(), name='execute_payment'),
    path('cancel-payment/', CancelPaymentView.as_view(), name='cancel_payment'),
    path('free-trial/', FreeTrialView.as_view(), name='free-trial'),
    path('', include(router.urls)),
    path('<int:user_id>/subscriptions/', UserSubscriptionsView.as_view(), name='user-subscriptions'),
    path('deactivate/<int:pk>/', DeactivateSubscriptionView.as_view(), name='deactivate-subscription')
]
