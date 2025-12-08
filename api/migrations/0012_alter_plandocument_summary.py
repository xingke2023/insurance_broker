# Generated manually on 2025-11-15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_add_trial_membership'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plandocument',
            name='summary',
            field=models.TextField(blank=True, default='', verbose_name='计划书概要'),
        ),
    ]
