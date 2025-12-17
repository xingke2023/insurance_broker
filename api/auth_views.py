from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
import requests
import logging
from .models import WeChatUser, Membership
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


def generate_nice_nickname():
    """生成好听的随机昵称"""
    import random

    # 形容词列表 - 积极正面的词汇
    adjectives = [
        '阳光', '温柔', '可爱', '快乐', '开心', '幸运', '勇敢', '聪明',
        '善良', '热情', '活力', '梦想', '自由', '浪漫', '清新', '优雅',
        '甜美', '灵动', '睿智', '真诚', '乐观', '坚强', '友善', '纯真',
        '勤奋', '机智', '风趣', '爽朗', '淡定', '从容', '洒脱', '独立'
    ]

    # 名词列表 - 美好事物
    nouns = [
        '微风', '星辰', '彩虹', '花朵', '海浪', '云朵', '晨光', '夜空',
        '小鹿', '飞鸟', '蝴蝶', '雪花', '月光', '阳光', '清风', '细雨',
        '樱花', '流星', '白云', '枫叶', '海豚', '熊猫', '小熊', '兔子',
        '天使', '精灵', '星光', '晚霞', '朝阳', '江河', '湖泊', '森林'
    ]

    # 随机组合：形容词 + 的 + 名词
    adj = random.choice(adjectives)
    noun = random.choice(nouns)

    # 30%概率使用"的"连接，70%概率直接连接
    if random.random() < 0.3:
        nickname = f'{adj}的{noun}'
    else:
        nickname = f'{adj}{noun}'

    return nickname


def create_trial_membership(user):
    """为新用户创建7天试用会员"""
    try:
        # 检查用户是否已有会员
        if Membership.objects.filter(user=user).exists():
            logger.info(f'用户 {user.username} 已有会员记录，跳过试用创建')
            return

        # 创建7天试用会员
        now = timezone.now()
        trial_end = now + timedelta(days=7)

        membership = Membership.objects.create(
            user=user,
            plan_type='trial',  # 试用类型
            is_active=True,
            start_date=now,
            end_date=trial_end,
            documents_created=0
        )

        logger.info(f'✅ 为用户 {user.username} 创建7天试用会员，到期时间: {trial_end}')

        # 为新用户创建UserQuota并赋予3次初始额度
        from .models import UserQuota
        quota, created = UserQuota.objects.get_or_create(
            user=user,
            defaults={'available_quota': 3}
        )
        if created:
            logger.info(f'✅ 为用户 {user.username} 创建初始额度: 3次')

        return membership
    except Exception as e:
        logger.error(f'创建试用会员失败: {str(e)}')
        return None


@api_view(['POST'])
@permission_classes([AllowAny])
def generate_miniprogram_scheme(request):
    """生成小程序URL Scheme，用于从H5页面跳转到小程序"""
    path = request.data.get('path', 'pages/index/index')
    query = request.data.get('query', '')

    app_id = getattr(settings, 'WECHAT_APP_ID', '')
    app_secret = getattr(settings, 'WECHAT_APP_SECRET', '')

    if not app_id or not app_secret:
        return Response(
            {'code': 500, 'message': '服务器配置错误'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    try:
        # 获取access_token
        token_url = 'https://api.weixin.qq.com/cgi-bin/token'
        token_params = {
            'grant_type': 'client_credential',
            'appid': app_id,
            'secret': app_secret
        }
        token_response = requests.get(token_url, params=token_params, timeout=10)
        token_data = token_response.json()

        if 'errcode' in token_data and token_data['errcode'] != 0:
            logger.error(f'获取access_token失败: {token_data}')
            return Response(
                {'code': 400, 'message': f'获取access_token失败: {token_data.get("errmsg", "未知错误")}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        access_token = token_data.get('access_token')

        # 生成URL Scheme
        scheme_url = f'https://api.weixin.qq.com/wxa/generatescheme?access_token={access_token}'
        scheme_data = {
            'jump_wxa': {
                'path': path,
                'query': query
            },
            'is_expire': True,
            'expire_type': 1,
            'expire_interval': 30  # 30天有效期
        }

        scheme_response = requests.post(scheme_url, json=scheme_data, timeout=10)
        scheme_result = scheme_response.json()

        if 'errcode' in scheme_result and scheme_result['errcode'] != 0:
            logger.error(f'生成URL Scheme失败: {scheme_result}')
            return Response(
                {'code': 400, 'message': f'生成URL Scheme失败: {scheme_result.get("errmsg", "未知错误")}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        openlink = scheme_result.get('openlink')

        return Response({
            'code': 200,
            'message': '生成成功',
            'data': {
                'scheme': openlink
            }
        })

    except requests.RequestException as e:
        logger.error(f'请求微信接口失败: {str(e)}')
        return Response(
            {'code': 500, 'message': '网络请求失败，请稍后重试'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        logger.error(f'生成URL Scheme异常: {str(e)}')
        return Response(
            {'code': 500, 'message': '服务器内部错误'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """用户注册"""
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    full_name = request.data.get('full_name', '')

    if not username or not email or not password:
        return Response(
            {'error': '用户名、邮箱和密码不能为空'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {'error': '用户名已存在'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {'error': '邮箱已被注册'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 创建用户
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    if full_name:
        names = full_name.split(' ', 1)
        user.first_name = names[0]
        if len(names) > 1:
            user.last_name = names[1]
        user.save()

    # 创建7天试用会员
    create_trial_membership(user)

    # 生成token
    refresh = RefreshToken.for_user(user)

    return Response({
        'message': '注册成功',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.get_full_name() or user.username,
            'groups': [group.name for group in user.groups.all()],  # 返回用户所属的组
            'is_staff': user.is_staff,  # 返回是否是管理员
        },
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """用户登录"""
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': '用户名和密码不能为空'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)

    if user is None:
        return Response(
            {'error': '用户名或密码错误'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # 生成token
    refresh = RefreshToken.for_user(user)

    return Response({
        'message': '登录成功',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.get_full_name() or user.username,
            'groups': [group.name for group in user.groups.all()],  # 返回用户所属的组
            'is_staff': user.is_staff,  # 返回是否是管理员
        },
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    })


@api_view(['GET', 'PUT'])
def user_profile(request):
    """获取或更新当前用户信息"""
    user = request.user

    if request.method == 'GET':
        # 获取用户信息
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.get_full_name() or user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined,
            'groups': [group.name for group in user.groups.all()],  # 返回用户所属的组
            'is_staff': user.is_staff,  # 返回是否是管理员
        }

        # 如果用户有关联的微信信息，也返回
        try:
            wechat_profile = user.wechat_profile
            user_data['wechat'] = {
                'nickname': wechat_profile.nickname,
                'avatar': wechat_profile.avatar_url,
                'phone': wechat_profile.phone_number,
            }
        except:
            pass

        return Response(user_data)

    elif request.method == 'PUT':
        # 更新用户信息
        data = request.data

        # 更新邮箱
        if 'email' in data and data['email']:
            # 检查邮箱是否已被其他用户使用
            if User.objects.filter(email=data['email']).exclude(id=user.id).exists():
                return Response(
                    {'error': '该邮箱已被使用'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.email = data['email']

        # 更新姓名
        if 'full_name' in data:
            full_name = data['full_name'].strip()
            if full_name:
                # 分割姓名为 first_name 和 last_name
                name_parts = full_name.split(' ', 1)
                user.first_name = name_parts[0]
                user.last_name = name_parts[1] if len(name_parts) > 1 else ''
            else:
                user.first_name = ''
                user.last_name = ''

        # 也支持直接更新 first_name 和 last_name
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']

        user.save()

        return Response({
            'message': '个人资料更新成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.get_full_name() or user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        })


@api_view(['POST'])
@permission_classes([AllowAny])
def wechat_login(request):
    """微信小程序登录"""
    code = request.data.get('code')
    phone_code = request.data.get('phone_code')  # 获取手机号code

    if not code:
        return Response(
            {'code': 400, 'message': '缺少code参数'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 调用微信接口获取session_key和openid
    app_id = getattr(settings, 'WECHAT_APP_ID', '')
    app_secret = getattr(settings, 'WECHAT_APP_SECRET', '')

    if not app_id or not app_secret:
        logger.error('微信小程序配置缺失: WECHAT_APP_ID 或 WECHAT_APP_SECRET 未设置')
        return Response(
            {'code': 500, 'message': '服务器配置错误'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # 调用微信code2Session接口
    wx_url = 'https://api.weixin.qq.com/sns/jscode2session'
    params = {
        'appid': app_id,
        'secret': app_secret,
        'js_code': code,
        'grant_type': 'authorization_code'
    }

    try:
        response = requests.get(wx_url, params=params, timeout=10)
        wx_data = response.json()

        if 'errcode' in wx_data and wx_data['errcode'] != 0:
            logger.error(f'微信登录失败: {wx_data}')
            return Response(
                {'code': 400, 'message': f'微信登录失败: {wx_data.get("errmsg", "未知错误")}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        openid = wx_data.get('openid')
        session_key = wx_data.get('session_key')
        unionid = wx_data.get('unionid')

        if not openid:
            logger.error('微信接口未返回openid')
            return Response(
                {'code': 400, 'message': '获取用户标识失败'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 如果有手机号code，获取手机号
        phone_number = None
        if phone_code:
            try:
                # 获取access_token
                token_url = 'https://api.weixin.qq.com/cgi-bin/token'
                token_params = {
                    'grant_type': 'client_credential',
                    'appid': app_id,
                    'secret': app_secret
                }
                token_response = requests.get(token_url, params=token_params, timeout=10)
                token_data = token_response.json()

                if 'access_token' in token_data:
                    access_token = token_data['access_token']

                    # 获取手机号
                    phone_url = f'https://api.weixin.qq.com/wxa/business/getuserphonenumber?access_token={access_token}'
                    phone_response = requests.post(phone_url, json={'code': phone_code}, timeout=10)
                    phone_data = phone_response.json()

                    logger.info(f'获取手机号响应: {phone_data}')

                    if phone_data.get('errcode') == 0 and 'phone_info' in phone_data:
                        phone_number = phone_data['phone_info'].get('phoneNumber')
                        logger.info(f'成功获取手机号: {phone_number}')
                else:
                    logger.error(f'获取access_token失败: {token_data}')
            except Exception as e:
                logger.error(f'获取手机号失败: {str(e)}')

        # 查找或创建微信用户（优先使用unionid，如果没有unionid则使用openid）
        wechat_user = None
        user = None

        # 优先使用 unionid 查找用户
        if unionid:
            try:
                wechat_user = WeChatUser.objects.get(unionid=unionid)
                logger.info(f'通过 unionid 找到用户: {wechat_user.user.username}')

                # 更新 openid 和 session_key（因为同一个 unionid 在不同平台的 openid 可能不同）
                wechat_user.openid = openid
                wechat_user.session_key = session_key
                if phone_number:
                    wechat_user.phone_number = phone_number
                wechat_user.save()
                user = wechat_user.user

            except WeChatUser.DoesNotExist:
                logger.info(f'未找到 unionid={unionid} 的用户，尝试使用 openid 查找')

        # 如果通过 unionid 没找到，则使用 openid 查找
        if not wechat_user:
            try:
                wechat_user = WeChatUser.objects.get(openid=openid)
                logger.info(f'通过 openid 找到用户: {wechat_user.user.username}')

                # 更新 session_key 和 unionid
                wechat_user.session_key = session_key
                if unionid:
                    wechat_user.unionid = unionid
                    logger.info(f'更新用户的 unionid: {unionid}')
                if phone_number:
                    wechat_user.phone_number = phone_number
                wechat_user.save()
                user = wechat_user.user

            except WeChatUser.DoesNotExist:
                logger.info(f'未找到 openid={openid} 的用户，创建新用户')

        # 如果用户存在，检查是否有效
        if user:
            if not user.is_active:
                logger.warning(f'用户 {user.username} 已被禁用，拒绝登录')
                return Response(
                    {'code': 401, 'message': '用户已被禁用，请联系管理员'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        else:
            # 创建新用户
            # 如果有 unionid，使用 unionid 作为用户名的一部分
            if unionid:
                username = f'wx_{unionid[:20]}'
                logger.info(f'使用 unionid 创建用户: {username}')
            else:
                username = f'wx_{openid[:20]}'
                logger.info(f'使用 openid 创建用户: {username}')

            # 生成随机密码
            import secrets
            random_password = secrets.token_urlsafe(32)
            user = User.objects.create_user(
                username=username,
                password=random_password
            )

            # 创建微信用户关联，使用好听的默认昵称
            default_nickname = generate_nice_nickname()
            wechat_user = WeChatUser.objects.create(
                user=user,
                openid=openid,
                session_key=session_key,
                unionid=unionid or '',
                phone_number=phone_number or '',
                nickname=default_nickname  # 设置默认昵称
            )

            logger.info(f'✨ 为新用户生成昵称: {default_nickname}')

            # 创建7天试用会员
            create_trial_membership(user)

        # 生成JWT token
        refresh = RefreshToken.for_user(user)

        # 检查用户是否已有手机号
        has_phone = bool(wechat_user.phone_number)

        # 处理头像URL - 如果是相对路径，转换为完整URL
        avatar_url = wechat_user.avatar_url or ''
        if avatar_url and not avatar_url.startswith('http'):
            # 相对路径，拼接域名
            avatar_url = request.build_absolute_uri(avatar_url)

        return Response({
            'code': 200,
            'message': '登录成功',
            'data': {
                'token': str(refresh.access_token),
                'refresh': str(refresh),
                'userInfo': {
                    'id': user.id,
                    'username': user.username,
                    'nickname': wechat_user.nickname or '',
                    'avatar': avatar_url,
                    'phone': phone_number or wechat_user.phone_number or '',
                    'hasPhone': has_phone,  # 是否已有手机号
                    'groups': [group.name for group in user.groups.all()],  # 返回用户所属的组
                    'is_staff': user.is_staff,  # 返回是否是管理员
                }
            }
        })

    except requests.RequestException as e:
        logger.error(f'请求微信接口失败: {str(e)}')
        return Response(
            {'code': 500, 'message': '网络请求失败，请稍后重试'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        logger.error(f'微信登录异常: {str(e)}')
        return Response(
            {'code': 500, 'message': '服务器内部错误'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def wechat_web_auth(request):
    """
    微信网页授权登录
    前端通过微信网页授权获取code后，传给后端换取access_token和用户信息
    """
    code = request.data.get('code')

    if not code:
        return Response(
            {'code': 400, 'message': '缺少code参数'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 从配置中获取公众号的appid和secret（不是小程序的）
    # 注意：网页授权需要使用公众号的配置
    app_id = getattr(settings, 'WECHAT_WEB_APP_ID', '') or getattr(settings, 'WECHAT_APP_ID', '')
    app_secret = getattr(settings, 'WECHAT_WEB_APP_SECRET', '') or getattr(settings, 'WECHAT_APP_SECRET', '')

    if not app_id or not app_secret:
        logger.error('微信网页授权配置缺失')
        return Response(
            {'code': 500, 'message': '服务器配置错误'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    try:
        # 1. 通过code换取网页授权access_token
        token_url = 'https://api.weixin.qq.com/sns/oauth2/access_token'
        token_params = {
            'appid': app_id,
            'secret': app_secret,
            'code': code,
            'grant_type': 'authorization_code'
        }

        token_response = requests.get(token_url, params=token_params, timeout=10)
        token_data = token_response.json()

        logger.info(f'微信网页授权token响应: {token_data}')

        if 'errcode' in token_data:
            logger.error(f'获取access_token失败: {token_data}')
            return Response(
                {'code': 400, 'message': f'微信授权失败: {token_data.get("errmsg", "未知错误")}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        access_token = token_data.get('access_token')
        openid = token_data.get('openid')
        unionid = token_data.get('unionid')

        if not access_token or not openid:
            logger.error('微信接口未返回access_token或openid')
            return Response(
                {'code': 400, 'message': '获取用户标识失败'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. 拉取用户信息(需scope为 snsapi_userinfo)
        userinfo_url = 'https://api.weixin.qq.com/sns/userinfo'
        userinfo_params = {
            'access_token': access_token,
            'openid': openid,
            'lang': 'zh_CN'
        }

        userinfo_response = requests.get(userinfo_url, params=userinfo_params, timeout=10)
        userinfo_data = userinfo_response.json()

        logger.info(f'微信用户信息响应: {userinfo_data}')

        if 'errcode' in userinfo_data:
            # 如果scope只是snsapi_base，则没有用户详细信息，只有openid
            logger.warning(f'获取用户信息失败，可能是授权scope不足: {userinfo_data}')
            nickname = generate_nice_nickname()  # 使用好听的昵称
            avatar_url = ''
        else:
            nickname = userinfo_data.get('nickname', generate_nice_nickname())  # 如果没有昵称，使用好听的昵称
            avatar_url = userinfo_data.get('headimgurl', '')

        # 3. 查找或创建微信用户（优先使用unionid，如果没有unionid则使用openid）
        wechat_user = None
        user = None

        # 优先使用 unionid 查找用户
        if unionid:
            try:
                wechat_user = WeChatUser.objects.get(unionid=unionid)
                logger.info(f'[网页授权] 通过 unionid 找到用户: {wechat_user.user.username}')

                # 更新 openid 和用户信息（因为同一个 unionid 在不同平台的 openid 可能不同）
                wechat_user.openid = openid
                wechat_user.nickname = nickname
                wechat_user.avatar_url = avatar_url
                wechat_user.save()
                user = wechat_user.user

            except WeChatUser.DoesNotExist:
                logger.info(f'[网页授权] 未找到 unionid={unionid} 的用户，尝试使用 openid 查找')

        # 如果通过 unionid 没找到，则使用 openid 查找
        if not wechat_user:
            try:
                wechat_user = WeChatUser.objects.get(openid=openid)
                logger.info(f'[网页授权] 通过 openid 找到用户: {wechat_user.user.username}')

                # 更新用户信息和 unionid
                wechat_user.nickname = nickname
                wechat_user.avatar_url = avatar_url
                if unionid:
                    wechat_user.unionid = unionid
                    logger.info(f'[网页授权] 更新用户的 unionid: {unionid}')
                wechat_user.save()
                user = wechat_user.user

            except WeChatUser.DoesNotExist:
                logger.info(f'[网页授权] 未找到 openid={openid} 的用户，创建新用户')

        # 如果用户存在，检查是否有效
        if user:
            if not user.is_active:
                logger.warning(f'用户 {user.username} 已被禁用，拒绝登录')
                return Response(
                    {'code': 401, 'message': '用户已被禁用，请联系管理员'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        else:
            # 创建新用户
            # 如果有 unionid，使用 unionid 作为用户名的一部分
            if unionid:
                username = f'wx_{unionid[:20]}'
                logger.info(f'[网页授权] 使用 unionid 创建用户: {username}')
            else:
                username = f'wx_{openid[:20]}'
                logger.info(f'[网页授权] 使用 openid 创建用户: {username}')

            import secrets
            random_password = secrets.token_urlsafe(32)
            user = User.objects.create_user(
                username=username,
                password=random_password,
                first_name=nickname[:30] if nickname else ''
            )

            # 创建微信用户关联
            wechat_user = WeChatUser.objects.create(
                user=user,
                openid=openid,
                unionid=unionid or '',
                nickname=nickname,
                avatar_url=avatar_url
            )

            # 创建7天试用会员
            create_trial_membership(user)

        # 4. 生成JWT token
        refresh = RefreshToken.for_user(user)

        return Response({
            'code': 200,
            'message': '登录成功',
            'data': {
                'token': str(refresh.access_token),
                'refresh': str(refresh),
                'userInfo': {
                    'id': user.id,
                    'username': user.username,
                    'nickname': wechat_user.nickname,
                    'avatar': wechat_user.avatar_url,
                    'full_name': user.get_full_name() or wechat_user.nickname or user.username,
                    'groups': [group.name for group in user.groups.all()],  # 返回用户所属的组
                    'is_staff': user.is_staff,  # 返回是否是管理员
                }
            }
        })

    except requests.RequestException as e:
        logger.error(f'请求微信接口失败: {str(e)}')
        return Response(
            {'code': 500, 'message': '网络请求失败，请稍后重试'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        logger.error(f'微信网页授权异常: {str(e)}')
        import traceback
        logger.error(traceback.format_exc())
        return Response(
            {'code': 500, 'message': '服务器内部错误'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def wechat_update_profile(request):
    """更新微信用户的昵称和头像"""
    user = request.user
    nickname = request.data.get('nickname', '')
    avatar_url = request.data.get('avatar_url', '')

    try:
        # 获取或创建微信用户记录
        wechat_user = user.wechat_profile

        # 更新信息
        if nickname:
            wechat_user.nickname = nickname
        if avatar_url:
            wechat_user.avatar_url = avatar_url

        wechat_user.save()

        logger.info(f'用户 {user.username} 更新了微信信息: 昵称={nickname}, 头像={avatar_url[:50] if avatar_url else ""}...')

        # 处理头像URL - 如果是相对路径，转换为完整URL
        response_avatar = wechat_user.avatar_url or ''
        if response_avatar and not response_avatar.startswith('http'):
            response_avatar = request.build_absolute_uri(response_avatar)

        return Response({
            'code': 200,
            'message': '更新成功',
            'data': {
                'nickname': wechat_user.nickname,
                'avatar': response_avatar
            }
        })

    except Exception as e:
        logger.error(f'更新微信用户信息失败: {str(e)}')
        return Response(
            {'code': 500, 'message': '更新失败'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def wechat_upload_avatar(request):
    """上传微信用户头像"""
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile
    import os
    from datetime import datetime

    try:
        avatar_file = request.FILES.get('avatar')

        if not avatar_file:
            return Response(
                {'code': 400, 'message': '未上传文件'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 生成文件名
        ext = os.path.splitext(avatar_file.name)[1] or '.jpg'
        filename = f'avatars/{request.user.id}_{datetime.now().strftime("%Y%m%d%H%M%S")}{ext}'

        # 保存文件
        path = default_storage.save(filename, ContentFile(avatar_file.read()))
        file_url = default_storage.url(path)

        logger.info(f'用户 {request.user.username} 上传了头像: {file_url}')

        return Response({
            'code': 200,
            'message': '上传成功',
            'data': {
                'avatar_url': file_url
            }
        })

    except Exception as e:
        logger.error(f'上传头像失败: {str(e)}')
        return Response(
            {'code': 500, 'message': '上传失败'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_page_permissions(request):
    """获取当前用户的页面访问权限"""
    from .models import PagePermission
    
    user = request.user
    
    # 获取所有启用的页面权限配置
    page_permissions = PagePermission.objects.filter(is_active=True).prefetch_related('allowed_groups')
    
    # 构建权限列表
    accessible_pages = []
    
    for page in page_permissions:
        # 检查用户是否有权限访问此页面
        if page.check_user_permission(user):
            accessible_pages.append({
                'page_code': page.page_code,
                'page_name': page.page_name,
                'route_path': page.route_path,
                'icon': page.icon,
                'color': page.color,
                'description': page.description,
                'sort_order': page.sort_order,
            })
    
    # 按排序字段排序
    accessible_pages.sort(key=lambda x: x['sort_order'])
    
    return Response({
        'status': 'success',
        'data': accessible_pages
    })
