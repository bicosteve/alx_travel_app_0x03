from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import status
from rest_framework import views
from rest_framework.decorators import action
from rest_framework.response import Response
import requests

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer, PaymentSerializer


# Create your views here.
class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """This is viewset for managing payments"""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_query(self):
        if getattr(self, "swagger_fake_view", False):
            return Payment.objects.none()

        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(booking_user=user)

    @swagger_auto_schema(
        operation_description="Verify payment status with Chapa",
        responses={
            200: openapi.Response(
                description="Payment verified", schema=PaymentSerializer()
            )
        },
    )
    @action(detail=True, methods=["GET"])
    def verify(self, request, pk=None):
        """Verify the status of payment with chapaa"""
        payment = self.get_object()

        try:
            # Set header with chapa secret key
            headers = {
                "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
                "Content-Type": "application/json",
            }

            # Make Verification Request to Chapa
            res = requests.get(
                f"{settings.CHAPA_API_URL}/v1/transaction/verify/{payment.payment_id}",
                headers=headers,
            )

            res_data = res.json()

            if res.status_code == 200 and res_data.get("status") == "sucess":
                # 1. Update payment status
                payment.status = Payment.PaymentStatus.COMPLETED
                payment.responses = res_data
                payment.save()

                # 2. Send Confirmation Mail --> coming soon

                # 3. Update booking status
                booking = payment.booking
                booking.status = Booking.status.Confirmed
                booking.save()
            return Response(PaymentSerializer(payment).data, status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"err": str(e)}, status.HTTP_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["POST"])
    def initialize(self, request, pk=None):
        """Initiate Payment for a booking"""
        payment = self.get_object()
        booking = payment.booking
        user = booking.user

        payment.email = user.email
        payment.first_name = "Guest"
        payment.last_name = "User"
        payment.payment_title = "Reservation Payment"
        payment.description = f"Booking from {booking.start_date} to {booking.end_date}"

        payment.save()

        try:
            headers = {
                "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
                "Content-Type": "application/json",
            }

            # Prepare payload for Chapa API
            payload = {
                "amount": str(payment.amount),
                "currency": payment.currency,
                "email": payment.booking.user,
                "phone_number": payment.booking.user,
            }

            response = requests.post(
                f"{settings.CHAPA_API_URL}/v1/transaction/initialize",
                json=payload,
                headers=headers,
            )

            response_data = response.json()

            if response.status_code != status.HTTP_200_OK:
                payment.status = Payment.PaymentStatus.FAILED
                payment.save()
                raise Exception(
                    f"CHAPA ERROR: {response_data.get('msg',str(response_data))}"
                )

            # Update payment with checkout URL and Response
            payment.checkout_url = response_data["data"]["checkout_url"]
            payment.responses = response_data
            payment.save()

            # Send checkout URL to user's email

            return Response(
                {
                    "checkout_url": payment.checkout_url,
                    "transaction_ref": str(payment.payment_id),
                    "message": "Payment checkout url has been sent to your mail",
                }
            )

        except Exception as e:
            return Response({"err": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Create a new payment for a booking",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=[
                "booking",
                "amount",
                "currency",
                "email",
            ],
            properties={
                "booking": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Booking UUID"
                ),
                "amount": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Amount to be paid (e.g., "1250.00")',
                ),
                "currency": openapi.Schema(
                    type=openapi.TYPE_STRING, description='Currency code (e.g., "KES")'
                ),
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Customer email address"
                ),
                "phone_number": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Customer phone number"
                ),
                "payment_title": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Title of the payment"
                ),
                "description": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Payment description"
                ),
            },
        ),
        responses={
            201: PaymentSerializer(),
            400: "Bad Request - Invalid input data",
            404: "Not Found - Booking not found",
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class PaymentCompleteView(views.APIView):
    """Handle payment completion redirect"""

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get payment details after completion",
        responses={200: PaymentSerializer(), 403: "Forbidden", 404: "Not Found"},
    )
    def get(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id)

        # Verify the payment belongs to the user
        if not request.user.is_staff and payment.booking.user != request.user:
            return Response(
                {"error": "Not authorized to view this payment"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = PaymentSerializer(payment)
        return Response(serializer.data)
