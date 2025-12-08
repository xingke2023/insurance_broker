from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import InsurancePolicy
from .serializers import InsurancePolicySerializer

class InsurancePolicyViewSet(viewsets.ModelViewSet):
    """
    保险策略ViewSet
    提供CRUD操作
    """
    queryset = InsurancePolicy.objects.all()
    serializer_class = InsurancePolicySerializer

    @action(detail=False, methods=['get'])
    def active_policies(self, request):
        """获取所有有效的保单"""
        active = self.queryset.filter(status='active')
        serializer = self.get_serializer(active, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel_policy(self, request, pk=None):
        """取消保单"""
        policy = self.get_object()
        policy.status = 'cancelled'
        policy.save()
        serializer = self.get_serializer(policy)
        return Response(serializer.data)
