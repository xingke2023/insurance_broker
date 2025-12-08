import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import { ArrowLeftIcon, ClipboardDocumentIcon, CheckIcon } from '@heroicons/react/24/outline';

function ApiCallPage() {
  const { companyCode, requestName } = useParams();
  const navigate = useNavigate();

  const [requestConfig, setRequestConfig] = useState(null);
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);

  const [copiedPost, setCopiedPost] = useState(false);
  const [copiedUrl, setCopiedUrl] = useState(false);
  const [copiedHeaders, setCopiedHeaders] = useState(false);
  const [copiedResponse, setCopiedResponse] = useState(false);

  const [editableRequestBody, setEditableRequestBody] = useState('');
  const [editableHeaders, setEditableHeaders] = useState('');

  useEffect(() => {
    fetchRequestConfig();
  }, [companyCode, requestName]);

  // 当requestConfig或formData变化时，更新可编辑内容
  useEffect(() => {
    if (requestConfig) {
      setEditableRequestBody(generatePostRequest());
      setEditableHeaders(generateHttpHeaders());
    }
  }, [requestConfig, formData]);

  const fetchRequestConfig = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');

      const response = await axios.get(
        `${API_BASE_URL}/api/insurance-companies/${companyCode}/requests/${encodeURIComponent(requestName)}/`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.data.status === 'success') {
        const config = response.data.data;
        console.log('📥 收到API配置:', config);
        console.log('📋 Headers配置:', config.headers);
        console.log('📋 Headers类型:', typeof config.headers);
        setRequestConfig(config);

        // 初始化表单数据（使用默认值）
        const initialFormData = {};
        config.configurable_fields.forEach(fieldName => {
          const fieldDesc = config.field_descriptions[fieldName];
          if (fieldDesc && fieldDesc.default !== undefined) {
            initialFormData[fieldName] = fieldDesc.default;
          } else {
            initialFormData[fieldName] = '';
          }
        });
        setFormData(initialFormData);
      }
    } catch (err) {
      console.error('获取请求配置失败:', err);
      setError('加载失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (fieldName, value) => {
    // 对于敏感字段，不要trim，保持原样
    setFormData(prev => ({
      ...prev,
      [fieldName]: value
    }));

    // 调试：如果是bearer_token，输出详细信息
    if (fieldName === 'bearer_token') {
      console.log('📝 Bearer Token输入变化:');
      console.log('  ========================================');
      console.log('  原始输入长度:', value.length);
      console.log('  前50字符:', value.substring(0, 50));
      console.log('  后50字符:', value.substring(Math.max(0, value.length - 50)));
      console.log('  ========================================');
      console.log('  Trim后长度:', value.trim().length);
      console.log('  是否包含"Bearer "前缀:', value.trim().startsWith('Bearer '));

      // 模拟实际处理逻辑
      const trimmedToken = value.trim();
      const finalAuthHeader = trimmedToken.startsWith('Bearer ') ? trimmedToken : `Bearer ${trimmedToken}`;
      console.log('  ========================================');
      console.log('  最终Authorization长度:', finalAuthHeader.length);
      console.log('  最终Authorization前50:', finalAuthHeader.substring(0, 50));
      console.log('  最终Authorization后50:', finalAuthHeader.substring(Math.max(0, finalAuthHeader.length - 50)));
      console.log('  ========================================');

      // 检查是否有不可见字符
      const hasInvisibleChars = /[\r\n\t]/.test(value);
      if (hasInvisibleChars) {
        console.warn('⚠️  警告：检测到不可见字符（换行符/制表符），这些会被trim()去除！');
      }
    }
  };

  const generatePostRequest = () => {
    if (!requestConfig) return '';

    // 深拷贝模板
    let requestBody = JSON.parse(JSON.stringify(requestConfig.request_template));

    // 递归替换占位符（注意：bearer_token等敏感字段不会在body中，会在header中）
    const replacePlaceholders = (obj) => {
      if (typeof obj === 'string') {
        // 替换 {{变量名}}
        return obj.replace(/\{\{(\w+)\}\}/g, (match, fieldName) => {
          // 跳过bearer_token等header字段
          if (fieldName === 'bearer_token') {
            return match; // 保持占位符不变
          }
          const value = formData[fieldName];
          return value !== undefined ? value : match;
        });
      } else if (Array.isArray(obj)) {
        return obj.map(item => replacePlaceholders(item));
      } else if (typeof obj === 'object' && obj !== null) {
        const newObj = {};
        for (const key in obj) {
          newObj[key] = replacePlaceholders(obj[key]);
        }
        return newObj;
      }
      return obj;
    };

    requestBody = replacePlaceholders(requestBody);
    return JSON.stringify(requestBody, null, 2);
  };

  const generateHttpHeaders = () => {
    // 从 insurance_company_requests 表读取基础headers（不包含Authorization）
    console.log('🔍 generateHttpHeaders 调用');
    console.log('  - requestConfig存在:', !!requestConfig);
    console.log('  - requestConfig.headers:', requestConfig?.headers);
    console.log('  - requestConfig.headers类型:', typeof requestConfig?.headers);

    const headers = requestConfig?.headers ? { ...requestConfig.headers } : {};
    console.log('  - 初始化后的headers:', headers);

    // Authorization优先级：用户输入 > insurance_companies表
    if (formData.bearer_token) {
      // 优先使用用户输入的Bearer Token
      console.log('📋 [使用用户输入的Bearer Token]');
      const token = formData.bearer_token.trim();
      const authValue = token.startsWith('Bearer ') ? token : `Bearer ${token}`;
      headers['Authorization'] = authValue;
      console.log('  - Authorization长度:', authValue.length);
    } else if (requestConfig?.company?.bearer_token) {
      // 如果用户没有输入，使用 insurance_companies 表的 bearer_token
      console.log('📋 [使用数据库配置的Bearer Token (insurance_companies表)]');
      const dbToken = requestConfig.company.bearer_token.trim();
      const authValue = dbToken.startsWith('Bearer ') ? dbToken : `Bearer ${dbToken}`;
      headers['Authorization'] = authValue;
      console.log('  - Authorization长度:', authValue.length);
    }

    // Cookie从 insurance_companies 表获取
    if (requestConfig?.company?.cookie) {
      headers['Cookie'] = requestConfig.company.cookie;
    }

    return JSON.stringify(headers, null, 2);
  };

  const getAuthHeaderLength = () => {
    if (!formData.bearer_token) return 0;
    const token = formData.bearer_token.trim();
    const authValue = token.startsWith('Bearer ') ? token : `Bearer ${token}`;
    console.log('📏 计算Authorization长度:', authValue.length);
    return authValue.length;
  };

  const handleExecute = async () => {
    try {
      setExecuting(true);
      setError(null);
      setResponse(null);

      // 验证必填字段
      const requiredFields = requestConfig.configurable_fields.filter(fieldName => {
        const fieldDesc = requestConfig.field_descriptions[fieldName];
        return fieldDesc && fieldDesc.required;
      });

      for (const fieldName of requiredFields) {
        if (!formData[fieldName]) {
          const fieldDesc = requestConfig.field_descriptions[fieldName];
          alert(`请填写${fieldDesc.label || fieldName}`);
          return;
        }
      }

      // 获取用户JWT Token
      const token = localStorage.getItem('access_token');

      console.log('📤 调用后端代理接口');
      console.log('📦 可编辑Request Body:', editableRequestBody);
      console.log('📦 可编辑Headers:', editableHeaders);

      // 解析可编辑的request body和headers
      let parsedRequestBody = {};
      let parsedHeaders = {};

      try {
        parsedRequestBody = JSON.parse(editableRequestBody);
      } catch (e) {
        alert('Request Body格式错误，请检查JSON格式');
        return;
      }

      try {
        parsedHeaders = JSON.parse(editableHeaders);
      } catch (e) {
        alert('HTTP Headers格式错误，请检查JSON格式');
        return;
      }

      // 调用后端代理接口
      const apiResponse = await axios.post(
        `${API_BASE_URL}/api/insurance-companies/${companyCode}/requests/${encodeURIComponent(requestName)}/execute`,
        {
          request_body: parsedRequestBody,  // 直接传递编辑后的request body
          custom_headers: parsedHeaders,     // 传递编辑后的headers
          custom_bearer_token: parsedHeaders['Authorization'] || ''  // 从headers中提取Bearer Token
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      console.log('✅ 后端响应:', apiResponse.data);

      // 后端返回格式：{ status: 'success', request_info: {...}, response_info: {...} }
      if (apiResponse.data.status === 'success') {
        setResponse(apiResponse.data.response_info.body);
      } else {
        setError(apiResponse.data.message || '请求失败');
      }
    } catch (err) {
      console.error('❌ API调用失败:', err);
      setError(err.response?.data?.message || err.message || '请求失败');
    } finally {
      setExecuting(false);
    }
  };

  const copyToClipboard = async (text, setCopied) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('复制失败:', err);
    }
  };

  const renderFormField = (fieldName) => {
    const fieldDesc = requestConfig.field_descriptions[fieldName] || {};
    const label = fieldDesc.label || fieldName;
    const type = fieldDesc.type || 'string';
    const required = fieldDesc.required || false;
    const sensitive = fieldDesc.sensitive || false;

    const inputClassName = sensitive
      ? 'w-full px-3 py-2 border-2 border-orange-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent bg-orange-50 font-mono text-sm'
      : 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent';

    const currentValue = formData[fieldName] || '';

    return (
      <div key={fieldName} className={sensitive ? 'col-span-2' : ''}>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
          {sensitive && <span className="text-orange-500 ml-2 text-xs">(敏感字段)</span>}
          {sensitive && currentValue && (
            <span className="float-right text-xs text-gray-500">
              {currentValue.length} 个字符
            </span>
          )}
        </label>
        {type === 'number' ? (
          <input
            type="number"
            value={currentValue}
            onChange={(e) => handleInputChange(fieldName, e.target.value)}
            className={inputClassName}
            placeholder={`请输入${label}`}
          />
        ) : sensitive ? (
          <>
            <textarea
              value={currentValue}
              onChange={(e) => handleInputChange(fieldName, e.target.value)}
              className={inputClassName}
              placeholder={`请输入${label}`}
              rows={4}
              style={{ resize: 'vertical' }}
              maxLength={5000}
            />
            {currentValue && (
              <div className="mt-1 space-y-1">
                <div className="text-xs text-gray-600">
                  {currentValue.startsWith('Bearer ') ? (
                    <span className="text-green-600">✓ 包含 Bearer 前缀</span>
                  ) : (
                    <span className="text-orange-600">ℹ️ 将自动添加 Bearer 前缀</span>
                  )}
                </div>
                {/* 长度警告 */}
                {currentValue.length < 200 && (
                  <div className="text-xs text-red-600 bg-red-50 p-2 rounded">
                    ⚠️ 警告：Token长度仅{currentValue.length}字符，可能不完整！标准JWT Token通常为200-1200字符。
                  </div>
                )}
                {currentValue.length >= 1000 && (
                  <div className="text-xs text-green-600 bg-green-50 p-2 rounded">
                    ✓ Token长度正常（{currentValue.length}字符）
                  </div>
                )}
              </div>
            )}
          </>
        ) : (
          <input
            type="text"
            value={currentValue}
            onChange={(e) => handleInputChange(fieldName, e.target.value)}
            className={inputClassName}
            placeholder={`请输入${label}`}
          />
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

  if (error && !requestConfig) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={() => navigate(-1)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            返回
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* 顶部导航栏 */}
      <div className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <button
              onClick={() => navigate(-1)}
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <ArrowLeftIcon className="h-5 w-5" />
              <span>返回</span>
            </button>
            <h1 className="text-xl font-bold text-gray-900">{requestConfig?.request_name}</h1>
            <div className="w-20"></div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 左侧：输入区域 */}
          <div className="space-y-6">
            {/* 表单卡片 */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">配置参数</h2>
              <div className="grid grid-cols-2 gap-4">
                {requestConfig?.configurable_fields.map(fieldName => renderFormField(fieldName))}
              </div>

              <button
                onClick={handleExecute}
                disabled={executing}
                className="w-full mt-6 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors font-medium"
              >
                {executing ? '执行中...' : '开始执行'}
              </button>
            </div>

            {/* POST URL */}
            <div className="bg-blue-50 rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-bold text-gray-900">POST URL</h3>
                <button
                  onClick={() => copyToClipboard(requestConfig?.request_url, setCopiedUrl)}
                  className="flex items-center space-x-1 text-blue-600 hover:text-blue-700"
                >
                  {copiedUrl ? (
                    <>
                      <CheckIcon className="h-5 w-5" />
                      <span className="text-sm">已复制</span>
                    </>
                  ) : (
                    <>
                      <ClipboardDocumentIcon className="h-5 w-5" />
                      <span className="text-sm">复制</span>
                    </>
                  )}
                </button>
              </div>
              <div className="bg-white rounded-lg p-4 font-mono text-sm break-all">
                {requestConfig?.request_url}
              </div>
            </div>

            {/* POST Request */}
            <div className="bg-green-50 rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-bold text-gray-900">POST Request Body (可编辑)</h3>
                <button
                  onClick={() => copyToClipboard(editableRequestBody, setCopiedPost)}
                  className="flex items-center space-x-1 text-green-600 hover:text-green-700"
                >
                  {copiedPost ? (
                    <>
                      <CheckIcon className="h-5 w-5" />
                      <span className="text-sm">已复制</span>
                    </>
                  ) : (
                    <>
                      <ClipboardDocumentIcon className="h-5 w-5" />
                      <span className="text-sm">复制</span>
                    </>
                  )}
                </button>
              </div>
              <textarea
                value={editableRequestBody}
                onChange={(e) => setEditableRequestBody(e.target.value)}
                className="w-full bg-white rounded-lg p-4 font-mono text-xs overflow-auto min-h-96 border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-colors"
                spellCheck={false}
              />
            </div>

            {/* HTTP Headers - 始终显示 */}
            <div className="bg-orange-50 rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-bold text-gray-900">
                  HTTP Headers (可编辑)
                  {(formData.bearer_token || requestConfig?.company?.bearer_token) && (
                    <span className="text-sm font-normal text-orange-600 ml-2">
                      (包含认证信息)
                    </span>
                  )}
                </h3>
                <button
                  onClick={() => copyToClipboard(editableHeaders, setCopiedHeaders)}
                  className="flex items-center space-x-1 text-orange-600 hover:text-orange-700"
                >
                  {copiedHeaders ? (
                    <>
                      <CheckIcon className="h-5 w-5" />
                      <span className="text-sm">已复制</span>
                    </>
                  ) : (
                    <>
                      <ClipboardDocumentIcon className="h-5 w-5" />
                      <span className="text-sm">复制</span>
                    </>
                  )}
                </button>
              </div>
              <textarea
                value={editableHeaders}
                onChange={(e) => setEditableHeaders(e.target.value)}
                className="w-full bg-white rounded-lg p-4 font-mono text-xs overflow-auto min-h-64 border border-gray-300 focus:border-orange-500 focus:ring-2 focus:ring-orange-200 transition-colors"
                spellCheck={false}
              />
              {(formData.bearer_token || requestConfig?.company?.bearer_token) && (
                <div className="mt-3 p-3 bg-orange-100 rounded-lg space-y-2">
                  <p className="text-xs text-orange-800">
                    💡 <strong>提示：</strong>Bearer Token会通过HTTP Header的Authorization字段发送，不会出现在Request Body中。
                  </p>
                  {formData.bearer_token && (
                    <>
                      <div className="flex items-center justify-between">
                        <p className="text-xs text-orange-700 font-mono">
                          📏 Authorization Header 长度: <strong className="text-lg">{getAuthHeaderLength()}</strong> 个字符
                        </p>
                        {getAuthHeaderLength() < 200 && (
                          <span className="text-xs text-red-600 font-bold">⚠️ 可能不完整</span>
                        )}
                        {getAuthHeaderLength() >= 1000 && getAuthHeaderLength() < 1100 && (
                          <span className="text-xs text-green-600 font-bold">✓ 长度正常</span>
                        )}
                      </div>
                      {getAuthHeaderLength() > 0 && getAuthHeaderLength() !== 1062 && (
                        <p className="text-xs text-blue-700">
                          ℹ️ 您提到应该是1062个字符，当前是{getAuthHeaderLength()}个字符
                        </p>
                      )}
                    </>
                  )}
                  {!formData.bearer_token && requestConfig?.company?.bearer_token && (
                    <p className="text-xs text-green-700">
                      ✓ 使用数据库配置的Bearer Token（来自保险公司配置）
                    </p>
                  )}
                </div>
              )}
              {requestConfig?.company?.cookie && (
                <div className="mt-3 p-3 bg-blue-100 rounded-lg">
                  <p className="text-xs text-blue-800">
                    🍪 <strong>Cookie:</strong> 已包含数据库配置的Cookie（{requestConfig.company.cookie.length} 个字符）
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* 右侧：响应区域 */}
          <div>
            <div className="bg-purple-50 rounded-xl shadow-lg p-6 sticky top-24">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-bold text-gray-900">Response 响应</h3>
                {response && (
                  <button
                    onClick={() => copyToClipboard(JSON.stringify(response, null, 2), setCopiedResponse)}
                    className="flex items-center space-x-1 text-purple-600 hover:text-purple-700"
                  >
                    {copiedResponse ? (
                      <>
                        <CheckIcon className="h-5 w-5" />
                        <span className="text-sm">已复制</span>
                      </>
                    ) : (
                      <>
                        <ClipboardDocumentIcon className="h-5 w-5" />
                        <span className="text-sm">复制</span>
                      </>
                    )}
                  </button>
                )}
              </div>

              <div className="bg-white rounded-lg p-4">
                {executing ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
                  </div>
                ) : response ? (
                  <pre className="font-mono text-xs overflow-auto max-h-[600px] whitespace-pre-wrap break-words">
                    {JSON.stringify(response, null, 2)}
                  </pre>
                ) : error ? (
                  <div className="text-red-600 py-4">
                    <p className="font-medium mb-2">❌ 请求失败</p>
                    <pre className="text-xs bg-red-50 rounded p-3 overflow-auto">
                      {typeof error === 'string' ? error : JSON.stringify(error, null, 2)}
                    </pre>
                  </div>
                ) : (
                  <p className="text-gray-400 text-center py-12">
                    点击"开始执行"按钮发送请求
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ApiCallPage;
