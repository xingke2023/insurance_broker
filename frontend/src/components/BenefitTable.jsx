import { useParams } from 'react-router-dom';
import { useAppNavigate } from '../hooks/useAppNavigate';
import { useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

function BenefitTable() {
  const { companyId } = useParams();
  const onNavigate = useAppNavigate();

  const [premium, setPremium] = useState('');
  const [analysisType, setAnalysisType] = useState('surrender');
  const [inputData, setInputData] = useState('');
  const [responseData, setResponseData] = useState('');
  const [loading, setLoading] = useState(false);
  const [bearerToken, setBearerToken] = useState('');

  // 公司配置信息
  const companyConfig = {
    axa: { name: '安盛', color: 'from-blue-600 to-blue-700', icon: '🏢', bgColor: 'bg-blue-50' },
  };

  const company = companyConfig[companyId] || { name: '未知公司', color: 'from-gray-600 to-gray-700', icon: '🏢', bgColor: 'bg-gray-50' };

  const handleAnalyze = async () => {
    if (!premium || !inputData || !bearerToken) {
      alert('请填写每期保费、Bearer Token和输入数据');
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
        analysis_type: analysisType,
        input_data: inputData
      };

      // 如果提供了Bearer Token，添加到请求中
      if (bearerToken) {
        requestData.bearer_token = bearerToken;
      }

      const response = await axios.post(
        `${API_BASE_URL}/api/axa/benefit/analyze`,
        requestData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.status === 'success') {
        // 格式化安盛API返回的数据
        const axaData = response.data.data;

        // 提取关键信息
        let formattedResult = `=== 安盛利益表分析结果 ===\n\n`;
        formattedResult += `分析类型: ${analysisType === 'surrender' ? '退保价值' : '身故保障'}\n`;
        formattedResult += `每期保费: ${premium} USD\n\n`;

        // 如果有利益表数据，格式化显示
        if (axaData.benefitTable) {
          formattedResult += `--- 利益表详情 ---\n`;
          formattedResult += JSON.stringify(axaData.benefitTable, null, 2);
        } else if (axaData.illustrationData) {
          formattedResult += `--- 计划书数据 ---\n`;
          formattedResult += JSON.stringify(axaData.illustrationData, null, 2);
        } else {
          // 显示完整响应
          formattedResult += `--- 完整响应数据 ---\n`;
          formattedResult += JSON.stringify(axaData, null, 2);
        }

        setResponseData(formattedResult);
      } else {
        alert(response.data.message || '分析失败');
        setResponseData('分析失败，请检查输入数据');
      }

    } catch (error) {
      console.error('分析失败:', error);

      let errorMessage = '分析失败，请重试';

      if (error.response?.data) {
        const data = error.response.data;
        errorMessage = data.message || errorMessage;

        // 如果是401错误，提示需要Bearer Token
        if (data.status_code === 401 || error.response.status === 401) {
          errorMessage = '需要安盛API的Bearer Token才能访问。请在上方输入有效的Token。';
        }

        // 显示详细错误信息
        if (data.details) {
          setResponseData(`错误 (HTTP ${data.status_code || error.response.status}):\n\n${errorMessage}\n\n详细信息:\n${data.details}`);
        } else {
          setResponseData(`错误: ${errorMessage}`);
        }
      } else if (error.message) {
        errorMessage = error.message;
        setResponseData(`错误: ${errorMessage}`);
      } else {
        setResponseData(`错误: ${errorMessage}`);
      }

      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setInputData('');
    setResponseData('');
  };

  return (
    <div className={`min-h-screen ${company.bgColor} transition-colors duration-300`}>
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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
            <div className={`w-16 h-16 bg-gradient-to-br ${company.color} rounded-2xl flex items-center justify-center shadow-lg flex-shrink-0`}>
              <span className="text-3xl">{company.icon}</span>
            </div>
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-gray-900 mb-1">{company.name} - 利益表分析</h1>
              <p className="text-sm text-gray-600">输入保险计划数据，AI智能分析利益表</p>
            </div>
          </div>
        </div>

        {/* 主内容区域 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 左侧：输入区域 */}
          <div className="bg-white rounded-2xl shadow-lg border-2 border-gray-200 overflow-hidden">
            <div className={`bg-gradient-to-r ${company.color} px-6 py-3`}>
              <h2 className="text-lg font-bold text-white">输入数据</h2>
            </div>

            <div className="p-6 space-y-4">
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
                  step="0.01"
                  className="w-full px-4 py-2.5 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-lg font-semibold"
                  placeholder="请输入每期保费"
                />
              </div>

              {/* 分析类型下拉列表 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  分析类型 <span className="text-red-500">*</span>
                </label>
                <select
                  value={analysisType}
                  onChange={(e) => setAnalysisType(e.target.value)}
                  className="w-full px-4 py-2.5 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base"
                >
                  <option value="surrender">退保价值</option>
                  <option value="death">身故保障</option>
                </select>
              </div>

              {/* Bearer Token 输入框 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  安盛API Token <span className="text-orange-500">(必填)</span>
                </label>
                <input
                  type="text"
                  value={bearerToken}
                  onChange={(e) => setBearerToken(e.target.value)}
                  className="w-full px-4 py-2.5 border-2 border-orange-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 font-mono text-xs bg-orange-50"
                  placeholder="eyJhbGciOiJSUzI1NiIsImtpZCI6..."
                />
                <p className="text-xs text-orange-600 mt-1 font-medium">
                  ⚠️ 必须提供有效的Bearer Token才能访问安盛API
                </p>
              </div>

              {/* 输入文本区域 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  输入数据 <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={inputData}
                  onChange={(e) => setInputData(e.target.value)}
                  rows={10}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono text-sm resize-none"
                  placeholder="请输入利益表数据..."
                />
                <p className="text-xs text-gray-500 mt-1">
                  提示：可以粘贴Excel表格数据或手动输入
                </p>
              </div>

              {/* 操作按钮 */}
              <div className="flex gap-3 pt-2">
                <button
                  onClick={handleClear}
                  disabled={loading}
                  className="flex-1 px-4 py-2.5 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium disabled:opacity-50"
                >
                  清空
                </button>
                <button
                  onClick={handleAnalyze}
                  disabled={loading || !premium || !inputData || !bearerToken}
                  className={`flex-1 px-4 py-2.5 bg-gradient-to-r ${company.color} text-white rounded-lg hover:shadow-lg transition-all font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2`}
                >
                  {loading ? (
                    <>
                      <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      分析中...
                    </>
                  ) : (
                    <>
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                      </svg>
                      开始分析
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* 右侧：响应区域 */}
          <div className="bg-white rounded-2xl shadow-lg border-2 border-gray-200 overflow-hidden">
            <div className={`bg-gradient-to-r ${company.color} px-6 py-3`}>
              <h2 className="text-lg font-bold text-white">分析结果</h2>
            </div>

            <div className="p-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  AI分析输出
                </label>
                <textarea
                  value={responseData}
                  readOnly
                  rows={20}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg bg-gray-50 font-mono text-sm resize-none"
                  placeholder="分析结果将显示在这里..."
                />
                {responseData && (
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(responseData);
                      alert('已复制到剪贴板');
                    }}
                    className="mt-3 w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium flex items-center justify-center gap-2"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    复制结果
                  </button>
                )}
              </div>
            </div>
          </div>
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
                <li>• 输入每期保费金额</li>
                <li>• 选择分析类型（退保价值或身故保障）</li>
                <li>• <strong>输入安盛API Bearer Token（必填）</strong></li>
                <li>• 在输入框中粘贴或输入利益表数据</li>
                <li>• 点击"开始分析"按钮，系统将调用安盛API进行分析</li>
                <li>• 分析完成后可一键复制结果</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default BenefitTable;
