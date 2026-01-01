import { useState, useEffect } from 'react';
import { useAppNavigate } from '../hooks/useAppNavigate';
import { ArrowLeftIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import axios from 'axios';
import { API_BASE_URL } from '../config';

function ProductComparisonSettings() {
  const onNavigate = useAppNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [groupedProducts, setGroupedProducts] = useState([]);
  const [selectedProducts, setSelectedProducts] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProductsAndSettings();
  }, []);

  const fetchProductsAndSettings = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');

      // 获取所有产品列表（按年期分组）
      const productsResponse = await axios.get(
        `${API_BASE_URL}/api/company-comparison/products`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      // 获取用户当前的设置
      const settingsResponse = await axios.get(
        `${API_BASE_URL}/api/user/product-comparison-settings`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      setGroupedProducts(productsResponse.data.grouped_products || []);
      setSelectedProducts(settingsResponse.data.selected_products || []);
    } catch (err) {
      console.error('获取产品列表失败:', err);
      setError(err.response?.data?.message || '获取产品列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleProduct = (productId) => {
    setSelectedProducts(prev => {
      if (prev.includes(productId)) {
        return prev.filter(id => id !== productId);
      } else {
        return [...prev, productId];
      }
    });
  };

  // 计算所有产品总数
  const getTotalProductCount = () => {
    return groupedProducts.reduce((total, group) => total + group.products.length, 0);
  };

  // 获取所有产品ID列表
  const getAllProductIds = () => {
    const allIds = [];
    groupedProducts.forEach(group => {
      group.products.forEach(product => {
        allIds.push(product.id);
      });
    });
    return allIds;
  };

  const handleSelectAll = () => {
    if (selectedProducts.length === getTotalProductCount()) {
      setSelectedProducts([]);
    } else {
      setSelectedProducts(getAllProductIds());
    }
  };

  // 按年期全选/取消全选
  const handleSelectAllInPeriod = (periodProducts) => {
    const periodIds = periodProducts.map(p => p.id);
    const allSelected = periodIds.every(id => selectedProducts.includes(id));

    if (allSelected) {
      // 取消选择这个年期的所有产品
      setSelectedProducts(prev => prev.filter(id => !periodIds.includes(id)));
    } else {
      // 选择这个年期的所有产品
      setSelectedProducts(prev => {
        const newSet = new Set([...prev, ...periodIds]);
        return Array.from(newSet);
      });
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      const token = localStorage.getItem('access_token');

      await axios.post(
        `${API_BASE_URL}/api/user/product-comparison-settings`,
        { selected_products: selectedProducts },
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      alert('保存成功！');
      onNavigate('settings');
    } catch (err) {
      console.error('保存失败:', err);
      alert(err.response?.data?.message || '保存失败，请重试');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-100 via-gray-200 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-4 border-b-4 border-blue-600"></div>
          <p className="mt-4 text-gray-600 text-sm font-medium">加载中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-100 via-gray-200 to-slate-100">
        <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12 py-6">
          <button
            onClick={() => onNavigate('settings')}
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors mb-4"
          >
            <ArrowLeftIcon className="w-4 h-4" />
            <span className="text-sm font-medium">返回设置</span>
          </button>
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
            <p className="text-red-600 font-medium">{error}</p>
            <button
              onClick={fetchProductsAndSettings}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm font-medium"
            >
              重试
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 via-gray-200 to-slate-100">
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12 py-4 sm:py-6">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => onNavigate('settings')}
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors mb-4"
          >
            <ArrowLeftIcon className="w-4 h-4" />
            <span className="text-sm font-medium">返回设置</span>
          </button>

          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 drop-shadow-sm">产品对比设置</h1>
              <p className="text-sm text-gray-600 mt-1">选择您想在产品对比页面中显示的保险产品（按缴费年期分类）</p>
            </div>
            <div className="text-sm text-gray-600">
              已选择 <span className="font-bold text-blue-600">{selectedProducts.length}</span> / {getTotalProductCount()} 个产品
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="mb-4 flex gap-3">
          <button
            onClick={handleSelectAll}
            className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium shadow-sm"
          >
            {selectedProducts.length === getTotalProductCount() ? '取消全选' : '全选'}
          </button>
          <button
            onClick={() => onNavigate('company-comparison')}
            className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-colors text-sm font-medium shadow-sm"
          >
            返回对比页
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? '保存中...' : '保存设置'}
          </button>
        </div>

        {/* Products by Payment Period */}
        <div className="space-y-6">
          {groupedProducts.map((group, groupIndex) => {
            const periodIds = group.products.map(p => p.id);
            const allSelectedInPeriod = periodIds.every(id => selectedProducts.includes(id));
            const someSelectedInPeriod = periodIds.some(id => selectedProducts.includes(id)) && !allSelectedInPeriod;

            return (
              <div key={groupIndex}>
                {/* Period Header */}
                <div className="flex items-center justify-between mb-3">
                  <h2 className="text-base sm:text-lg font-bold text-gray-900 drop-shadow-sm flex items-center gap-2">
                    <div className="w-1 h-5 bg-gradient-to-b from-blue-500 to-blue-600 rounded-full"></div>
                    缴费年期：{group.payment_period} 年
                    <span className="text-sm font-normal text-gray-600">
                      ({group.products.length} 个产品)
                    </span>
                  </h2>
                  <button
                    onClick={() => handleSelectAllInPeriod(group.products)}
                    className="px-3 py-1 text-sm bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
                  >
                    {allSelectedInPeriod ? '取消全选' : someSelectedInPeriod ? '全选' : '全选'}
                  </button>
                </div>

                {/* Products Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-2">
                  {group.products.map((product) => {
                    const isSelected = selectedProducts.includes(product.id);
                    return (
                      <button
                        key={product.id}
                        onClick={() => handleToggleProduct(product.id)}
                        className={`relative p-3 rounded-lg border transition-all text-left ${
                          isSelected
                            ? 'bg-blue-50 border-blue-500 shadow-sm'
                            : 'bg-white border-gray-200 hover:border-gray-300 shadow-sm hover:shadow'
                        }`}
                      >
                        {/* Checkbox */}
                        <div className="absolute top-2 right-2">
                          {isSelected ? (
                            <CheckCircleIcon className="w-5 h-5 text-blue-600" />
                          ) : (
                            <div className="w-5 h-5 rounded-full border-2 border-gray-300"></div>
                          )}
                        </div>

                        {/* Product Info */}
                        <h3 className={`text-xs font-bold mb-1 pr-6 line-clamp-2 ${
                          isSelected ? 'text-blue-900' : 'text-gray-900'
                        }`}>
                          {product.product_name}
                        </h3>
                        <p className={`text-[10px] ${
                          isSelected ? 'text-blue-700' : 'text-gray-600'
                        }`}>
                          {product.company_name}
                        </p>
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>

        {groupedProducts.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">暂无可用的保险产品</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default ProductComparisonSettings;
