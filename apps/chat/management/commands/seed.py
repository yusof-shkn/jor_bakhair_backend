from django.core.management.base import BaseCommand
from django.db import transaction
from apps.authentication.models import CustomUser
from apps.chat.models import Interest


class Command(BaseCommand):
    help = "Seed the database with global data."
    data = ["bahir", "mansour", "bozorg", "yusof", "danish", "nazir"]

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Starting database seeding..."))

        # Clear existing data (optional)
        CustomUser.objects.all().delete()
        Interest.objects.all().delete()

        # Seed users
        users = []
        for name in self.data:
            user = CustomUser.objects.create_user(
                email=f"{name}@example.com",
                password="Bozorg123",
                first_name=name.capitalize(),
                last_name="king",
            )
            users.append(user)

        self.stdout.write(
            self.style.SUCCESS(
                f"Created Users: {', '.join([user.email for user in users])}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS("Interest connections created successfully!")
        )
