"""
安盛利益表分析视图
处理安盛API调用的代理
"""
import requests
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_withdrawal(request):
    """
    计算提取金额 - 调用安盛API
    """
    try:
        # 从请求中获取参数
        premium = request.data.get('premium')
        withdrawal_amount = request.data.get('withdrawal_amount', 10000)
        bearer_token = request.data.get('bearer_token')

        # 基本参数验证
        if not premium:
            return Response({
                'status': 'error',
                'message': '请输入每期保费'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not bearer_token:
            return Response({
                'status': 'error',
                'message': '请提供安盛API的Bearer Token'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 构建安盛API请求
        axa_api_url = 'https://az-api.axa.com.hk/api/iprotoolkit/b2c/pos/v1/ext/proposals/illustrate'

        # 计算日期
        today = datetime.now()
        birth_date = (today - timedelta(days=365*35)).strftime('%Y-%m-%d')  # 35岁
        insured_birth_date = today.strftime('%Y-%m-%d')  # 0岁

        # 构建请求体
        payload = {
            "prodCode": "HK_WEB",
            "insuredInfos": [{
                "gender": "M",
                "isSmoker": False,
                "fullName": "JACKSON",
                "dob": insured_birth_date,
                "residency": "CN",
                "nationality": "CN",
                "occupation": "00004",
                "isCompClient": False,
                "sameAsOwnerIndex": -1,
                "age": 0,
                "occupationGroup": "NON_GAIN",
                "residencyGroup": "MCV"
            }],
            "ownerInfos": [{
                "gender": "M",
                "isSmoker": False,
                "fullName": "MIKE",
                "dob": birth_date,
                "residency": "CN",
                "nationality": "CN",
                "occupation": "00003",
                "age": 35,
                "occupationGroup": "GAIN_EMP",
                "residencyGroup": "MCV"
            }],
            "plans": [{
                "covCode": "HK_WEB",
                "planCode": "WEB05",
                "covClass": "S",
                "defaultClass": "S",
                "premTerm": 5,
                "policyTerm": 138,
                "covName": {
                    "en": "WealthAhead II Savings Insurance - Supreme (With extra Death Benefit)",
                    "zh-Hant": "盛利 II 儲蓄保險 – 至尊 (設有額外身故保險賠償)"
                },
                "planInd": "B",
                "payMode": "A",
                "classType": "S",
                "calcBy": "sumAssured",
                "premium": int(premium),
                "printSeq": -1,
                "yearPrem": int(premium),
                "halfYearPrem": int(int(premium) * 0.52),
                "monthPrem": int(int(premium) * 0.09),
                "sumInsured": int(int(premium) * 5),
                "extraOptions": {},
                "paymentTermInd": "N",
                "wholePremPaymentTerm": False,
                "initialModPrem": int(premium),
                "premMataFemale": "",
                "premMattFemale": 5,
                "premMataMale": "",
                "premMattMale": 5,
                "minSumInsured": "10000",
                "maxSumInsured": "90000000",
                "notAllowAutoRiderList": ["HK_APF3R", "HK_SHC1R"],
                "premRate": 200,
                "temporaryLoading": 0,
                "premiumNoDiscountNoLoss": int(premium),
                "premiumScale": 1000,
                "premiumStdNoDiscount": int(premium),
                "premiumNoDiscount": int(premium),
                "permanentLoading": 0
            }],
            "ccy": "USD",
            "policyOptions": {
                "switchCcyOpt": "NA",
                "wdRecipient": "1",
                "wdIndicate": "periodic",
                "wdPayee1WdSwFromOpt0": None,
                "wdPayee1WdKey0": False,
                "flexiContinuationOpt": "0",
                "preFlexiContinuationOpt": "0",
                "fcoEffectiveOpt": None,
                "preFcoEffectiveOpt": None,
                "switchFromOpt": "",
                "withExtraDeathBenefit": "Y",
                "withExtraDeathBenefitCurrent": "Y",
                "swCcyFrom": "",
                "swCcyTo": "",
                "swCcyPercent": "",
                "wdFrom": "",
                "wdTo": "",
                "wdAmount": "",
                "wdSelect": True,
                "withwithdrawOpt": "2",
                "preWdIndicate": "periodic",
                "wdPayee1PwCount": [0],
                "wdPayee1PwCb": [False],
                "wdPayee1PwFrom": [5],
                "wdPayee1PwTo": [138],
                "wdPayee1PwAmount": [int(withdrawal_amount)],
                "wdPayee1PwSwOpt": [""],
                "preWithwithdrawOpt": "2",
                "wdPayee1WdTo0": 138,
                "wdPayee1WdFrom0": 5,
                "wdPayee1WdAmount0": int(withdrawal_amount),
                "wdSwFromOpt": None,
                "lockinKey": False,
                "swCcyKey": False
            },
            "paymentMode": "A",
            "reportOptions": {},
            "custom": {
                "ppsNo": "PPS0002614192",
                "ppsNoDisp": "AA077253-0002614192-1",
                "occupationQuestionsAns": {},
                "pOccupationQuestionsAns": {},
                "recAgentName": None,
                "isQuickQuote": True,
                "skipSTEPolicyNumber": False,
                "hasPremiumHoliday": False,
                "agtCnaBasicPlanListStr": ";WEB05;WEB10;WEBB05;WEBB10;",
                "agtCnaRiderPlanListStr": ";AP;APF3R;APFR;CAP1;CAP2;",
                "agentCodeProposal": "000000-05-077253",
                "agentFax": "",
                "agentDealerGroup": "BK",
                "isNewOccupation": True
            },
            "isBackDate": "N",
            "campaignYesNoSectionValue": "N",
            "originalPlanDetail": {},
            "compCode": "AXAHK",
            "skipParamsPrefill": True
        }

        # 设置请求头
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*',
            'Language': 'zh-Hant',
            'X-Compcode': 'AXAHK',
            'X-Device-Type': 'web',
            'X-Device-Version': '1.41.0.4.30',
            'Origin': 'https://atk.axahk.digital',
            'Referer': 'https://atk.axahk.digital/',
            'Authorization': f'Bearer {bearer_token}'
        }

        # 发送请求到安盛API
        print(f"发送提取金额计算请求到安盛API: {axa_api_url}")
        print(f"保费: {premium}, 提取金额: {withdrawal_amount}")

        response = requests.post(
            axa_api_url,
            json=payload,
            headers=headers,
            timeout=30,
            verify=True
        )

        print(f"安盛API响应状态: {response.status_code}")

        # 检查响应状态
        if response.status_code == 200:
            result = response.json()

            # 返回成功响应，包含POST URL、Request和Response
            return Response({
                'status': 'success',
                'post_url': axa_api_url,
                'post_request': payload,
                'data': result,
                'message': '计算成功'
            })
        elif response.status_code == 401:
            return Response({
                'status': 'error',
                'message': '需要安盛API的Bearer Token。请提供有效的token。',
                'post_url': axa_api_url,
                'post_request': payload,
                'details': response.text,
                'status_code': 401
            }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({
                'status': 'error',
                'message': f'安盛API调用失败 (HTTP {response.status_code})',
                'post_url': axa_api_url,
                'post_request': payload,
                'details': response.text[:1000],
                'status_code': response.status_code
            }, status=status.HTTP_502_BAD_GATEWAY)

    except requests.exceptions.Timeout:
        return Response({
            'status': 'error',
            'message': '请求超时，请稍后重试'
        }, status=status.HTTP_504_GATEWAY_TIMEOUT)

    except requests.exceptions.RequestException as e:
        return Response({
            'status': 'error',
            'message': f'网络请求失败: {str(e)}'
        }, status=status.HTTP_502_BAD_GATEWAY)

    except Exception as e:
        print(f"计算失败: {str(e)}")
        import traceback
        traceback.print_exc()

        return Response({
            'status': 'error',
            'message': f'服务器错误: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_axa_benefit(request):
    """
    调用安盛API进行利益表分析
    """
    try:
        # 从请求中获取参数
        premium = request.data.get('premium')
        analysis_type = request.data.get('analysis_type', 'surrender')
        input_data = request.data.get('input_data', '')

        # 基本参数验证
        if not premium:
            return Response({
                'status': 'error',
                'message': '请输入每期保费'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 构建安盛API请求
        axa_api_url = 'https://az-api.axa.com.hk/api/iprotoolkit/b2c/pos/v1/ext/proposals/illustrate'

        # 计算日期
        today = datetime.now()
        birth_date = (today - timedelta(days=365*35)).strftime('%Y-%m-%d')  # 35岁
        insured_birth_date = today.strftime('%Y-%m-%d')  # 0岁

        # 从input_data中解析提取金额（如果有）
        withdrawal_amount = 10000  # 默认提取金额
        try:
            # 尝试从输入数据中提取数字
            import re
            numbers = re.findall(r'\d+', input_data)
            if numbers and len(numbers) > 0:
                withdrawal_amount = int(numbers[0])
        except:
            pass

        # 构建请求体
        payload = {
            "prodCode": "HK_WEB",
            "insuredInfos": [{
                "gender": "M",
                "isSmoker": False,
                "fullName": "JACKSON",
                "dob": insured_birth_date,
                "residency": "CN",
                "nationality": "CN",
                "occupation": "00004",
                "isCompClient": False,
                "sameAsOwnerIndex": -1,
                "age": 0,
                "occupationGroup": "NON_GAIN",
                "residencyGroup": "MCV"
            }],
            "ownerInfos": [{
                "gender": "M",
                "isSmoker": False,
                "fullName": "MIKE",
                "dob": birth_date,
                "residency": "CN",
                "nationality": "CN",
                "occupation": "00003",
                "age": 35,
                "occupationGroup": "GAIN_EMP",
                "residencyGroup": "MCV"
            }],
            "plans": [{
                "covCode": "HK_WEB",
                "planCode": "WEB05",
                "covClass": "S",
                "defaultClass": "S",
                "premTerm": 5,
                "policyTerm": 138,
                "covName": {
                    "en": "WealthAhead II Savings Insurance - Supreme (With extra Death Benefit)",
                    "zh-Hant": "盛利 II 儲蓄保險 – 至尊 (設有額外身故保險賠償)"
                },
                "planInd": "B",
                "payMode": "A",
                "classType": "S",
                "calcBy": "sumAssured",
                "premium": int(premium),
                "printSeq": -1,
                "yearPrem": int(premium),
                "halfYearPrem": int(int(premium) * 0.52),
                "monthPrem": int(int(premium) * 0.09),
                "sumInsured": int(int(premium) * 5),
                "extraOptions": {},
                "paymentTermInd": "N",
                "wholePremPaymentTerm": False,
                "initialModPrem": int(premium),
                "premMataFemale": "",
                "premMattFemale": 5,
                "premMataMale": "",
                "premMattMale": 5,
                "minSumInsured": "10000",
                "maxSumInsured": "90000000",
                "notAllowAutoRiderList": ["HK_APF3R", "HK_SHC1R"],
                "premRate": 200,
                "temporaryLoading": 0,
                "premiumNoDiscountNoLoss": int(premium),
                "premiumScale": 1000,
                "premiumStdNoDiscount": int(premium),
                "premiumNoDiscount": int(premium),
                "permanentLoading": 0
            }],
            "ccy": "USD",
            "policyOptions": {
                "switchCcyOpt": "NA",
                "wdRecipient": "1",
                "wdIndicate": "periodic",
                "wdPayee1WdSwFromOpt0": None,
                "wdPayee1WdKey0": False,
                "flexiContinuationOpt": "0",
                "preFlexiContinuationOpt": "0",
                "fcoEffectiveOpt": None,
                "preFcoEffectiveOpt": None,
                "switchFromOpt": "",
                "withExtraDeathBenefit": "Y",
                "withExtraDeathBenefitCurrent": "Y",
                "swCcyFrom": "",
                "swCcyTo": "",
                "swCcyPercent": "",
                "wdFrom": "",
                "wdTo": "",
                "wdAmount": "",
                "wdSelect": True,
                "withwithdrawOpt": "2",
                "preWdIndicate": "periodic",
                "wdPayee1PwCount": [0],
                "wdPayee1PwCb": [False],
                "wdPayee1PwFrom": [5],
                "wdPayee1PwTo": [138],
                "wdPayee1PwAmount": [withdrawal_amount],
                "wdPayee1PwSwOpt": [""],
                "preWithwithdrawOpt": "2",
                "wdPayee1WdTo0": 138,
                "wdPayee1WdFrom0": 5,
                "wdPayee1WdAmount0": withdrawal_amount,
                "wdSwFromOpt": None,
                "lockinKey": False,
                "swCcyKey": False
            },
            "paymentMode": "A",
            "reportOptions": {},
            "custom": {
                "ppsNo": "PPS0002614192",
                "ppsNoDisp": "AA077253-0002614192-1",
                "occupationQuestionsAns": {},
                "pOccupationQuestionsAns": {},
                "recAgentName": None,
                "isQuickQuote": True,
                "skipSTEPolicyNumber": False,
                "hasPremiumHoliday": False,
                "agtCnaBasicPlanListStr": ";WEB05;WEB10;WEBB05;WEBB10;",
                "agtCnaRiderPlanListStr": ";AP;APF3R;APFR;CAP1;CAP2;",
                "agentCodeProposal": "000000-05-077253",
                "agentFax": "",
                "agentDealerGroup": "BK",
                "isNewOccupation": True
            },
            "isBackDate": "N",
            "campaignYesNoSectionValue": "N",
            "originalPlanDetail": {},
            "compCode": "AXAHK",
            "skipParamsPrefill": True
        }

        # 设置请求头
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*',
            'Language': 'zh-Hant',
            'X-Compcode': 'AXAHK',
            'X-Device-Type': 'web',
            'X-Device-Version': '1.41.0.4.30',
            'Origin': 'https://atk.axahk.digital',
            'Referer': 'https://atk.axahk.digital/',
        }

        # 如果用户提供了自定义的Bearer token，使用它
        bearer_token = request.data.get('bearer_token')
        if bearer_token:
            headers['Authorization'] = f'Bearer {bearer_token}'

        # 发送请求到安盛API
        print(f"发送请求到安盛API: {axa_api_url}")
        print(f"保费: {premium}, 提取金额: {withdrawal_amount}")
        print(f"请求头: {headers}")

        response = requests.post(
            axa_api_url,
            json=payload,
            headers=headers,
            timeout=30,
            verify=True  # 验证SSL证书
        )

        print(f"安盛API响应状态: {response.status_code}")
        print(f"响应内容前500字符: {response.text[:500]}")

        # 检查响应状态
        if response.status_code == 200:
            result = response.json()

            # 返回成功响应
            return Response({
                'status': 'success',
                'data': result,
                'message': '分析成功'
            })
        elif response.status_code == 401:
            # 未授权 - 需要Bearer token
            return Response({
                'status': 'error',
                'message': '需要安盛API的Bearer Token。请提供有效的token。',
                'details': response.text,
                'status_code': 401
            }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            # API调用失败
            return Response({
                'status': 'error',
                'message': f'安盛API调用失败 (HTTP {response.status_code})',
                'details': response.text[:1000],  # 限制返回的错误信息长度
                'status_code': response.status_code
            }, status=status.HTTP_502_BAD_GATEWAY)

    except requests.exceptions.Timeout:
        return Response({
            'status': 'error',
            'message': '请求超时，请稍后重试'
        }, status=status.HTTP_504_GATEWAY_TIMEOUT)

    except requests.exceptions.RequestException as e:
        return Response({
            'status': 'error',
            'message': f'网络请求失败: {str(e)}'
        }, status=status.HTTP_502_BAD_GATEWAY)

    except Exception as e:
        print(f"分析失败: {str(e)}")
        import traceback
        traceback.print_exc()

        return Response({
            'status': 'error',
            'message': f'服务器错误: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
