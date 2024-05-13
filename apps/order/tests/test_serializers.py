# import pytest
# from django.utils import timezone
# import datetime
# from rest_framework.exceptions import ValidationError
#
# from happyhours.factories import BeverageFactory, EstablishmentFactory, UserFactory
# from ..serializers import OrderSerializer
# from ..models import Order
#
#
# @pytest.mark.django_db
# class TestOrderSerializer:
#     def test_validate_order_happyhours_fail(self):
#         """ Test happy hours validation failure """
#         establishment = EstablishmentFactory(happyhours_start='00:00:00', happyhours_end='00:01:00')
#         beverage = BeverageFactory(establishment=establishment)
#         user = UserFactory(role='client')
#         data = {
#             'client': user,
#             'beverage': beverage.id,
#             'establishment': establishment,
#             'order_date': timezone.now()
#         }
#         serializer = OrderSerializer(data=data)
#         with pytest.raises(ValidationError) as excinfo:
#             serializer.is_valid(raise_exception=True)
#         assert "Order can only be placed during happy hours." in str(excinfo.value)
#
#     def test_validate_order_per_hour_fail(self):
#         """ Test that more than one order per hour is not allowed """
#         establishment = EstablishmentFactory(happyhours_start='00:00:00', happyhours_end='23:59:00')
#         establishment_second = EstablishmentFactory(happyhours_start='00:00:00', happyhours_end='23:59:00')
#         beverage = BeverageFactory(establishment=establishment)
#         beverage_second = BeverageFactory(establishment=establishment_second)
#         user = UserFactory(role='client')
#         Order.objects.create(client=user, beverage=beverage, establishment=establishment, order_date=timezone.now())
#
#         data = {
#             'client': user,
#             'beverage': beverage_second.id,
#             'establishment': establishment_second,
#             'order_date': timezone.now() + datetime.timedelta(minutes=30)
#         }
#         serializer = OrderSerializer(data=data)
#         with pytest.raises(ValidationError) as excinfo:
#             serializer.is_valid(raise_exception=True)
#         assert "You can only place one order per hour." in str(excinfo.value)
#
#     def test_validate_order_per_day_fail(self):
#         """ Test that more than one order per day per establishment is not allowed """
#         establishment = EstablishmentFactory(happyhours_start='00:00:00', happyhours_end='23:59:00')
#         beverage = BeverageFactory(establishment=establishment)
#         user = UserFactory(role='client')
#         Order.objects.create(client=user, beverage=beverage, establishment=establishment, order_date=timezone.now())
#         data = {
#             'client': user,
#             'beverage': beverage.id,
#             'establishment': establishment,
#             'order_date': timezone.now() + datetime.timedelta(hours=2)
#         }
#         serializer = OrderSerializer(data=data)
#         with pytest.raises(ValidationError) as excinfo:
#             serializer.is_valid(raise_exception=True)
#         assert "You can only place one order per establishment per day." in str(excinfo.value)
#
#
