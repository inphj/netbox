# 손으로 작성함. NetBox 는 개발 모드가 아니면 makemigrations 를 막는다.
# 형식은 netbox_oci/migrations/0001_initial.py (실제 생성물) 를 원본 대조해 맞췄다.
# 확인 필요: 이미지 빌드 후 `migrate` 로 실제 적용을 확인해야 한다.

import django.core.validators
import django.db.models.deletion
import netbox.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('extras', '0140_imageattachment_image_size'),
        ('tenancy', '0024_default_ordering_indexes'),
    ]

    operations = [
        migrations.CreateModel(
            name='CloudPlatform',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('label', models.CharField(max_length=100)),
                ('kind', models.CharField(default='public', max_length=10)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': '클라우드 플랫폼',
                'verbose_name_plural': '클라우드 플랫폼',
                'ordering': ('name',),
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
        migrations.CreateModel(
            name='CloudService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('code', models.CharField(max_length=50)),
                ('label', models.CharField(max_length=100)),
                ('category', models.CharField(default='other', max_length=20)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('platform', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='services', to='netbox_cloudinv.cloudplatform')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': '클라우드 서비스',
                'verbose_name_plural': '클라우드 서비스',
                'ordering': ('platform', 'category', 'code'),
                'unique_together': {('platform', 'code')},
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
        migrations.CreateModel(
            name='CloudResource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('name', models.CharField(max_length=200)),
                ('native_id', models.CharField(blank=True, max_length=500)),
                ('account', models.CharField(blank=True, max_length=100)),
                ('region', models.CharField(blank=True, max_length=50)),
                ('environment', models.CharField(blank=True, max_length=50)),
                ('status', models.CharField(default='active', max_length=20)),
                ('monthly_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('description', models.CharField(blank=True, max_length=200)),
                ('attrs', models.JSONField(blank=True, default=dict)),
                ('platform', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='resources', to='netbox_cloudinv.cloudplatform')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='resources', to='netbox_cloudinv.cloudservice')),
                ('tenant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='cloud_resources', to='tenancy.tenant')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': '클라우드 자원',
                'verbose_name_plural': '클라우드 자원',
                'ordering': ('platform', 'service', 'name'),
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
        migrations.AddIndex(
            model_name='cloudresource',
            index=models.Index(fields=['native_id'], name='cloudinv_native_id_idx'),
        ),
    ]
