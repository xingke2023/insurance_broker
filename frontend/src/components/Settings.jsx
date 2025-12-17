import { useAppNavigate } from '../hooks/useAppNavigate';
import { CogIcon, ChartBarIcon, ArrowLeftIcon } from '@heroicons/react/24/outline';

function Settings() {
  const onNavigate = useAppNavigate();

  const settingOptions = [
    {
      name: '产品对比设置',
      description: '选择在产品对比页面中显示的保险产品',
      icon: ChartBarIcon,
      action: () => onNavigate('product-comparison-settings'),
      color: 'from-blue-500 via-blue-600 to-indigo-700'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 via-gray-200 to-slate-100">
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12 py-4 sm:py-6">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => onNavigate('dashboard')}
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors mb-4"
          >
            <ArrowLeftIcon className="w-4 h-4" />
            <span className="text-sm font-medium">返回Dashboard</span>
          </button>

          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-md">
              <CogIcon className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 drop-shadow-sm">设置</h1>
              <p className="text-sm text-gray-600">管理您的个人偏好和系统设置</p>
            </div>
          </div>
        </div>

        {/* Settings Options */}
        <div className="space-y-4">
          <h2 className="text-base sm:text-lg font-bold text-gray-900 drop-shadow-sm flex items-center gap-2">
            <div className="w-1 h-5 bg-gradient-to-b from-blue-500 to-blue-600 rounded-full"></div>
            功能设置
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {settingOptions.map((option, index) => (
              <button
                key={index}
                onClick={option.action}
                className={`group relative overflow-hidden bg-gradient-to-br ${option.color} rounded-xl p-4 shadow-[0_4px_16px_rgba(0,0,0,0.12)] hover:shadow-[0_8px_24px_rgba(0,0,0,0.2)] transition-all duration-300 text-left hover:scale-[1.02] hover:-translate-y-0.5 active:scale-[0.98] active:translate-y-0`}
              >
                <div className="absolute inset-0 bg-gradient-to-t from-black/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>

                <div className="relative z-10">
                  <option.icon className="w-10 h-10 text-white mb-3 drop-shadow-lg" />
                  <h3 className="text-base font-bold text-white mb-1 drop-shadow-md">
                    {option.name}
                  </h3>
                  <p className="text-xs text-white/90 drop-shadow-sm">
                    {option.description}
                  </p>
                </div>

                <div className="absolute bottom-3 right-3 text-white/60 group-hover:text-white/90 transition-colors">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Settings;
