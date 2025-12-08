# Generated migration to set initial quota for existing users

from django.db import migrations


def set_initial_quota(apps, schema_editor):
    """为所有现有用户设置3次初始额度"""
    User = apps.get_model('auth', 'User')
    UserQuota = apps.get_model('api', 'UserQuota')

    # 获取所有用户
    all_users = User.objects.all()
    created_count = 0

    for user in all_users:
        # 为没有UserQuota记录的用户创建，并设置3次额度
        quota, created = UserQuota.objects.get_or_create(
            user=user,
            defaults={'available_quota': 3, 'total_purchased': 0}
        )
        if created:
            created_count += 1

    print(f'✅ 成功为 {created_count} 个现有用户创建初始额度（3次）')


def reverse_set_initial_quota(apps, schema_editor):
    """回滚操作：不做任何处理"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_membershipplan_features_delete_planfeature'),
    ]

    operations = [
        migrations.RunPython(set_initial_quota, reverse_set_initial_quota),
    ]
