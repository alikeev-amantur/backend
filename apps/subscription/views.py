from datetime import datetime

import paypalrestsdk
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets, generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.state import token_backend
from rest_framework_simplejwt.tokens import UntypedToken

from apps.subscription.models import SubscriptionPlan, Subscription
from apps.subscription.schema_definitions import deactivate_subscription_responses, free_trial_responses, \
    free_trial_request_body
from apps.subscription.serializers import FreeTrialSerializer, SubscriptionPlanSerializer, SubscriptionSerializer
from apps.user.models import User
from happyhours.permissions import IsAdmin


@extend_schema(tags=["Subscriptions"])
class CreatePaymentView(APIView):
    def post(self, request, plan_id):
        plan = SubscriptionPlan.objects.get(id=plan_id)
        user = request.user
        active_subscriptions = Subscription.objects.filter(user=user, is_active=True, is_trial=False)
        if active_subscriptions.exists():
            active_subscription = active_subscriptions.first()
            if active_subscription.plan.id == plan.id:
                return Response({'error': 'You already have an active subscription for this plan.'},
                                status=status.HTTP_400_BAD_REQUEST)

        access_token = request.auth.token
        base_url = request.build_absolute_uri('/')
        return_url = f"{base_url}api/v1/subscription/execute-payment/?access_token={access_token}"
        cancel_url = f"{base_url}api/v1/subscription/cancel-payment/"
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": plan.name,
                        "sku": str(plan.id),
                        "price": str(plan.price),
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": str(plan.price),
                    "currency": "USD"
                },
                "description": plan.description
            }],
            "redirect_urls": {
                "return_url": return_url,
                "cancel_url": cancel_url
            }
        })

        if payment.create():
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = str(link.href)
                    return Response({'approval_url': approval_url}, status=status.HTTP_200_OK)
        else:
            return Response({'error': payment.error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(tags=["Subscriptions"])
class ExecutePaymentView(APIView):
    def get(self, request):
        payment_id = request.query_params.get('paymentId')
        payer_id = request.query_params.get('PayerID')
        payment = paypalrestsdk.Payment.find(payment_id)
        access_token = request.query_params.get('access_token')

        # Authenticate user using the access token
        user = self.authenticate_token(access_token)
        if not user:
            return Response({'error': 'Invalid access token'}, status=status.HTTP_401_UNAUTHORIZED)

        if payment.execute({"payer_id": payer_id}):
            plan_id = payment.transactions[0].item_list.items[0].sku
            plan = SubscriptionPlan.objects.get(id=plan_id)
            Subscription.objects.create(
                user=user,
                plan=plan,
                start_date=datetime.now()
            )
            return Response({'status': 'Payment executed successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': payment.error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def authenticate_token(self, token):
        try:
            if token.startswith("b'") and token.endswith("'"):
                token = token[2:-1]

            UntypedToken(token)
            data = token_backend.decode(token, verify=True)
            user_id = data.get('user_id')
            user = User.objects.get(id=user_id)
            return user
        except (InvalidToken, TokenError, User.DoesNotExist) as e:
            return None


@extend_schema(tags=["Subscriptions"])
class CancelPaymentView(APIView):
    def get(self, request):
        return Response({'status': 'Payment cancelled'}, status=status.HTTP_200_OK)


@extend_schema(tags=["Subscriptions"], request=free_trial_request_body, responses=free_trial_responses)
class FreeTrialView(APIView):
    def post(self, request):
        serializer = FreeTrialSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            subscription = serializer.save()
            return Response({
                'status': 'Free trial activated',
                'subscription_id': subscription.id,
                'end_date': subscription.end_date
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Subscriptions"])
class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer

    def get_permissions(self):
        permission_classes = {
            "list": [IsAuthenticated],
            "retrieve": [IsAuthenticated],
            "create": [IsAdmin],
            "update": [IsAdmin],
            "partial_update": [IsAdmin],
            "destroy": [IsAdmin],
        }.get(self.action, [IsAuthenticated])
        return [permission() for permission in permission_classes]


@extend_schema(tags=["Subscriptions"])
class UserSubscriptionsView(generics.ListAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        subscriptions = Subscription.objects.filter(user__id=user_id)
        for subscription in subscriptions:
            subscription.deactivate()
        return subscriptions


@extend_schema(tags=["Subscriptions"], request=None, responses=deactivate_subscription_responses)
class DeactivateSubscriptionView(APIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        instance = get_object_or_404(Subscription, pk=pk)

        if instance.user != request.user:
            return Response({'detail': 'Not allowed to deactivate this subscription.'},
                            status=status.HTTP_403_FORBIDDEN)

        if not instance.is_active:
            return Response({'detail': 'Subscription is already deactivated.'}, status=status.HTTP_400_BAD_REQUEST)

        instance.is_active = False
        instance.save()

        return Response({'detail': 'Subscription deactivated successfully.'}, status=status.HTTP_200_OK)


@extend_schema(tags=["Subscriptions"])
class ActiveUserSubscriptionView(generics.RetrieveAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        subscriptions = Subscription.objects.filter(user=user)
        for subscription in subscriptions:
            subscription.deactivate()

        active_subscription = get_object_or_404(Subscription, user=user, is_active=True)
        return active_subscription
