# 손으로 작성함. NetBox 는 개발 모드가 아니면 makemigrations 를 막는다.
# 적용 전 임시 컨테이너에서 makemigrations --check 로 모델과 일치를 확인한다.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_cloudinv', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='cloudresource',
            constraint=models.UniqueConstraint(
                condition=models.Q(('native_id', ''), _negated=True),
                fields=('platform', 'account', 'native_id'),
                name='cloudinv_resource_native_uniq'),
        ),
    ]
