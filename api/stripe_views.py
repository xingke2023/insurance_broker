"""
Stripe支付集成视图
"""
import stripe
import os
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import PaymentOrder, Membership
import uuid

# 从环境变量获取Stripe密钥
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

# 会员计划配置
MEMBERSHIP_PLANS = {
    'solo': {
        'name': 'Solo计划',
        'price': 20,  # 美元
        'duration_months': 1,
    },
    'team': {
        'name': 'Team计划',
        'price': 10,  # 美元每人
        'duration_months': 1,
        'min_users': 5,
    }
}


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    """
    创建Stripe结账会话
    """
    try:
        plan_type = request.data.get('plan_type')  # 'solo' 或 'team'
        team_size = request.data.get('team_size', 1)  # Team计划的人数

        if plan_type not in MEMBERSHIP_PLANS:
            return Response({
                'error': '无效的会员计划类型'
            }, status=status.HTTP_400_BAD_REQUEST)

        plan_config = MEMBERSHIP_PLANS[plan_type]

        # 验证Team计划人数
        if plan_type == 'team' and team_size < plan_config.get('min_users', 5):
            return Response({
                'error': f'Team计划至少需要{plan_config["min_users"]}人'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 计算金额（单位：分）
        unit_price = plan_config['price']
        quantity = team_size if plan_type == 'team' else 1
        total_amount = unit_price * quantity

        # 创建订单
        order_no = f'ORD-{uuid.uuid4().hex[:16].upper()}'
        order = PaymentOrder.objects.create(
            user=request.user,
            order_no=order_no,
            amount=total_amount,
            description=f'{plan_config["name"]} - {quantity}人' if plan_type == 'team' else plan_config['name'],
            plan_type=plan_type,
            payment_method='stripe',
            status='pending'
        )

        # 创建Stripe结账会话
        # 注意：Stripe使用美分作为单位，需要转换
        # 1 USD = 100 cents
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=[
                'card',        # 信用卡/借记卡
                'wechat_pay',  # 微信支付
                'alipay',      # 支付宝（额外赠送）
            ],
            line_items=[{
                'price_data': {
                    'currency': 'usd',  # 使用美元
                    'product_data': {
                        'name': plan_config['name'],
                        'description': f'{quantity}人' if plan_type == 'team' else '个人订阅',
                    },
                    'unit_amount': int(unit_price * 100),  # 转换为美分
                },
                'quantity': quantity,
            }],
            mode='payment',
            success_url='https://hongkong.xingke888.com/membership-plans?success=true',
            cancel_url='https://hongkong.xingke888.com/membership-plans?canceled=true',
            client_reference_id=order.order_no,
            metadata={
                'order_no': order.order_no,
                'user_id': str(request.user.id),
                'plan_type': plan_type,
            },
            # 自动启用适用的支付方式（根据用户设备和地区）
            payment_method_options={
                'wechat_pay': {
                    'client': 'web',  # 支持网页版微信支付
                },
            },
        )

        # 保存session_id到订单
        order.stripe_session_id = checkout_session.id
        order.save()

        return Response({
            'session_id': checkout_session.id,
            'session_url': checkout_session.url,
            'order_no': order.order_no,
        })

    except Exception as e:
        return Response({
            'error': f'创建支付会话失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def stripe_webhook(request):
    """
    处理Stripe Webhook事件
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return Response({'error': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.SignatureVerificationError:
        return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)

    # 处理支付成功事件
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_successful_payment(session)

    return Response({'status': 'success'})


def handle_successful_payment(session):
    """
    处理支付成功后的逻辑
    """
    try:
        order_no = session.get('client_reference_id') or session['metadata'].get('order_no')

        # 查找订单
        order = PaymentOrder.objects.get(order_no=order_no)

        # 更新订单状态
        order.status = 'paid'
        order.paid_at = timezone.now()
        order.stripe_payment_intent_id = session.get('payment_intent')
        order.save()

        # 获取会员计划配置
        plan_config = MEMBERSHIP_PLANS.get(order.plan_type)
        if not plan_config:
            return

        # 创建或更新会员
        user = order.user
        now = timezone.now()
        end_date = now + timedelta(days=30 * plan_config['duration_months'])

        membership, created = Membership.objects.get_or_create(
            user=user,
            defaults={
                'plan_type': order.plan_type,
                'is_active': True,
                'start_date': now,
                'end_date': end_date,
                'stripe_customer_id': session.get('customer', ''),
            }
        )

        if not created:
            # 如果会员已存在，延长会员期限
            if membership.end_date < now:
                # 会员已过期，从现在开始计算
                membership.start_date = now
                membership.end_date = end_date
            else:
                # 会员未过期，在原有基础上延长
                membership.end_date = membership.end_date + timedelta(days=30 * plan_config['duration_months'])

            membership.plan_type = order.plan_type
            membership.is_active = True
            membership.stripe_customer_id = session.get('customer', '')
            membership.save()

        print(f'✅ 会员订阅成功: {user.username} - {order.plan_type} - 到期时间: {membership.end_date}')

    except PaymentOrder.DoesNotExist:
        print(f'❌ 订单不存在: {order_no}')
    except Exception as e:
        print(f'❌ 处理支付成功事件失败: {str(e)}')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_membership_status(request):
    """
    检查用户会员状态
    """
    try:
        membership = Membership.objects.get(user=request.user)
        return Response({
            'has_membership': True,
            'plan_type': membership.plan_type,
            'is_active': membership.is_valid(),
            'end_date': membership.end_date,
            'days_remaining': membership.days_remaining(),
        })
    except Membership.DoesNotExist:
        return Response({
            'has_membership': False,
        })
