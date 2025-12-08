# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0033_alter_insurancecompanyrequest_headers'),
    ]

    operations = [
        migrations.AddField(
            model_name='insurancecompany',
            name='headers',
            field=models.TextField(blank=True, default='', help_text='公司级别的通用HTTP Headers（JSON格式或键值对格式），会应用到该公司的所有API请求', verbose_name='公司级别Headers'),
        ),
    ]
