import { useParams } from 'react-router-dom';
import { useAppNavigate } from '../hooks/useAppNavigate';
import { useState } from 'react';

function CompanyPlanBuilder() {
  const { companyId } = useParams();
  const onNavigate = useAppNavigate();
  const [formData, setFormData] = useState({
    clientName: 'Mike',
    clientAge: '0',
    clientGender: 'male',
    productName: '储蓄',
    premium: '',
    paymentYears: '5',
    insuredAmount: '',
    insurancePeriod: '100',
  });

  // 公司配置信息
  const companyConfig = {
    prudential: { name: '保诚', color: 'from-red-600 to-red-700', icon: '🏛️', bgColor: 'bg-red-50' },
    manulife: { name: '宏利', color: 'from-green-600 to-green-700', icon: '🌳', bgColor: 'bg-green-50' },
    sunlife: { name: '永明', color: 'from-yellow-600 to-orange-600', icon: '☀️', bgColor: 'bg-yellow-50' },
    axa: { name: '安盛', color: 'from-blue-600 to-blue-700', icon: '🏢', bgColor: 'bg-blue-50' },
    boc: { name: '中银', color: 'from-red-700 to-red-800', icon: '🏦', bgColor: 'bg-red-50' },
    chinalife: { name: '国寿', color: 'from-red-600 to-orange-600', icon: '🇨🇳', bgColor: 'bg-orange-50' },
    ctf: { name: '周大福', color: 'from-yellow-600 to-yellow-700', icon: '💎', bgColor: 'bg-yellow-50' },
    ftlife: { name: '富通', color: 'from-blue-700 to-indigo-700', icon: '💼', bgColor: 'bg-indigo-50' },
    fwd: { name: '富卫', color: 'from-orange-600 to-red-600', icon: '🛡️', bgColor: 'bg-orange-50' },
    regent: { name: '立桥', color: 'from-purple-600 to-purple-700', icon: '🌉', bgColor: 'bg-purple-50' },
    aia: { name: '友邦', color: 'from-teal-600 to-teal-700', icon: '🤝', bgColor: 'bg-teal-50' },
  };

  const company = companyConfig[companyId] || { name: '未知公司', color: 'from-gray-600 to-gray-700', icon: '🏢', bgColor: 'bg-gray-50' };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: 实现计划书生成逻辑
    console.log('生成计划书:', { company: company.name, ...formData });
    alert(`正在为 ${company.name} 生成计划书...\n此功能开发中`);
  };

  return (
    <div className={`min-h-screen ${company.bgColor} transition-colors duration-300`}>
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 页头 */}
        <div className="mb-8">
          <button
            onClick={() => onNavigate('/plan-builder')}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-900 transition-colors mb-6"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            返回选择公司
          </button>

          <div className="flex items-center gap-6 bg-white rounded-2xl shadow-lg p-6 border-2 border-gray-200">
            <div className={`w-20 h-20 bg-gradient-to-br ${company.color} rounded-2xl flex items-center justify-center shadow-lg flex-shrink-0`}>
              <span className="text-4xl">{company.icon}</span>
            </div>
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{company.name}</h1>
              <p className="text-gray-600">保险计划书制作</p>
            </div>
            {/* 安盛专属功能按钮 */}
            {companyId === 'axa' && (
              <div className="flex gap-3">
                <button
                  onClick={() => onNavigate(`/benefit-table/${companyId}`)}
                  className={`px-5 py-2.5 bg-gradient-to-r ${company.color} text-white rounded-lg hover:shadow-lg transition-all font-medium flex items-center gap-2 text-sm`}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  利益表
                </button>
                <button
                  onClick={() => onNavigate(`/withdrawal-calculator/${companyId}`)}
                  className={`px-5 py-2.5 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:shadow-lg transition-all font-medium flex items-center gap-2 text-sm`}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  提取金额计算
                </button>
              </div>
            )}
          </div>
        </div>

        {/* 表单 */}
        <div className="bg-white rounded-2xl shadow-lg border-2 border-gray-200 overflow-hidden">
          <div className={`bg-gradient-to-r ${company.color} px-6 py-4`}>
            <h2 className="text-xl font-bold text-white">基本信息</h2>
          </div>

          <form onSubmit={handleSubmit} className="p-4 space-y-4">
            {/* 第一行：基本信息（已有默认值） */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  客户姓名
                </label>
                <input
                  type="text"
                  name="clientName"
                  value={formData.clientName}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  年龄
                </label>
                <input
                  type="number"
                  name="clientAge"
                  value={formData.clientAge}
                  onChange={handleInputChange}
                  required
                  min="0"
                  max="120"
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  性别
                </label>
                <select
                  name="clientGender"
                  value={formData.clientGender}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="male">男</option>
                  <option value="female">女</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  产品名称
                </label>
                <input
                  type="text"
                  name="productName"
                  value={formData.productName}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            {/* 第二行：需要填写的重要字段 */}
            <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-2">
                <svg className="w-4 h-4 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                <span className="text-xs font-semibold text-yellow-800">请填写以下重要信息</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    年缴保费 (USD) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    name="premium"
                    value={formData.premium}
                    onChange={handleInputChange}
                    required
                    min="0"
                    step="0.01"
                    className="w-full px-3 py-2 text-sm border-2 border-yellow-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500 bg-white"
                    placeholder="请输入年缴保费"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    基本保额 (USD) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    name="insuredAmount"
                    value={formData.insuredAmount}
                    onChange={handleInputChange}
                    required
                    min="0"
                    step="0.01"
                    className="w-full px-3 py-2 text-sm border-2 border-yellow-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500 bg-white"
                    placeholder="请输入基本保额"
                  />
                </div>
              </div>
            </div>

            {/* 第三行：其他信息（已有默认值） */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  缴费年期
                </label>
                <input
                  type="number"
                  name="paymentYears"
                  value={formData.paymentYears}
                  onChange={handleInputChange}
                  required
                  min="1"
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  保险期限
                </label>
                <input
                  type="text"
                  name="insurancePeriod"
                  value={formData.insurancePeriod}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            {/* 提交按钮 */}
            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={() => onNavigate('/plan-builder')}
                className="flex-1 px-4 py-2 text-sm border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
              >
                取消
              </button>
              <button
                type="submit"
                className={`flex-1 px-4 py-2 text-sm bg-gradient-to-r ${company.color} text-white rounded-lg hover:shadow-lg transition-all font-medium transform hover:scale-105`}
              >
                生成计划书
              </button>
            </div>
          </form>
        </div>

        {/* 功能说明 */}
        <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-3">
          <div className="flex items-start gap-2">
            <svg className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            <div>
              <h4 className="text-xs font-semibold text-blue-900 mb-0.5">功能说明</h4>
              <p className="text-xs text-blue-800">
                填写完整信息后，系统将自动生成专业的保险计划书。
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CompanyPlanBuilder;
