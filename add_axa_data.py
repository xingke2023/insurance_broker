"""
添加安盛保险公司及其请求配置到数据库
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import InsuranceCompany, InsuranceCompanyRequest
from datetime import datetime, timedelta

def add_axa_data():
    """添加安盛保险公司和两个请求配置"""

    # 1. 创建或获取安盛保险公司
    axa_company, created = InsuranceCompany.objects.get_or_create(
        code='axa',
        defaults={
            'name': '安盛',
            'name_en': 'AXA',
            'icon': '🏢',
            'color_gradient': 'from-blue-600 to-blue-700',
            'bg_color': 'bg-blue-50',
            'description': '安盛保险有限公司',
            'is_active': True,
            'sort_order': 4
        }
    )

    if created:
        print(f"✓ 创建安盛保险公司记录")
    else:
        print(f"✓ 安盛保险公司记录已存在")

    # 2. 添加利益表计算请求
    benefit_table_request = {
        "prodCode": "HK_WEB",
        "insuredInfos": [{
            "gender": "M",
            "isSmoker": False,
            "fullName": "JACKSON",
            "dob": "{{insured_birth_date}}",
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
            "dob": "{{owner_birth_date}}",
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
            "premium": "{{premium}}",
            "printSeq": -1,
            "yearPrem": "{{premium}}",
            "halfYearPrem": "{{premium_half_year}}",
            "monthPrem": "{{premium_month}}",
            "sumInsured": "{{sum_insured}}",
            "extraOptions": {},
            "paymentTermInd": "N",
            "wholePremPaymentTerm": False,
            "initialModPrem": "{{premium}}",
            "premMataFemale": "",
            "premMattFemale": 5,
            "premMataMale": "",
            "premMattMale": 5,
            "minSumInsured": "10000",
            "maxSumInsured": "90000000",
            "notAllowAutoRiderList": ["HK_APF3R", "HK_SHC1R"],
            "premRate": 200,
            "temporaryLoading": 0,
            "premiumNoDiscountNoLoss": "{{premium}}",
            "premiumScale": 1000,
            "premiumStdNoDiscount": "{{premium}}",
            "premiumNoDiscount": "{{premium}}",
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
            "wdPayee1PwAmount": ["{{withdrawal_amount}}"],
            "wdPayee1PwSwOpt": [""],
            "preWithwithdrawOpt": "2",
            "wdPayee1WdTo0": 138,
            "wdPayee1WdFrom0": 5,
            "wdPayee1WdAmount0": "{{withdrawal_amount}}",
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

    benefit_configurable_fields = [
        "premium",
        "withdrawal_amount",
        "bearer_token"
    ]

    benefit_field_descriptions = {
        "premium": {
            "label": "每期保费",
            "type": "number",
            "required": True,
            "default": 10000
        },
        "withdrawal_amount": {
            "label": "提取金额",
            "type": "number",
            "required": False,
            "default": 10000
        },
        "bearer_token": {
            "label": "安盛API Token",
            "type": "string",
            "required": True,
            "sensitive": True
        }
    }

    benefit_table, created = InsuranceCompanyRequest.objects.get_or_create(
        company=axa_company,
        request_name='利益表计算',
        defaults={
            'request_url': 'https://az-api.axa.com.hk/api/iprotoolkit/b2c/pos/v1/ext/proposals/illustrate',
            'request_method': 'POST',
            'request_template': benefit_table_request,
            'configurable_fields': benefit_configurable_fields,
            'field_descriptions': benefit_field_descriptions,
            'insurance_product': '盛利 II 儲蓄保險 – 至尊',
            'requires_bearer_token': True,
            'is_active': True,
            'sort_order': 1
        }
    )

    if created:
        print(f"✓ 创建利益表计算请求配置")
    else:
        print(f"✓ 利益表计算请求配置已存在")

    # 3. 添加提取金额计算请求
    withdrawal_configurable_fields = [
        "premium",
        "withdrawal_amount",
        "bearer_token"
    ]

    withdrawal_field_descriptions = {
        "premium": {
            "label": "每期保费",
            "type": "number",
            "required": True,
            "default": 10000
        },
        "withdrawal_amount": {
            "label": "提取金额",
            "type": "number",
            "required": True,
            "default": 10000
        },
        "bearer_token": {
            "label": "安盛API Token",
            "type": "string",
            "required": True,
            "sensitive": True
        }
    }

    withdrawal_calc, created = InsuranceCompanyRequest.objects.get_or_create(
        company=axa_company,
        request_name='提取金额计算',
        defaults={
            'request_url': 'https://az-api.axa.com.hk/api/iprotoolkit/b2c/pos/v1/ext/proposals/illustrate',
            'request_method': 'POST',
            'request_template': benefit_table_request,  # 使用相同的模板
            'configurable_fields': withdrawal_configurable_fields,
            'field_descriptions': withdrawal_field_descriptions,
            'insurance_product': '盛利 II 儲蓄保險 – 至尊',
            'requires_bearer_token': True,
            'is_active': True,
            'sort_order': 2
        }
    )

    if created:
        print(f"✓ 创建提取金额计算请求配置")
    else:
        print(f"✓ 提取金额计算请求配置已存在")

    print("\n数据添加完成！")
    print(f"保险公司: {axa_company.name} (ID: {axa_company.id})")
    print(f"请求配置数量: {axa_company.insurancecompanyrequest_set.count()}")

if __name__ == '__main__':
    add_axa_data()
