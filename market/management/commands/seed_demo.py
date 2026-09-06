from django.core.management.base import BaseCommand

from demo.services import seed_demo


class Command(BaseCommand):
    help = "Seed deterministic Gapline demo users, watchlists, market data, and replay state."

    def handle(self, *args, **options):
        seed_demo()
        self.stdout.write(self.style.SUCCESS("Gapline demo seeded."))
