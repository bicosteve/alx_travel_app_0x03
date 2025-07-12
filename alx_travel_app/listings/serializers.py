from rest_framework import serializers
from .models import Listing, Booking, Payment


class ListingSerializer(serializers.ModelSerializer):
    listing_id = serializers.UUIDField(read_only=True)
    host = serializers.UUIDField(read_only=True)
    name = serializers.CharField()
    description = serializers.CharField()
    location = serializers.CharField()
    price_per_night = serializers.DecimalField(max_digits=10, decimal_places=2)
    created_at = serializers.DateTimeField(auto_now_add=True)
    updated_at = serializers.DateTimeField(auto_now=True)

    class Meta:
        model = Listing
        fields = "__all__"

        read_only_fields = ["listing_id", "host"]


class BookingSerializer(serializers.ModelSerializer):
    booking_id = serializers.UUIDField(primary_key=True)
    listing = serializers.UUIDField(foreign_key=True)
    user = serializers.UUIDField(foreign_key=True)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField(
        max_length=10,
        choices=[
            ("pending", "Pending"),
            ("confirmed", "Confirmed"),
            ("canceled", "Canceled"),
        ],
    )
    created_at = serializers.DateTimeField(auto_now_add=True)

    class Meta:
        model = Booking
        fields = "__all__"

        read_only_fields = ["booking_id", "listing", "user"]


class PaymentSerializer(serializers.ModelSerializer):
    responses = serializers.CharField(required=False)

    class Meta:
        model = Payment
        fields = [
            "payment_id",
            "booking",
            "booking_reference",
            "amount",
            "currenty",
            "status",
            "payment_method",
            "transaction_id",
            "created_at",
            "updated_at",
            "responses",
        ]
        read_only_fields = ["payment_id", "created_at", "updated_at"]
