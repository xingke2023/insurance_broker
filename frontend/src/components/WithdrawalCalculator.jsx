import { useParams } from 'react-router-dom';
import { useAppNavigate } from '../hooks/useAppNavigate';
import { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

function WithdrawalCalculator() {
  const { companyId } = useParams();
  const onNavigate = useAppNavigate();

  const [premium, setPremium] = useState('50000');
  const [withdrawalAmount, setWithdrawalAmount] = useState('10000');
  const [bearerToken, setBearerToken] = useState('');
  const [loading, setLoading] = useState(false);

  const [postUrl, setPostUrl] = useState('https://az-api.axa.com.hk/api/iprotoolkit/b2c/pos/v1/ext/proposals/illustrate');
  const [postRequest, setPostRequest] = useState('');
  const [responseData, setResponseData] = useState('');

  // 公司配置信息
  const companyConfig = {
    axa: { name: '安盛', color: 'from-blue-600 to-blue-700', icon: '🏢', bgColor: 'bg-blue-50' },
  };

  const company = companyConfig[companyId] || { name: '未知公司', color: 'from-gray-600 to-gray-700', icon: '🏢', bgColor: 'bg-gray-50' };

  // 生成POST Request的函数
  const generatePostRequest = (premiumValue, withdrawalValue) => {
    const today = new Date();
    const birthDate = new Date(today.getFullYear() - 35, today.getMonth(), today.getDate()).toISOString().split('T')[0];
    const insuredBirthDate = today.toISOString().split('T')[0];

    return {
      "prodCode": "HK_WEB",
      "insuredInfos": [{
        "gender": "M",
        "isSmoker": false,
        "fullName": "JACKSON",
        "dob": insuredBirthDate,
        "residency": "CN",
        "nationality": "CN",
        "occupation": "00004",
        "isCompClient": false,
        "sameAsOwnerIndex": -1,
        "age": 0,
        "occupationGroup": "NON_GAIN",
        "residencyGroup": "MCV"
      }],
      "ownerInfos": [{
        "gender": "M",
        "isSmoker": false,
        "fullName": "MIKE",
        "dob": birthDate,
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
        "premium": parseInt(premiumValue),
        "printSeq": -1,
        "yearPrem": parseInt(premiumValue),
        "halfYearPrem": parseInt(parseInt(premiumValue) * 0.52),
        "monthPrem": parseInt(parseInt(premiumValue) * 0.09),
        "sumInsured": parseInt(parseInt(premiumValue) * 5),
        "extraOptions": {},
        "paymentTermInd": "N",
        "wholePremPaymentTerm": false,
        "initialModPrem": parseInt(premiumValue),
        "premMataFemale": "",
        "premMattFemale": 5,
        "premMataMale": "",
        "premMattMale": 5,
        "minSumInsured": "10000",
        "maxSumInsured": "90000000",
        "notAllowAutoRiderList": ["HK_APF3R", "HK_SHC1R"],
        "premRate": 200,
        "temporaryLoading": 0,
        "premiumNoDiscountNoLoss": parseInt(premiumValue),
        "premiumScale": 1000,
        "premiumStdNoDiscount": parseInt(premiumValue),
        "premiumNoDiscount": parseInt(premiumValue),
        "permanentLoading": 0
      }],
      "ccy": "USD",
      "policyOptions": {
        "switchCcyOpt": "NA",
        "wdRecipient": "1",
        "wdIndicate": "periodic",
        "wdPayee1WdSwFromOpt0": null,
        "wdPayee1WdKey0": false,
        "flexiContinuationOpt": "0",
        "preFlexiContinuationOpt": "0",
        "fcoEffectiveOpt": null,
        "preFcoEffectiveOpt": null,
        "switchFromOpt": "",
        "withExtraDeathBenefit": "Y",
        "withExtraDeathBenefitCurrent": "Y",
        "swCcyFrom": "",
        "swCcyTo": "",
        "swCcyPercent": "",
        "wdFrom": "",
        "wdTo": "",
        "wdAmount": "",
        "wdSelect": true,
        "withwithdrawOpt": "2",
        "preWdIndicate": "periodic",
        "wdPayee1PwCount": [0],
        "wdPayee1PwCb": [false],
        "wdPayee1PwFrom": [5],
        "wdPayee1PwTo": [138],
        "wdPayee1PwAmount": [parseInt(withdrawalValue)],
        "wdPayee1PwSwOpt": [""],
        "preWithwithdrawOpt": "2",
        "wdPayee1WdTo0": 138,
        "wdPayee1WdFrom0": 5,
        "wdPayee1WdAmount0": parseInt(withdrawalValue),
        "wdSwFromOpt": null,
        "lockinKey": false,
        "swCcyKey": false
      },
      "paymentMode": "A",
      "reportOptions": {},
      "custom": {
        "ppsNo": "PPS0002614192",
        "ppsNoDisp": "AA077253-0002614192-1",
        "occupationQuestionsAns": {},
        "pOccupationQuestionsAns": {},
        "recAgentName": null,
        "isQuickQuote": true,
        "skipSTEPolicyNumber": false,
        "hasPremiumHoliday": false,
        "agtCnaBasicPlanListStr": ";WEB05;WEB10;WEBB05;WEBB10;",
        "agtCnaRiderPlanListStr": ";AP;APF3R;APFR;CAP1;CAP2;",
        "agentCodeProposal": "000000-05-077253",
        "agentFax": "",
        "agentDealerGroup": "BK",
        "isNewOccupation": true
      },
      "isBackDate": "N",
      "campaignYesNoSectionValue": "N",
      "originalPlanDetail": {},
      "compCode": "AXAHK",
      "skipParamsPrefill": true
    };
  };

  // 页面加载时和参数改变时更新POST Request
  useEffect(() => {
    const request = generatePostRequest(premium, withdrawalAmount);
    setPostRequest(JSON.stringify(request, null, 2));
  }, [premium, withdrawalAmount]);

  const handleCalculate = async () => {
    if (!premium || !withdrawalAmount || !bearerToken) {
      alert('请填写所有必填项');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        alert('请先登录');
        setLoading(false);
        return;
      }

      // 调用后端API
      const requestData = {
        premium: premium,
        withdrawal_amount: withdrawalAmount,
        bearer_token: bearerToken
      };

      const response = await axios.post(
        `${API_BASE_URL}/api/axa/withdrawal/calculate`,
        requestData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.status === 'success') {
        // 显示POST URL
        setPostUrl(response.data.post_url || 'https://az-api.axa.com.hk/api/iprotoolkit/b2c/pos/v1/ext/proposals/illustrate');

        // 显示POST Request (格式化JSON)
        setPostRequest(JSON.stringify(response.data.post_request, null, 2));

        // 显示响应结果 (格式化JSON)
        setResponseData(JSON.stringify(response.data.data, null, 2));
      } else {
        alert(response.data.message || '计算失败');
        setResponseData(`错误: ${response.data.message}`);
      }

    } catch (error) {
      console.error('计算失败:', error);

      let errorMessage = '计算失败，请重试';
      if (error.response?.data) {
        const data = error.response.data;
        errorMessage = data.message || errorMessage;

        if (data.post_url) setPostUrl(data.post_url);
        if (data.post_request) setPostRequest(JSON.stringify(data.post_request, null, 2));

        if (data.details) {
          setResponseData(`错误 (HTTP ${data.status_code || error.response.status}):\n\n${errorMessage}\n\n详细信息:\n${data.details}`);
        } else {
          setResponseData(`错误: ${errorMessage}`);
        }
      } else if (error.message) {
        errorMessage = error.message;
        setResponseData(`错误: ${errorMessage}`);
      }

      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setPostUrl('');
    setPostRequest('');
    setResponseData('');
  };

  const copyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text);
    alert(`${label}已复制到剪贴板`);
  };

  return (
    <div className={`min-h-screen ${company.bgColor} transition-colors duration-300`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 页头 */}
        <div className="mb-6">
          <button
            onClick={() => onNavigate(`/plan-builder/${companyId}`)}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-900 transition-colors mb-4"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            返回计划书制作
          </button>

          <div className="flex items-center gap-6 bg-white rounded-2xl shadow-lg p-6 border-2 border-gray-200">
            <div className={`w-16 h-16 bg-gradient-to-br from-green-600 to-emerald-600 rounded-2xl flex items-center justify-center shadow-lg flex-shrink-0`}>
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-gray-900 mb-1">{company.name} - 提取金额计算</h1>
              <p className="text-sm text-gray-600">计算不同提取金额下的保单价值</p>
            </div>
          </div>
        </div>

        {/* 输入区域 */}
        <div className="bg-white rounded-2xl shadow-lg border-2 border-gray-200 overflow-hidden mb-6">
          <div className={`bg-gradient-to-r from-green-600 to-emerald-600 px-6 py-3`}>
            <h2 className="text-lg font-bold text-white">计算参数</h2>
          </div>

          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* 每期保费 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  每期保费 (USD) <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  value={premium}
                  onChange={(e) => setPremium(e.target.value)}
                  min="0"
                  step="1000"
                  className="w-full px-4 py-2.5 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 text-base font-semibold"
                  placeholder="50000"
                />
              </div>

              {/* 提取金额 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  提取金额 (USD) <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  value={withdrawalAmount}
                  onChange={(e) => setWithdrawalAmount(e.target.value)}
                  min="0"
                  step="1000"
                  className="w-full px-4 py-2.5 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 text-base font-semibold"
                  placeholder="10000"
                />
              </div>

              {/* Bearer Token */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  安盛API Token <span className="text-orange-500">(必填)</span>
                </label>
                <input
                  type="text"
                  value={bearerToken}
                  onChange={(e) => setBearerToken(e.target.value)}
                  className="w-full px-4 py-2.5 border-2 border-orange-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 font-mono text-xs bg-orange-50"
                  placeholder="eyJhbGciOiJSUzI1NiIs..."
                />
              </div>
            </div>

            {/* 操作按钮 */}
            <div className="flex gap-3 mt-6">
              <button
                onClick={handleClear}
                disabled={loading}
                className="flex-1 px-4 py-2.5 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium disabled:opacity-50"
              >
                清空结果
              </button>
              <button
                onClick={handleCalculate}
                disabled={loading || !premium || !withdrawalAmount || !bearerToken}
                className="flex-1 px-4 py-2.5 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:shadow-lg transition-all font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    计算中...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                    开始计算
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* 结果展示区域 */}
        <div className="grid grid-cols-1 gap-6">
          {/* POST URL */}
          <div className="bg-white rounded-2xl shadow-lg border-2 border-gray-200 overflow-hidden">
              <div className="bg-gradient-to-r from-purple-600 to-purple-700 px-6 py-3 flex items-center justify-between">
                <h2 className="text-lg font-bold text-white">POST URL</h2>
                <button
                  onClick={() => copyToClipboard(postUrl, 'POST URL')}
                  className="px-3 py-1.5 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg text-white text-sm font-medium transition-all flex items-center gap-1.5"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  复制
                </button>
              </div>
              <div className="p-6">
                <code className="block p-4 bg-gray-50 rounded-lg border border-gray-200 text-sm font-mono text-purple-700 break-all">
                  {postUrl}
                </code>
              </div>
            </div>

          {/* POST Request */}
          <div className="bg-white rounded-2xl shadow-lg border-2 border-gray-200 overflow-hidden">
              <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-3 flex items-center justify-between">
                <h2 className="text-lg font-bold text-white">POST Request</h2>
                <button
                  onClick={() => copyToClipboard(postRequest, 'POST Request')}
                  className="px-3 py-1.5 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg text-white text-sm font-medium transition-all flex items-center gap-1.5"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  复制
                </button>
              </div>
              <div className="p-6">
                <pre className="p-4 bg-gray-50 rounded-lg border border-gray-200 text-xs font-mono overflow-x-auto max-h-96 overflow-y-auto">
                  {postRequest}
                </pre>
              </div>
            </div>

          {/* Response Result */}
          {responseData && (
            <div className="bg-white rounded-2xl shadow-lg border-2 border-gray-200 overflow-hidden">
              <div className="bg-gradient-to-r from-green-600 to-emerald-600 px-6 py-3 flex items-center justify-between">
                <h2 className="text-lg font-bold text-white">Response Result</h2>
                <button
                  onClick={() => copyToClipboard(responseData, 'Response Result')}
                  className="px-3 py-1.5 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg text-white text-sm font-medium transition-all flex items-center gap-1.5"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  复制
                </button>
              </div>
              <div className="p-6">
                <pre className="p-4 bg-gray-50 rounded-lg border border-gray-200 text-xs font-mono overflow-x-auto max-h-96 overflow-y-auto">
                  {responseData}
                </pre>
              </div>
            </div>
          )}
        </div>

        {/* 使用说明 */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <svg className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            <div>
              <h4 className="text-sm font-semibold text-blue-900 mb-1">使用说明</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• <strong>POST URL 和 POST Request 会根据输入参数实时更新</strong></li>
                <li>• 修改保费或提取金额会自动更新POST Request</li>
                <li>• 输入安盛API Bearer Token（必填）</li>
                <li>• 点击"开始计算"按钮获取Response Result</li>
                <li>• 可一键复制每个部分的内容</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default WithdrawalCalculator;
