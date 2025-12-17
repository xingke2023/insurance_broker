import { useState, useEffect } from 'react';
import { useAppNavigate } from '../hooks/useAppNavigate';
import { CheckIcon } from '@heroicons/react/24/outline';
import axios from 'axios';
import { API_BASE_URL } from '../config';

function MembershipPlans() {
  const onNavigate = useAppNavigate();
  const [loading, setLoading] = useState(false);
  const [teamSize, setTeamSize] = useState(5);
  const [showTeamModal, setShowTeamModal] = useState(false);
  const [membershipStatus, setMembershipStatus] = useState(null);
  const [loadingStatus, setLoadingStatus] = useState(true);

  const plans = [
    {
      name: 'Solo计划',
      price: '20',
      period: '月',
      description: '适合个人从业者',
      features: [
        '无限量计划书分析',
        '个人IP形象生成',
        '文案智能创作',
        '海报分析工具',
        '优先客服支持',
        '所有基础功能'
      ],
      color: 'from-purple-600 to-pink-600',
      popular: false,
      planType: 'solo'
    },
    {
      name: 'Team计划',
      price: '10',
      period: '月/人',
      description: '5人以上团队',
      features: [
        '所有Solo计划功能',
        '团队协作空间',
        '统一账单管理',
        '数据共享',
        '团队成员管理',
        '专属客户经理'
      ],
      color: 'from-blue-600 to-cyan-600',
      popular: true,
      planType: 'team'
    }
  ];

  // 处理订阅
  const handleSubscribe = async (planType) => {
    if (planType === 'team') {
      setShowTeamModal(true);
      return;
    }

    await createCheckoutSession(planType, 1);
  };

  // 创建Stripe结账会话
  const createCheckoutSession = async (planType, quantity = 1) => {
    try {
      setLoading(true);

      const token = localStorage.getItem('access_token');
      if (!token) {
        alert('请先登录');
        onNavigate('home');
        return;
      }

      console.log('[Stripe] Creating checkout session...', { planType, quantity });

      const response = await axios.post(
        `${API_BASE_URL}/api/stripe/create-checkout-session`,
        {
          plan_type: planType,
          team_size: quantity
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      console.log('[Stripe] Session created:', response.data);

      // 直接跳转到Stripe结账页面（新版API）
      if (response.data.session_url) {
        console.log('[Stripe] Redirecting to checkout URL...');
        window.location.href = response.data.session_url;
      } else {
        console.error('[Stripe] No session_url in response');
        alert('❌ 创建支付会话失败\n\n未获取到支付链接，请重试');
      }
    } catch (error) {
      console.error('[Stripe] Error:', error);
      const errorMsg = error.response?.data?.error || error.message || '未知错误';
      alert(`❌ 创建支付会话失败\n\n${errorMsg}\n\n请刷新页面后重试`);
    } finally {
      setLoading(false);
    }
  };

  // Team计划订阅
  const handleTeamSubscribe = async () => {
    if (teamSize < 5) {
      alert('Team计划至少需要5人');
      return;
    }

    setShowTeamModal(false);
    await createCheckoutSession('team', teamSize);
  };

  // 获取会员状态
  useEffect(() => {
    const fetchMembershipStatus = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (!token) {
          setLoadingStatus(false);
          return;
        }

        const response = await axios.get(
          `${API_BASE_URL}/api/membership/check`,
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        );

        setMembershipStatus(response.data);
      } catch (error) {
        console.error('获取会员状态失败:', error);
      } finally {
        setLoadingStatus(false);
      }
    };

    fetchMembershipStatus();
  }, []);

  // 检查URL参数，显示支付结果
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('success') === 'true') {
      alert('支付成功！您的会员已激活。');
      // 清除URL参数
      window.history.replaceState({}, '', '/membership-plans');
      // 重新获取会员状态
      window.location.reload();
    } else if (urlParams.get('canceled') === 'true') {
      alert('支付已取消');
      // 清除URL参数
      window.history.replaceState({}, '', '/membership-plans');
    }
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* 返回按钮 */}
        <button
          onClick={() => onNavigate('dashboard')}
          className="mb-8 inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-all shadow-sm"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          返回Dashboard
        </button>

        {/* 标题区域 */}
        <div className="text-center mb-16">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">
            选择适合您的
            <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent"> 会员计划</span>
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto mb-6">
            专业的保险从业者工具平台，助力您的业务增长
          </p>

          {/* 支付方式提示 */}
          <div className="flex items-center justify-center gap-4 flex-wrap">
            <span className="text-sm text-gray-500">支持多种支付方式：</span>
            <div className="flex items-center gap-3">
              <div className="px-3 py-1.5 bg-white border border-gray-200 rounded-lg flex items-center gap-2 shadow-sm">
                <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20 8H4V6h16v2zm0 4H4v6h16v-6z"/>
                </svg>
                <span className="text-xs font-medium text-gray-700">信用卡</span>
              </div>
              <div className="px-3 py-1.5 bg-white border border-gray-200 rounded-lg flex items-center gap-2 shadow-sm">
                <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/>
                </svg>
                <span className="text-xs font-medium text-gray-700">微信支付</span>
              </div>
              <div className="px-3 py-1.5 bg-white border border-gray-200 rounded-lg flex items-center gap-2 shadow-sm">
                <svg className="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
                </svg>
                <span className="text-xs font-medium text-gray-700">支付宝</span>
              </div>
              <div className="px-3 py-1.5 bg-white border border-gray-200 rounded-lg flex items-center gap-2 shadow-sm">
                <span className="text-xs font-bold text-gray-700">G Pay</span>
              </div>
            </div>
          </div>
        </div>

        {/* 当前会员状态 */}
        {!loadingStatus && membershipStatus?.has_membership && (
          <div className="max-w-3xl mx-auto mb-12">
            <div className={`rounded-2xl shadow-lg p-6 border-2 ${
              membershipStatus.is_active
                ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-300'
                : 'bg-gradient-to-r from-red-50 to-orange-50 border-red-300'
            }`}>
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div className="flex items-center gap-4">
                  <div className={`w-16 h-16 rounded-full flex items-center justify-center ${
                    membershipStatus.is_active ? 'bg-green-500' : 'bg-red-500'
                  }`}>
                    <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      {membershipStatus.is_active ? (
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      ) : (
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      )}
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">
                      {membershipStatus.is_active ? '✨ 会员有效' : '⚠️ 会员已过期'}
                    </h3>
                    <p className="text-gray-600 mt-1">
                      当前计划：
                      <span className="font-semibold ml-1">
                        {membershipStatus.plan_type === 'solo' ? 'Solo计划' :
                         membershipStatus.plan_type === 'team' ? 'Team计划' :
                         membershipStatus.plan_type}
                      </span>
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600 mb-1">到期日期</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {new Date(membershipStatus.end_date).toLocaleDateString('zh-CN', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </p>
                  {membershipStatus.is_active && (
                    <p className={`text-sm mt-1 font-semibold ${
                      membershipStatus.days_remaining <= 7 ? 'text-red-600' : 'text-green-600'
                    }`}>
                      剩余 {membershipStatus.days_remaining} 天
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 计划卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {plans.map((plan, index) => (
            <div
              key={index}
              className={`relative bg-white rounded-2xl shadow-xl overflow-hidden transform transition-all hover:scale-105 ${
                plan.popular ? 'ring-4 ring-blue-400' : ''
              }`}
            >
              {/* 热门标签 */}
              {plan.popular && (
                <div className="absolute top-0 right-0 bg-gradient-to-r from-blue-600 to-cyan-600 text-white px-4 py-1 rounded-bl-lg text-sm font-bold">
                  推荐
                </div>
              )}

              <div className="p-8">
                {/* 计划名称 */}
                <div className="mb-6">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                  <p className="text-gray-600">{plan.description}</p>
                </div>

                {/* 价格 */}
                <div className="mb-8">
                  <div className="flex items-baseline gap-2">
                    <span className={`text-5xl font-bold bg-gradient-to-r ${plan.color} bg-clip-text text-transparent`}>
                      ${plan.price}
                    </span>
                    <span className="text-xl text-gray-600">/{plan.period}</span>
                  </div>
                </div>

                {/* 功能列表 */}
                <div className="space-y-4 mb-8">
                  {plan.features.map((feature, idx) => (
                    <div key={idx} className="flex items-start gap-3">
                      <div className={`flex-shrink-0 w-6 h-6 rounded-full bg-gradient-to-r ${plan.color} flex items-center justify-center`}>
                        <CheckIcon className="w-4 h-4 text-white" />
                      </div>
                      <span className="text-gray-700">{feature}</span>
                    </div>
                  ))}
                </div>

                {/* 购买按钮 */}
                <button
                  onClick={() => handleSubscribe(plan.planType)}
                  disabled={loading}
                  className={`w-full py-4 rounded-lg font-semibold text-white bg-gradient-to-r ${plan.color} hover:shadow-lg transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  {loading ? '处理中...' : '立即订阅'}
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* 说明文字 */}
        <div className="mt-16 text-center">
          <div className="max-w-3xl mx-auto bg-white rounded-xl p-8 shadow-md">
            <h3 className="text-xl font-bold text-gray-900 mb-4">常见问题</h3>
            <div className="space-y-4 text-left">
              <div>
                <p className="font-semibold text-gray-900 mb-1">Q: Team计划如何计费？</p>
                <p className="text-gray-600">A: Team计划需要至少5人订阅，每人每月90元。例如5人团队每月总费用为450元。</p>
              </div>
              <div>
                <p className="font-semibold text-gray-900 mb-1">Q: 可以随时取消吗？</p>
                <p className="text-gray-600">A: 可以。您可以随时取消订阅，取消后将继续享受服务至当前计费周期结束。</p>
              </div>
              <div>
                <p className="font-semibold text-gray-900 mb-1">Q: 如何升级计划？</p>
                <p className="text-gray-600">A: 联系我们的客服团队，我们将协助您完成计划升级，费用按比例计算。</p>
              </div>
            </div>
          </div>

          {/* 联系方式 */}
          <div className="mt-8 text-gray-600">
            <p>有任何问题？联系我们：</p>
            <p className="mt-2">
              <span className="font-semibold">电话：</span>852 62645180
              <span className="mx-4">|</span>
              <span className="font-semibold">邮箱：</span>client@xingke888.com
            </p>
          </div>
        </div>

        {/* Team人数选择模态框 */}
        {showTeamModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-4">选择团队人数</h3>
              <p className="text-gray-600 mb-6">Team计划至少需要5人订阅</p>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  团队人数
                </label>
                <input
                  type="number"
                  min="5"
                  value={teamSize}
                  onChange={(e) => setTeamSize(parseInt(e.target.value) || 5)}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-lg font-semibold"
                />
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-700">单价：</span>
                  <span className="text-xl font-bold text-gray-900">$10/人/月</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-700">总价：</span>
                  <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                    ${teamSize * 10}
                  </span>
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setShowTeamModal(false)}
                  disabled={loading}
                  className="flex-1 py-3 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-all font-semibold disabled:opacity-50"
                >
                  取消
                </button>
                <button
                  onClick={handleTeamSubscribe}
                  disabled={loading || teamSize < 5}
                  className="flex-1 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-lg hover:shadow-lg transition-all font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? '处理中...' : '确认订阅'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default MembershipPlans;
