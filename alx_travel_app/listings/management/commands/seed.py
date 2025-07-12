import uuid
from django.core.management.base import BaseCommand
from listings.models import Listing
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database with sample listings."

    def handle(self, *args, **kwargs):
        user, created = User.objects.get_or_create(
            username="test_host", defaults={"email": "test@example.com"}
        )

        sample_listings = [
            {
                "name": "Cozy Apartment in Nairobi",
                "description": "A lovely one-bedroom apartment in the heart of Nairobi.",
                "location": "Nairobi, Kenya",
                "price_per_night": 50.00,
                "host": user,
            },
            {
                "name": "Beachfront Villa in Mombasa",
                "description": "Luxurious villa with stunning ocean views.",
                "location": "Mombasa, Kenya",
                "price_per_night": 150.00,
                "host": user,
            },
            {
                "name": "Cabin Retreat in Naivasha",
                "description": "Quiet and peaceful getaway surrounded by nature.",
                "location": "Naivasha, Kenya",
                "price_per_night": 75.00,
                "host": user,
            },
        ]

        for data in sample_listings:
            Listing.objects.get_or_create(listing_id=uuid.uuid4(), **data)

        self.stdout.write(
            self.style.SUCCESS(f"Successfully seeded {len(sample_listings)} listings!")
        )
