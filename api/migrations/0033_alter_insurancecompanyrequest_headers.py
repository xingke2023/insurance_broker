# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0032_insurancecompanyrequest_authorization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='insurancecompanyrequest',
            name='headers',
            field=models.TextField(blank=True, default='', help_text='HTTP请求头（JSON格式字符串），例如：{"Content-Type": "application/json", "X-Custom-Header": "value"}', verbose_name='请求头'),
        ),
    ]
