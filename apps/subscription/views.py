from datetime import datetime

import paypalrestsdk
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.state import token_backend
from rest_framework_simplejwt.tokens import UntypedToken

from apps.subscription.models import SubscriptionPlan, Subscription
from apps.user.models import User


# Create your views here.
class CreatePaymentView(APIView):
    def post(self, request, plan_id):
        plan = SubscriptionPlan.objects.get(id=plan_id)
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
            # Strip the 'b' prefix and quotes from the token if present
            if token.startswith("b'") and token.endswith("'"):
                token = token[2:-1]

            # Decode the token
            UntypedToken(token)
            # Retrieve the token's data
            data = token_backend.decode(token, verify=True)
            # Get the user based on the user_id
            user_id = data.get('user_id')
            user = User.objects.get(id=user_id)
            return user
        except (InvalidToken, TokenError, User.DoesNotExist) as e:
            return None

class CancelPaymentView(APIView):
    def get(self, request):
        return Response({'status': 'Payment cancelled'}, status=status.HTTP_200_OK)
