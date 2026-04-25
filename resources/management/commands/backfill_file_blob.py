import mimetypes

from django.conf import settings
from django.core.management.base import BaseCommand

from resources.models import Resource


class Command(BaseCommand):
    help = 'Copy existing attachment files from storage into DB blob fields.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--only-missing',
            action='store_true',
            help='Only backfill records that do not already have file_blob data.',
        )

    def handle(self, *args, **options):
        if not getattr(settings, 'STORE_UPLOADS_IN_DB', False):
            self.stdout.write(self.style.WARNING(
                'STORE_UPLOADS_IN_DB đang là False. Backfill vẫn chạy được nhưng bạn nên bật biến này khi deploy.'
            ))

        queryset = Resource.objects.exclude(file='')
        if options['only_missing']:
            queryset = queryset.filter(file_blob__isnull=True)

        total = queryset.count()
        success_count = 0
        skipped_count = 0

        for resource in queryset.iterator():
            if not resource.file:
                skipped_count += 1
                continue

            try:
                with resource.file.open('rb') as f:
                    data = f.read()

                resource.file_blob = data
                if not resource.file_name:
                    resource.file_name = resource.file.name.rsplit('/', 1)[-1]
                if not resource.file_content_type:
                    resource.file_content_type = (
                        mimetypes.guess_type(resource.file_name or resource.file.name)[0]
                        or 'application/octet-stream'
                    )
                resource.file_size = len(data)
                resource.save(update_fields=['file_blob', 'file_name', 'file_content_type', 'file_size'])
                success_count += 1
            except Exception as exc:
                skipped_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Bỏ qua resource {resource.pk} ({resource.title}): {exc}')
                )

        self.stdout.write(self.style.SUCCESS(
            f'Backfill hoàn tất. Tổng: {total}, Thành công: {success_count}, Bỏ qua: {skipped_count}'
        ))