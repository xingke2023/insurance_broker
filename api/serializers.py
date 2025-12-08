from rest_framework import serializers
from .models import InsurancePolicy
import json

class InsurancePolicySerializer(serializers.ModelSerializer):
    """保险策略序列化器"""

    # 自定义字段，将JSON字符串转换为对象
    table1 = serializers.SerializerMethodField()
    table2 = serializers.SerializerMethodField()

    def get_table1(self, obj):
        """将table1 JSON字符串转换为对象"""
        if obj.table1:
            try:
                return json.loads(obj.table1)
            except (json.JSONDecodeError, TypeError):
                return None
        return None

    def get_table2(self, obj):
        """将table2 JSON字符串转换为对象"""
        if obj.table2:
            try:
                return json.loads(obj.table2)
            except (json.JSONDecodeError, TypeError):
                return None
        return None

    class Meta:
        model = InsurancePolicy
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
