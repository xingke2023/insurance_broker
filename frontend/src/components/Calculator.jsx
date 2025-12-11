import React, { useState, useEffect } from 'react';
import { X, Delete } from 'lucide-react';

/**
 * Calculator Component - iPad友好的数字输入计算器
 * @param {boolean} isOpen - 是否显示计算器
 * @param {function} onClose - 关闭回调
 * @param {function} onConfirm - 确认回调，接收输入的数字
 * @param {number} initialValue - 初始值
 * @param {string} title - 标题
 * @param {number} min - 最小值
 * @param {number} max - 最大值
 */
function Calculator({ isOpen, onClose, onConfirm, initialValue = 0, title = '输入数字', min, max }) {
  const [value, setValue] = useState(initialValue.toString());

  useEffect(() => {
    if (isOpen) {
      setValue(initialValue.toString());
    }
  }, [isOpen, initialValue]);

  const handleNumberClick = (num) => {
    if (value === '0') {
      setValue(num.toString());
    } else {
      const newValue = value + num.toString();
      setValue(newValue);
    }
  };

  const handleDelete = () => {
    if (value.length > 1) {
      setValue(value.slice(0, -1));
    } else {
      setValue('0');
    }
  };

  const handleClear = () => {
    setValue('0');
  };

  const handleConfirm = () => {
    const numValue = parseInt(value) || 0;

    // 验证范围
    if (min !== undefined && numValue < min) {
      alert(`最小值为 ${min}`);
      return;
    }
    if (max !== undefined && numValue > max) {
      alert(`最大值为 ${max}`);
      return;
    }

    onConfirm(numValue);
    onClose();
  };

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!isOpen) return null;

  // 数字按钮数据
  const numbers = [
    [7, 8, 9],
    [4, 5, 6],
    [1, 2, 3],
    [0, '00']
  ];

  return (
    <div
      className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-3"
      onClick={handleBackdropClick}
    >
      <div className="bg-white rounded-2xl shadow-2xl max-w-xs w-full overflow-hidden">
        {/* 标题栏 */}
        <div className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 px-4 py-2.5 flex items-center justify-between">
          <h3 className="text-base font-bold text-white">{title}</h3>
          <button
            onClick={onClose}
            className="text-white hover:bg-white/20 rounded-full p-1 transition-all"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* 显示屏 */}
        <div className="bg-gradient-to-br from-slate-50 to-gray-100 px-3 py-4">
          <div className="bg-white rounded-xl shadow-inner px-3 py-2 border-2 border-indigo-100">
            <div className="text-right text-2xl font-bold text-gray-900 tracking-wider min-h-[40px] flex items-center justify-end">
              {parseInt(value).toLocaleString('zh-CN')}
            </div>
          </div>
        </div>

        {/* 按键区域 */}
        <div className="p-3 bg-gradient-to-br from-gray-50 to-slate-50">
          <div className="grid gap-2 mb-3">
            {numbers.map((row, rowIndex) => (
              <div key={rowIndex} className="grid grid-cols-3 gap-2">
                {row.map((num) => (
                  <button
                    key={num}
                    onClick={() => handleNumberClick(num)}
                    className="
                      bg-white hover:bg-gradient-to-br hover:from-blue-50 hover:to-indigo-50
                      rounded-xl shadow-md hover:shadow-lg
                      border-2 border-gray-200 hover:border-indigo-300
                      transition-all active:scale-95
                      py-3 text-2xl font-bold text-gray-800
                    "
                  >
                    {num}
                  </button>
                ))}
                {rowIndex === 3 && (
                  <button
                    onClick={handleDelete}
                    className="bg-gradient-to-br from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white rounded-xl shadow-md hover:shadow-lg transition-all active:scale-95 flex items-center justify-center py-3"
                  >
                    <Delete className="w-6 h-6" />
                  </button>
                )}
              </div>
            ))}
          </div>

          {/* 底部按钮 */}
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={handleClear}
              className="bg-gradient-to-br from-gray-400 to-gray-500 hover:from-gray-500 hover:to-gray-600 text-white rounded-xl shadow-md hover:shadow-lg transition-all active:scale-95 py-2.5 text-base font-bold"
            >
              清空
            </button>
            <button
              onClick={handleConfirm}
              className="bg-gradient-to-br from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white rounded-xl shadow-md hover:shadow-lg transition-all active:scale-95 py-2.5 text-base font-bold"
            >
              确认
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Calculator;
