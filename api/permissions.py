"""
自定义权限类
"""
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from .models import Membership


class IsMemberActive(BasePermission):
    """
    检查用户是否有有效的会员资格
    """
    message = '您的会员已过期，请加入会员计划以继续使用此功能'

    def has_permission(self, request, view):
        # 必须先登录
        if not request.user or not request.user.is_authenticated:
            return False

        # 检查是否有会员记录
        try:
            membership = Membership.objects.get(user=request.user)
            # 检查会员是否有效
            if not membership.is_valid():
                raise PermissionDenied(detail={
                    'error': 'membership_expired',
                    'message': '您的会员已过期，请续费以继续使用',
                    'redirect': '/membership-plans'
                })
            return True
        except Membership.DoesNotExist:
            raise PermissionDenied(detail={
                'error': 'no_membership',
                'message': '您还不是会员，请加入会员计划以使用此功能',
                'redirect': '/membership-plans'
            })


def require_active_membership(view_func):
    """
    装饰器：要求有效的会员资格
    用法：@require_active_membership
    """
    from functools import wraps
    from rest_framework.response import Response
    from rest_framework import status

    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # 检查用户是否登录
        if not request.user or not request.user.is_authenticated:
            return Response({
                'error': 'not_authenticated',
                'message': '请先登录'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # 检查会员状态
        try:
            membership = Membership.objects.get(user=request.user)
            if not membership.is_valid():
                return Response({
                    'error': 'membership_expired',
                    'message': '您的会员已过期，请续费以继续使用此功能',
                    'redirect': '/membership-plans',
                    'end_date': membership.end_date.isoformat()
                }, status=status.HTTP_403_FORBIDDEN)
        except Membership.DoesNotExist:
            return Response({
                'error': 'no_membership',
                'message': '您还不是会员，请加入会员计划以使用此功能',
                'redirect': '/membership-plans'
            }, status=status.HTTP_403_FORBIDDEN)

        # 会员有效，继续执行原视图函数
        return view_func(request, *args, **kwargs)

    return wrapped_view
