from django.core.management.base import BaseCommand
from companies.models import Company
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = "Delete Companies who's requested to delete 30 days ago"
    def handle(self ,*args ,**options):
        thirty_days_ago = timezone.now() - timedelta(days = 30)
        companies_to_delete = Company.objects.filter(
            is_active = False , 
            deleted_at__lte = thirty_days_ago)
        count = companies_to_delete.count()
        if count > 0 :
            companies_to_delete.delete()
            self.stdout.write(self.style.SUCCESS(f"Successfully deleted {count} companies."))
        else:
            self.stdout.write("No companies to delete.")
            

        