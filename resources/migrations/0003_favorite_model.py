from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def create_favorite_table_if_missing(apps, schema_editor):
    from resources.models import Favorite

    existing_tables = schema_editor.connection.introspection.table_names()
    if Favorite._meta.db_table not in existing_tables:
        schema_editor.create_model(Favorite)


def drop_favorite_table_if_exists(apps, schema_editor):
    from resources.models import Favorite

    existing_tables = schema_editor.connection.introspection.table_names()
    if Favorite._meta.db_table in existing_tables:
        schema_editor.delete_model(Favorite)


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0002_comment_idx_comment_resource_created_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    create_favorite_table_if_missing,
                    reverse_code=drop_favorite_table_if_exists,
                )
            ],
            state_operations=[
                migrations.CreateModel(
                    name='Favorite',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')),
                        ('resource', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='resources.resource', verbose_name='Tài liệu')),
                        ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_resources', to=settings.AUTH_USER_MODEL, verbose_name='Người dùng')),
                    ],
                    options={
                        'verbose_name': 'Tài liệu yêu thích',
                        'verbose_name_plural': 'Tài liệu yêu thích',
                        'db_table': 'resources_favorite',
                        'ordering': ['-created_at'],
                    },
                ),
                migrations.AddConstraint(
                    model_name='favorite',
                    constraint=models.UniqueConstraint(fields=('user', 'resource'), name='unique_user_resource_favorite'),
                ),
                migrations.AddIndex(
                    model_name='favorite',
                    index=models.Index(fields=['user', '-created_at'], name='idx_favorite_user_created'),
                ),
                migrations.AddIndex(
                    model_name='favorite',
                    index=models.Index(fields=['resource'], name='idx_favorite_resource'),
                ),
            ],
        ),
    ]
