from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from wechatpayv3 import WeChatPay, WeChatPayType
import time
import logging
import json
from decimal import Decimal
from .models import PaymentOrder, WeChatUser, Membership, UserQuota, MembershipPlan

logger = logging.getLogger(__name__)


def generate_order_no():
    """生成订单号"""
    import uuid
    return f"ORDER_{int(time.time())}_{uuid.uuid4().hex[:8].upper()}"


def activate_membership(user, plan_type):
    """开通或续费会员"""
    from datetime import timedelta

    # 计算会员时长
    if plan_type == 'monthly':
        duration_days = 30
    elif plan_type == 'yearly':
        duration_days = 365
    else:
        logger.error(f'未知的套餐类型: {plan_type}')
        return

    now = timezone.now()

    try:
        # 获取现有会员
        membership = Membership.objects.get(user=user)

        # 如果会员还有效，从到期时间续费，否则从现在开始
        if membership.is_valid():
            start_date = membership.end_date
        else:
            start_date = now

        membership.plan_type = plan_type
        membership.is_active = True
        membership.start_date = start_date if start_date > now else now
        membership.end_date = membership.start_date + timedelta(days=duration_days)
        membership.save()

        logger.info(f'会员续费成功: {user.username}, 到期时间: {membership.end_date}')

    except Membership.DoesNotExist:
        # 创建新会员
        end_date = now + timedelta(days=duration_days)
        membership = Membership.objects.create(
            user=user,
            plan_type=plan_type,
            is_active=True,
            start_date=now,
            end_date=end_date
        )

        logger.info(f'会员开通成功: {user.username}, 到期时间: {membership.end_date}')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_order_v3(request):
    """创建支付订单 - 微信支付V3版本"""
    amount = request.data.get('amount')
    description = request.data.get('description', '商品购买')
    plan_type = request.data.get('plan_type', '')  # 获取套餐类型

    if not amount:
        return Response(
            {'code': 400, 'message': '缺少支付金额'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        amount = Decimal(amount)
        if amount <= 0:
            return Response(
                {'code': 400, 'message': '支付金额必须大于0'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except:
        return Response(
            {'code': 400, 'message': '支付金额格式错误'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 获取微信用户的openid
    try:
        wechat_user = WeChatUser.objects.get(user=request.user)
        openid = wechat_user.openid
    except WeChatUser.DoesNotExist:
        return Response(
            {'code': 400, 'message': '未找到微信用户信息'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 创建订单
    order_no = generate_order_no()
    order = PaymentOrder.objects.create(
        user=request.user,
        order_no=order_no,
        amount=amount,
        description=description,
        plan_type=plan_type,  # 保存套餐类型
        status='pending'
    )

    # 获取配置
    mch_id = getattr(settings, 'WECHAT_MCH_ID', '')
    app_id = getattr(settings, 'WECHAT_APP_ID', '')
    apiv3_key = getattr(settings, 'WECHAT_APIV3_KEY', '')
    cert_serial_no = getattr(settings, 'WECHAT_CERT_SERIAL_NO', '')
    private_key_path = getattr(settings, 'WECHAT_PRIVATE_KEY_PATH', '')
    notify_url = getattr(settings, 'WECHAT_NOTIFY_URL', 'https://cardbuy.xingke888.com/api/payment/notify')

    if not all([mch_id, app_id, apiv3_key, cert_serial_no, private_key_path]):
        logger.error('微信支付V3配置缺失')
        return Response(
            {'code': 500, 'message': '服务器配置错误'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    try:
        # 读取私钥
        with open(private_key_path, 'r') as f:
            private_key = f.read()

        # 初始化微信支付客户端
        wxpay = WeChatPay(
            wechatpay_type=WeChatPayType.JSAPI,
            mchid=mch_id,
            private_key=private_key,
            cert_serial_no=cert_serial_no,
            apiv3_key=apiv3_key,
            appid=app_id
        )

        # 构造支付参数
        out_trade_no = order_no
        total = int(amount * 100)  # 金额转为分

        logger.info(f'创建V3支付订单: order_no={out_trade_no}, amount={total}, openid={openid}')

        # 调用统一下单接口
        code, message = wxpay.pay(
            description=description,
            out_trade_no=out_trade_no,
            amount={'total': total, 'currency': 'CNY'},
            payer={'openid': openid},
            notify_url=notify_url
        )

        if code != 200:
            logger.error(f'微信支付V3下单失败: code={code}, message={message}')
            return Response(
                {'code': 400, 'message': f'下单失败: {message}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # message 包含 prepay_id
        result = json.loads(message)
        prepay_id = result.get('prepay_id')

        if not prepay_id:
            logger.error(f'未获取到prepay_id: {result}')
            return Response(
                {'code': 400, 'message': '下单失败：未获取到支付ID'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.prepay_id = prepay_id
        order.save()

        logger.info(f'获取到prepay_id: {prepay_id}')

        # 生成小程序调起支付的参数
        import random
        import string
        timestamp = str(int(time.time()))
        nonce_str = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        package = f'prepay_id={prepay_id}'

        # 构造签名数据
        sign_data = f'{app_id}\n{timestamp}\n{nonce_str}\n{package}\n'

        # 使用商户私钥进行签名
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.backends import default_backend
        import base64

        # 加载私钥
        private_key_obj = serialization.load_pem_private_key(
            private_key.encode('utf-8'),
            password=None,
            backend=default_backend()
        )

        # 签名
        signature = private_key_obj.sign(
            sign_data.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        pay_sign = base64.b64encode(signature).decode('utf-8')

        logger.info(f'生成支付签名: timestamp={timestamp}, nonce_str={nonce_str}, package={package}')

        return Response({
            'code': 200,
            'message': '创建订单成功',
            'data': {
                'order_no': order_no,
                'payment': {
                    'timeStamp': timestamp,
                    'nonceStr': nonce_str,
                    'package': package,
                    'signType': 'RSA',
                    'paySign': pay_sign
                }
            }
        })

    except FileNotFoundError:
        logger.error(f'证书文件不存在: {private_key_path}')
        return Response(
            {'code': 500, 'message': '证书文件配置错误'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        logger.error(f'创建订单异常: {str(e)}', exc_info=True)
        return Response(
            {'code': 500, 'message': f'服务器内部错误: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_jsapi_payment(request):
    """创建JSAPI支付订单 - 用于网页版微信支付"""
    amount = request.data.get('amount')
    description = request.data.get('description', '充值服务')
    plan_type = request.data.get('plan_type', '')  # 获取套餐类型

    if not amount:
        return Response(
            {'code': 400, 'message': '缺少支付金额'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        amount = Decimal(amount)
        if amount <= 0:
            return Response(
                {'code': 400, 'message': '支付金额必须大于0'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except:
        return Response(
            {'code': 400, 'message': '支付金额格式错误'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 获取微信用户的openid
    try:
        wechat_user = WeChatUser.objects.get(user=request.user)
        openid = wechat_user.openid
    except WeChatUser.DoesNotExist:
        return Response(
            {'code': 400, 'message': '请先使用微信小程序登录'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 创建订单
    order_no = generate_order_no()
    order = PaymentOrder.objects.create(
        user=request.user,
        order_no=order_no,
        amount=amount,
        description=description,
        plan_type=plan_type,  # 保存套餐类型
        status='pending'
    )

    # 获取配置
    mch_id = getattr(settings, 'WECHAT_MCH_ID', '')
    app_id = getattr(settings, 'WECHAT_APP_ID', '')
    apiv3_key = getattr(settings, 'WECHAT_APIV3_KEY', '')
    cert_serial_no = getattr(settings, 'WECHAT_CERT_SERIAL_NO', '')
    private_key_path = getattr(settings, 'WECHAT_PRIVATE_KEY_PATH', '')
    notify_url = getattr(settings, 'WECHAT_NOTIFY_URL', 'https://cardbuy.xingke888.com/api/payment/notify')

    if not all([mch_id, app_id, apiv3_key, cert_serial_no, private_key_path]):
        logger.error('微信支付V3配置缺失')
        return Response(
            {'code': 500, 'message': '服务器配置错误'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    try:
        # 读取私钥
        with open(private_key_path, 'r') as f:
            private_key = f.read()

        # 初始化微信支付客户端
        wxpay = WeChatPay(
            wechatpay_type=WeChatPayType.JSAPI,
            mchid=mch_id,
            private_key=private_key,
            cert_serial_no=cert_serial_no,
            apiv3_key=apiv3_key,
            appid=app_id
        )

        # 构造支付参数
        out_trade_no = order_no
        total = int(amount * 100)  # 金额转为分

        logger.info(f'创建JSAPI支付订单: order_no={out_trade_no}, amount={total}, openid={openid}')

        # 调用统一下单接口
        code, message = wxpay.pay(
            description=description,
            out_trade_no=out_trade_no,
            amount={'total': total, 'currency': 'CNY'},
            payer={'openid': openid},
            notify_url=notify_url
        )

        if code != 200:
            logger.error(f'微信支付JSAPI下单失败: code={code}, message={message}')
            return Response(
                {'code': 400, 'message': f'下单失败: {message}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # message 包含 prepay_id
        result = json.loads(message)
        prepay_id = result.get('prepay_id')

        if not prepay_id:
            logger.error(f'未获取到prepay_id: {result}')
            return Response(
                {'code': 400, 'message': '下单失败：未获取到支付ID'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.prepay_id = prepay_id
        order.save()

        logger.info(f'获取到prepay_id: {prepay_id}')

        # 生成JSAPI调起支付的参数
        import random
        import string
        timestamp = str(int(time.time()))
        nonce_str = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        package = f'prepay_id={prepay_id}'

        # 构造签名数据
        sign_data = f'{app_id}\n{timestamp}\n{nonce_str}\n{package}\n'

        # 使用商户私钥进行签名
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.backends import default_backend
        import base64

        # 加载私钥
        private_key_obj = serialization.load_pem_private_key(
            private_key.encode('utf-8'),
            password=None,
            backend=default_backend()
        )

        # 签名
        signature = private_key_obj.sign(
            sign_data.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        pay_sign = base64.b64encode(signature).decode('utf-8')

        logger.info(f'生成JSAPI支付签名: timestamp={timestamp}, nonce_str={nonce_str}')

        return Response({
            'code': 200,
            'message': '创建订单成功',
            'data': {
                'order_no': order_no,
                'appId': app_id,
                'timeStamp': timestamp,
                'nonceStr': nonce_str,
                'package': package,
                'signType': 'RSA',
                'paySign': pay_sign
            }
        })

    except FileNotFoundError:
        logger.error(f'证书文件不存在: {private_key_path}')
        return Response(
            {'code': 500, 'message': '证书文件配置错误'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        logger.error(f'创建JSAPI订单异常: {str(e)}', exc_info=True)
        return Response(
            {'code': 500, 'message': f'服务器内部错误: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([])
def payment_notify_v3(request):
    """微信支付回调通知 - V3版本"""
    try:
        # 获取配置
        app_id = getattr(settings, 'WECHAT_APP_ID', '')
        mch_id = getattr(settings, 'WECHAT_MCH_ID', '')
        apiv3_key = getattr(settings, 'WECHAT_APIV3_KEY', '')
        cert_serial_no = getattr(settings, 'WECHAT_CERT_SERIAL_NO', '')
        private_key_path = getattr(settings, 'WECHAT_PRIVATE_KEY_PATH', '')

        # 读取私钥
        with open(private_key_path, 'r') as f:
            private_key = f.read()

        # 初始化微信支付客户端
        wxpay = WeChatPay(
            wechatpay_type=WeChatPayType.JSAPI,
            mchid=mch_id,
            private_key=private_key,
            cert_serial_no=cert_serial_no,
            apiv3_key=apiv3_key,
            appid=app_id
        )

        # 验证签名并解密
        result = wxpay.callback(
            headers=request.headers,
            body=request.body
        )

        logger.info(f'收到微信支付V3回调: {result}')

        # 检查支付结果
        if result.get('event_type') == 'TRANSACTION.SUCCESS':
            resource = result.get('resource', {})
            out_trade_no = resource.get('out_trade_no')
            transaction_id = resource.get('transaction_id')
            trade_state = resource.get('trade_state')

            if trade_state == 'SUCCESS':
                # 更新订单状态
                try:
                    order = PaymentOrder.objects.get(order_no=out_trade_no)
                    if order.status == 'pending':
                        order.status = 'paid'
                        order.transaction_id = transaction_id
                        order.paid_at = timezone.now()
                        order.save()
                        logger.info(f'订单 {out_trade_no} 支付成功')

                        # 根据套餐类型处理
                        if order.plan_type == 'quota':
                            # 次数卡：增加1000次额度
                            try:
                                quota, created = UserQuota.objects.get_or_create(user=order.user)
                                quota.add_quota(1000)  # 增加1000次调用额度
                                logger.info(f'用户 {order.user.username} 购买次数卡，额度增加1000次，当前可用: {quota.available_quota}次')
                            except Exception as e:
                                logger.error(f'增加用户额度失败: {str(e)}')
                        elif order.plan_type in ['monthly', 'yearly']:
                            # 会员套餐：开通会员 + 增加100次额度
                            activate_membership(order.user, order.plan_type)
                            logger.info(f'用户 {order.user.username} 开通 {order.plan_type} 会员成功')

                            try:
                                quota, created = UserQuota.objects.get_or_create(user=order.user)
                                quota.add_quota(100)  # 增加100次调用额度
                                logger.info(f'用户 {order.user.username} 额度增加100次，当前可用: {quota.available_quota}次')
                            except Exception as e:
                                logger.error(f'增加用户额度失败: {str(e)}')
                        else:
                            # 其他未知套餐类型：默认增加100次额度
                            try:
                                quota, created = UserQuota.objects.get_or_create(user=order.user)
                                quota.add_quota(100)
                                logger.info(f'用户 {order.user.username} 额度增加100次，当前可用: {quota.available_quota}次')
                            except Exception as e:
                                logger.error(f'增加用户额度失败: {str(e)}')

                except PaymentOrder.DoesNotExist:
                    logger.error(f'订单 {out_trade_no} 不存在')

        # 返回成功响应
        return Response({'code': 'SUCCESS', 'message': '成功'})

    except Exception as e:
        logger.error(f'处理支付回调异常: {str(e)}', exc_info=True)
        return Response(
            {'code': 'FAIL', 'message': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_membership_plans(request):
    """获取会员套餐列表"""
    try:
        # 获取所有启用的套餐
        plans = MembershipPlan.objects.filter(is_active=True)

        # 构造返回数据
        plans_data = []
        for plan in plans:
            plan_dict = {
                'id': plan.plan_id,
                'name': plan.name,
                'price': float(plan.price),
                'duration': plan.duration,
                'badge': plan.badge,
                'popular': plan.is_popular,
                'features': plan.features if plan.features else []
            }

            # 如果有原价，添加原价
            if plan.original_price:
                plan_dict['originalPrice'] = float(plan.original_price)

            # 如果有优惠信息，添加优惠信息
            if plan.discount_info:
                plan_dict['discount'] = plan.discount_info

            plans_data.append(plan_dict)

        return Response({
            'code': 200,
            'message': '获取成功',
            'data': plans_data
        })

    except Exception as e:
        logger.error(f'获取会员套餐失败: {str(e)}', exc_info=True)
        return Response(
            {'code': 500, 'message': f'服务器错误: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
