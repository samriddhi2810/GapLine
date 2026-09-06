from django.core.management.base import BaseCommand

from demo.services import reset_demo


class Command(BaseCommand):
    help = "Reset deterministic Gapline demo data."

    def handle(self, *args, **options):
        reset_demo()
        self.stdout.write(self.style.SUCCESS("Gapline demo reset."))
