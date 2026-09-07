# 손으로 작성함. 적용 전 임시 컨테이너에서 makemigrations --check 로 확인한다.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_cloudinv', '0002_cloudresource_native_uniq'),
    ]

    operations = [
        migrations.AddField(
            model_name='cloudresource',
            name='last_seen',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
