from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0003_favorite_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='file_blob',
            field=models.BinaryField(blank=True, editable=False, null=True, verbose_name='Nội dung tệp (DB)'),
        ),
        migrations.AddField(
            model_name='resource',
            name='file_content_type',
            field=models.CharField(blank=True, default='', max_length=120, verbose_name='MIME type của tệp'),
        ),
        migrations.AddField(
            model_name='resource',
            name='file_name',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Tên tệp gốc'),
        ),
        migrations.AddField(
            model_name='resource',
            name='file_size',
            field=models.PositiveBigIntegerField(default=0, verbose_name='Kích thước tệp (bytes)'),
        ),
    ]