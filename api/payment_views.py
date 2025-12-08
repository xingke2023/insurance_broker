from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import requests
import hashlib
import time
import logging
import xml.etree.ElementTree as ET
from decimal import Decimal
from .models import PaymentOrder, WeChatUser

logger = logging.getLogger(__name__)


def generate_order_no():
    """生成订单号"""
    import uuid
    return f"ORDER_{int(time.time())}_{uuid.uuid4().hex[:8].upper()}"


def generate_sign(params, api_key):
    """生成微信支付签名"""
    # 过滤空值和sign字段
    filtered_params = {k: v for k, v in params.items() if v and k != 'sign'}
    # 按照key的ASCII码排序
    sorted_params = sorted(filtered_params.items())
    # 拼接参数（确保值都是字符串）
    string_sign_temp = '&'.join([f"{k}={str(v)}" for k, v in sorted_params])
    # 拼接API密钥
    string_sign_temp += f"&key={api_key}"
    # 打印签名字符串用于调试
    logger.info(f'签名字符串: {string_sign_temp}')
    # MD5加密并转大写
    sign = hashlib.md5(string_sign_temp.encode('utf-8')).hexdigest().upper()
    logger.info(f'生成签名: {sign}')
    return sign


def dict_to_xml(data):
    """字典转XML"""
    xml = '<xml>'
    for k, v in data.items():
        xml += f'<{k}><![CDATA[{v}]]></{k}>'
    xml += '</xml>'
    return xml


def xml_to_dict(xml_str):
    """XML转字典"""
    root = ET.fromstring(xml_str)
    return {child.tag: child.text for child in root}


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_order(request):
    """创建支付订单"""
    amount = request.data.get('amount')
    description = request.data.get('description', '商品购买')

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
        status='pending'
    )

    # 调用微信统一下单接口
    mch_id = getattr(settings, 'WECHAT_MCH_ID', '')
    api_key = getattr(settings, 'WECHAT_API_KEY', '')
    app_id = getattr(settings, 'WECHAT_APP_ID', '')

    if not mch_id or not api_key or not app_id:
        logger.error('微信支付配置缺失')
        return Response(
            {'code': 500, 'message': '服务器配置错误'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # 统一下单参数
    notify_url = getattr(settings, 'WECHAT_NOTIFY_URL', 'https://cardbuy.xingke888.com/api/payment/notify')
    params = {
        'appid': app_id,
        'mch_id': mch_id,
        'nonce_str': hashlib.md5(str(time.time()).encode()).hexdigest(),
        'body': description,
        'out_trade_no': order_no,
        'total_fee': int(amount * 100),  # 金额转为分（整数）
        'spbill_create_ip': request.META.get('REMOTE_ADDR', '127.0.0.1'),
        'notify_url': notify_url,
        'trade_type': 'JSAPI',
        'openid': openid
    }

    logger.info(f'统一下单参数: {params}')

    # 生成签名
    params['sign'] = generate_sign(params, api_key)

    logger.info(f'最终请求参数: {params}')

    # 转换为XML
    xml_data = dict_to_xml(params)
    logger.info(f'发送XML: {xml_data}')

    try:
        # 调用微信统一下单接口
        response = requests.post(
            'https://api.mch.weixin.qq.com/pay/unifiedorder',
            data=xml_data.encode('utf-8'),
            headers={'Content-Type': 'application/xml'},
            timeout=10
        )

        logger.info(f'微信返回XML: {response.content.decode("utf-8")}')

        # 解析返回结果
        result = xml_to_dict(response.content)

        if result.get('return_code') != 'SUCCESS':
            logger.error(f'微信统一下单失败: {result}')
            return Response(
                {'code': 400, 'message': f"下单失败: {result.get('return_msg', '未知错误')}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if result.get('result_code') != 'SUCCESS':
            logger.error(f'微信统一下单业务失败: {result}')
            return Response(
                {'code': 400, 'message': f"下单失败: {result.get('err_code_des', '未知错误')}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        prepay_id = result.get('prepay_id')
        order.prepay_id = prepay_id
        order.save()

        # 生成小程序支付参数
        timestamp = str(int(time.time()))
        nonce_str = hashlib.md5(str(time.time()).encode()).hexdigest()
        pay_sign_params = {
            'appId': app_id,
            'timeStamp': timestamp,
            'nonceStr': nonce_str,
            'package': f'prepay_id={prepay_id}',
            'signType': 'MD5'
        }
        pay_sign = generate_sign(pay_sign_params, api_key)

        return Response({
            'code': 200,
            'message': '创建订单成功',
            'data': {
                'order_no': order_no,
                'payment': {
                    'timeStamp': timestamp,
                    'nonceStr': nonce_str,
                    'package': f'prepay_id={prepay_id}',
                    'signType': 'MD5',
                    'paySign': pay_sign
                }
            }
        })

    except requests.RequestException as e:
        logger.error(f'请求微信支付接口失败: {str(e)}')
        return Response(
            {'code': 500, 'message': '网络请求失败'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        logger.error(f'创建订单异常: {str(e)}')
        return Response(
            {'code': 500, 'message': '服务器内部错误'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([])
def payment_notify(request):
    """微信支付回调通知"""
    try:
        # 解析XML数据
        xml_data = request.body
        result = xml_to_dict(xml_data)

        logger.info(f'收到微信支付回调: {result}')

        # 验证签名
        api_key = getattr(settings, 'WECHAT_API_KEY', '')
        sign = result.pop('sign', '')
        calculated_sign = generate_sign(result, api_key)

        if sign != calculated_sign:
            logger.error('微信支付回调签名验证失败')
            return Response(dict_to_xml({
                'return_code': 'FAIL',
                'return_msg': '签名验证失败'
            }), content_type='application/xml')

        # 检查支付结果
        if result.get('return_code') == 'SUCCESS' and result.get('result_code') == 'SUCCESS':
            order_no = result.get('out_trade_no')
            transaction_id = result.get('transaction_id')

            # 更新订单状态
            try:
                order = PaymentOrder.objects.get(order_no=order_no)
                if order.status == 'pending':
                    order.status = 'paid'
                    order.transaction_id = transaction_id
                    order.paid_at = timezone.now()
                    order.save()
                    logger.info(f'订单 {order_no} 支付成功')
            except PaymentOrder.DoesNotExist:
                logger.error(f'订单 {order_no} 不存在')

        # 返回成功响应
        return Response(dict_to_xml({
            'return_code': 'SUCCESS',
            'return_msg': 'OK'
        }), content_type='application/xml')

    except Exception as e:
        logger.error(f'处理支付回调异常: {str(e)}')
        return Response(dict_to_xml({
            'return_code': 'FAIL',
            'return_msg': '处理失败'
        }), content_type='application/xml')
