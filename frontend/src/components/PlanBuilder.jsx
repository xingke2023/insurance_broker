import { useState, useEffect } from 'react';
import { useAppNavigate } from '../hooks/useAppNavigate';
import { BuildingOffice2Icon } from '@heroicons/react/24/outline';
import axios from 'axios';
import { API_BASE_URL } from '../config';

function PlanBuilder() {
  const onNavigate = useAppNavigate();
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCompanies();
  }, []);

  const fetchCompanies = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(
        `${API_BASE_URL}/api/insurance-companies/`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.data.status === 'success') {
        setCompanies(response.data.data);
      }
    } catch (error) {
      console.error('获取保险公司列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 页头 */}
        <div className="mb-8">
          <button
            onClick={() => onNavigate('dashboard')}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-900 transition-colors mb-4"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            返回Dashboard
          </button>

          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl shadow-lg mb-4">
              <BuildingOffice2Icon className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">计划书制作</h1>
            <p className="text-gray-600">选择保险公司查看可用的API接口</p>
          </div>
        </div>

        {/* 公司卡片网格 */}
        {companies.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-xl p-12 text-center">
            <p className="text-gray-500 text-lg">暂无保险公司数据</p>
            <p className="text-gray-400 text-sm mt-2">请联系管理员添加保险公司</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {companies.map((company) => (
              <button
                key={company.code}
                onClick={() => onNavigate(`insurance-company/${company.code}`)}
                className="group bg-white border-2 border-gray-200 rounded-2xl p-8 hover:border-blue-400 hover:shadow-2xl transition-all duration-300 transform hover:scale-105 relative overflow-hidden"
              >
                {/* 渐变背景 */}
                <div className={`absolute inset-0 bg-gradient-to-br ${company.color_gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-300`}></div>

                {/* 内容 */}
                <div className="relative z-10">
                  {/* 图标 */}
                  <div className="flex items-center justify-center mb-4">
                    <div className={`w-20 h-20 bg-gradient-to-br ${company.color_gradient} rounded-2xl flex items-center justify-center shadow-lg group-hover:shadow-2xl transition-all duration-300 transform group-hover:rotate-6`}>
                      <span className="text-4xl">{company.icon}</span>
                    </div>
                  </div>

                  {/* 公司名称 */}
                  <h3 className="text-2xl font-bold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
                    {company.name}
                  </h3>

                  {/* 英文名称 */}
                  <p className="text-sm text-gray-500 mb-4">
                    {company.name_en}
                  </p>

                  {/* 箭头图标 */}
                  <div className="flex items-center justify-center text-gray-400 group-hover:text-blue-600 transition-colors">
                    <svg className="w-6 h-6 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </div>
                </div>

                {/* 装饰性元素 */}
                <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-100 to-transparent rounded-bl-full opacity-0 group-hover:opacity-50 transition-opacity duration-300"></div>
              </button>
            ))}
          </div>
        )}

        {/* 底部提示 */}
        <div className="mt-12 text-center">
          <div className="inline-flex items-center gap-2 px-6 py-3 bg-white border border-blue-200 rounded-full shadow-sm">
            <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            <span className="text-sm text-gray-700">共支持 <span className="font-bold text-blue-600">{companies.length}</span> 家保险公司</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PlanBuilder;
