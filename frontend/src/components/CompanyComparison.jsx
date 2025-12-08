import React, { useState, useEffect, useRef } from 'react';
import { ArrowLeft, GitCompare, Loader2, CheckCircle, Printer, Download, Check } from 'lucide-react';
import { useAppNavigate } from '../hooks/useAppNavigate';
import axios from 'axios';
import html2canvas from 'html2canvas';

function CompanyComparison() {
  const onNavigate = useAppNavigate();
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedIds, setSelectedIds] = useState([]);
  const [showComparison, setShowComparison] = useState(false);
  const [comparisonData, setComparisonData] = useState(null);
  const [customAgesInput, setCustomAgesInput] = useState('1,2,3,4,5,6,7,8,9,10,15,20,25,30,35,40,60,80,100');
  const [useCustomAges, setUseCustomAges] = useState(true);
  const [annualPremium, setAnnualPremium] = useState(10000); // 假设年缴保费

  // 演示用客户信息
  const [customerAge, setCustomerAge] = useState(30);
  const [customerGender, setCustomerGender] = useState('male');
  const [paymentAmount, setPaymentAmount] = useState(10000);
  const [paymentYears, setPaymentYears] = useState(5); // 缴费年限

  const comparisonTableRef = useRef(null); // 用于截图的ref

  useEffect(() => {
    fetchCompanies();
  }, []);

  const fetchCompanies = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/insurance-companies/standard-comparison/');
      const data = response.data;

      if (data.status === 'success') {
        setCompanies(data.data || []);
        console.log('✅ 保险公司数量:', data.data?.length);
      }
    } catch (error) {
      console.error('获取保险公司列表失败:', error);
      alert('获取保险公司列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectOne = (id) => {
    const company = companies.find(c => c.id === id);

    // 如果没有数据，不允许选择
    if (!company.has_data) {
      return;
    }

    setSelectedIds(prev => {
      if (prev.includes(id)) {
        return prev.filter(i => i !== id);
      } else {
        return [...prev, id];
      }
    });
  };

  // 计算年化单利（考虑每年交保费）
  const calculateSimpleAnnualizedReturn = (totalValue, annualPremium, holdingYears) => {
    if (!totalValue || !annualPremium || !holdingYears || holdingYears <= 0 || annualPremium <= 0) {
      return null;
    }
    // 总投入 = 年缴保费 × 持有年数
    const totalInvestment = annualPremium * holdingYears;
    // 年化单利 = (回报 - 投入) / 投入 / 年数 × 100%
    const simpleReturn = ((totalValue - totalInvestment) / totalInvestment / holdingYears) * 100;
    return simpleReturn;
  };

  // 计算IRR（内部收益率，基于实际的已缴保费数据）
  // yearlyPremiums: 数组，每年的已缴保费 [第1年, 第2年, ..., 第N年]
  // totalValue: 第N年的退保价值
  const calculateIRRFromActualPayments = (yearlyPremiums, totalValue, currentYear) => {
    if (!yearlyPremiums || yearlyPremiums.length === 0 || !totalValue || totalValue <= 0) {
      return null;
    }

    // 使用牛顿迭代法计算IRR
    // 对于长期持有，初始猜测值应该更低
    let rate = currentYear > 50 ? 0.03 : 0.05; // 长期持有初始猜测3%，短期5%
    const maxIterations = 200; // 增加迭代次数，支持长期计算
    const precision = currentYear > 50 ? 0.001 : 0.0001; // 长期持有降低精度要求

    for (let i = 0; i < maxIterations; i++) {
      let npv = 0;
      let derivative = 0;

      // 计算每年的现金流（基于已缴保费的增量）
      for (let year = 1; year <= currentYear; year++) {
        const currentPaid = yearlyPremiums[year - 1] || 0;
        const previousPaid = year > 1 ? (yearlyPremiums[year - 2] || 0) : 0;
        const payment = currentPaid - previousPaid; // 这一年实际缴纳的保费

        if (payment > 0) {
          const factor = Math.pow(1 + rate, year);
          npv -= payment / factor;
          derivative += (payment * year) / Math.pow(1 + rate, year + 1);
        }
      }

      // 第N年获得退保价值
      const finalFactor = Math.pow(1 + rate, currentYear);
      npv += totalValue / finalFactor;
      derivative -= (totalValue * currentYear) / Math.pow(1 + rate, currentYear + 1);

      // 检查收敛
      if (Math.abs(npv) < precision) {
        // 合理性检查：IRR不应超过100%（保险产品长期持有可能有较高收益）
        if (rate > 1) {
          console.warn('IRR异常高:', rate * 100, '%', {yearlyPremiums, totalValue, currentYear});
          return null;
        }
        // 对于长期持有，高IRR是正常的，只要在合理范围内就返回
        return rate * 100; // 转换为百分比
      }

      // 检查导数是否为0（避免除以0）
      if (Math.abs(derivative) < 0.0000001) {
        return null;
      }

      // 牛顿迭代：rate_new = rate_old - f(rate) / f'(rate)
      const newRate = rate - npv / derivative;

      // 防止振荡：如果变化太大，减小步长
      if (Math.abs(newRate - rate) > 1) {
        rate = rate - (npv / derivative) * 0.5;
      } else {
        rate = newRate;
      }

      // 防止负利率或过大利率
      if (rate < -0.99) rate = -0.99;
      if (rate > 2) rate = 2; // 放宽限制到200%（长期持有可能较高）
    }

    // 未收敛，输出调试信息
    console.warn('IRR计算未收敛', {
      yearlyPremiums: yearlyPremiums.length,
      totalValue,
      currentYear,
      lastRate: rate
    });
    return null;
  };

  const handleCompareCompanies = () => {
    if (selectedIds.length === 0) {
      alert('请先选择要对比的保险公司');
      return;
    }

    // 验证年缴保费最低2000
    if (paymentAmount < 2000) {
      alert('年缴保费最低为2000元');
      return;
    }

    // 获取选中的公司
    const selectedCompanies = companies.filter(c => selectedIds.includes(c.id));

    console.log('===== 开始检查选中的公司 =====');
    console.log('选中的公司数量:', selectedCompanies.length);

    // 检查是否所有公司都有standard_data
    const companiesWithoutData = selectedCompanies.filter(company => !company.has_data || !company.standard_data);

    if (companiesWithoutData.length > 0) {
      alert(`以下保险公司没有标准退保数据：\n${companiesWithoutData.map(c => c.name).join('\n')}`);
      return;
    }

    // 计算保费比例：用户输入 / 数据库标准值
    // 从第一家公司的数据中获取标准年缴保费（第1年的premiums_paid）
    const firstCompanyData = selectedCompanies[0]?.standard_data?.standard;
    const standardAnnualPremium = firstCompanyData?.[0]?.premiums_paid || 10000; // 默认10000
    const premiumRatio = paymentAmount / standardAnnualPremium;

    console.log('保费比例计算:', {
      userInput: paymentAmount,
      standardPremium: standardAnnualPremium,
      ratio: premiumRatio
    });

    // 动态计算所有公司的实际年龄范围
    let allYears = new Set();
    selectedCompanies.forEach(company => {
      const years = company.standard_data?.standard || [];
      years.forEach(y => {
        if (y.policy_year) {
          allYears.add(y.policy_year);
        }
      });
    });

    // 从实际数据中选择关键年度点
    const sortedYears = Array.from(allYears).sort((a, b) => a - b);
    let targetYears;

    // 如果用户输入了自定义年度
    if (useCustomAges && customAgesInput.trim()) {
      // 支持全角半角逗号、空格作为分隔符
      const inputs = customAgesInput
        .replace(/[,，\s]+/g, ',')  // 将全角逗号、半角逗号、空格都替换为统一的半角逗号
        .split(',')
        .map(item => item.trim())
        .filter(item => item);

      const customYears = new Set();
      inputs.forEach(input => {
        const year = parseInt(input);
        if (!isNaN(year) && allYears.has(year)) {
          customYears.add(year);
        }
      });

      targetYears = Array.from(customYears).sort((a, b) => a - b);

      if (targetYears.length === 0) {
        alert('输入的年度在数据中没有对应数据，请检查输入');
        return;
      }
    } else {
      // 默认逻辑：自动选择关键年度点 (1-9, 10, 15, 20, 25, 30, 35, 40, 60, 80, 100)
      const defaultYears = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30, 35, 40, 60, 80, 100];
      targetYears = sortedYears.filter(year => defaultYears.includes(year));

      // 如果某些默认年度不存在，尝试找最接近的
      if (targetYears.length === 0) {
        targetYears = sortedYears.filter((year, index, arr) => {
          // 保留关键节点：首、尾、以及均匀分布的中间节点
          if (index === 0 || index === arr.length - 1) return true;
          // 每5年取一个点
          return year % 5 === 0;
        }).slice(0, 20); // 最多显示20个年度点
      }
    }

    // 提取对比数据（应用保费比例）
    const comparison = selectedCompanies.map(company => {
      const years = company.standard_data?.standard || [];
      const yearData = {}; // 只存储要显示的年份数据
      const allYearData = {}; // 存储所有年份数据（用于IRR计算）

      // 提取显示年份的数据（按比例调整）
      targetYears.forEach(targetYear => {
        const data = years.find(y => y.policy_year === targetYear);

        if (data) {
          yearData[targetYear] = {
            guaranteed: Math.round(data.guaranteed * premiumRatio),
            non_guaranteed: Math.round(data.non_guaranteed * premiumRatio),
            total: Math.round(data.total * premiumRatio),
            premiums_paid: Math.round(data.premiums_paid * premiumRatio)
          };
        } else {
          yearData[targetYear] = {
            guaranteed: undefined,
            non_guaranteed: undefined,
            total: undefined,
            premiums_paid: undefined
          };
        }
      });

      // 提取所有年份的数据（按比例调整，用于IRR计算）
      years.forEach(yearItem => {
        const year = yearItem.policy_year;
        allYearData[year] = {
          guaranteed: Math.round(yearItem.guaranteed * premiumRatio),
          non_guaranteed: Math.round(yearItem.non_guaranteed * premiumRatio),
          total: Math.round(yearItem.total * premiumRatio),
          premiums_paid: Math.round(yearItem.premiums_paid * premiumRatio)
        };
      });

      return {
        id: company.id,
        name: company.name,
        icon: company.icon,
        yearData,        // 只用于显示
        allYearData      // 用于IRR计算
      };
    });

    setComparisonData({
      companies: comparison,
      targetYears,
      allYears: sortedYears // 保存所有年份，用于IRR计算
    });
    setShowComparison(true);
  };

  // 打印功能
  const handlePrint = () => {
    window.print();
  };

  // 下载为图片功能
  const handleDownloadImage = async () => {
    if (!comparisonTableRef.current) return;

    try {
      const canvas = await html2canvas(comparisonTableRef.current, {
        scale: 2, // 提高清晰度
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#ffffff'
      });

      // 转换为图片并下载
      const link = document.createElement('a');
      link.download = `保险公司对比_${new Date().toLocaleDateString('zh-CN')}.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
    } catch (error) {
      console.error('下载图片失败:', error);
      alert('下载图片失败，请重试');
    }
  };

  // 如果正在查看对比
  if (showComparison && comparisonData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 p-4 md:p-8">
        <div className="max-w-[98%] mx-auto">
          {/* 顶部按钮栏 */}
          <div className="mb-6 flex items-center justify-between print:hidden">
            <button
              onClick={() => setShowComparison(false)}
              className="flex items-center gap-2 px-6 py-3 bg-white/90 backdrop-blur-sm rounded-xl shadow-lg hover:shadow-xl transition-all text-base font-semibold hover:bg-white"
            >
              <ArrowLeft className="w-5 h-5" />
              返回列表
            </button>

            {/* 右侧操作按钮 */}
            <div className="flex items-center gap-3">
              <button
                onClick={handlePrint}
                className="flex items-center gap-2 px-6 py-3 bg-white/90 backdrop-blur-sm rounded-xl shadow-lg hover:shadow-xl transition-all text-base font-semibold hover:bg-white"
              >
                <Printer className="w-5 h-5" />
                打印
              </button>
              <button
                onClick={handleDownloadImage}
                className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl shadow-lg hover:shadow-xl transition-all text-base font-semibold hover:from-blue-700 hover:to-indigo-700"
              >
                <Download className="w-5 h-5" />
                下载图片
              </button>
            </div>
          </div>

          {/* 对比表格 */}
          <div ref={comparisonTableRef} className="bg-white/95 backdrop-blur-sm rounded-3xl shadow-2xl overflow-hidden border border-gray-100">
            {/* 标题栏 - 更大气的渐变 */}
            <div className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 px-6 py-6">
              <h2 className="text-2xl md:text-3xl font-bold text-white mb-4 tracking-wide text-center">退保价值数据对比分析</h2>

              {/* 客户信息展示 */}
              <div className="mt-4">
                <div className="flex items-center gap-6 flex-wrap text-white">
                  <div className="flex items-center gap-2">
                    <span className="text-blue-100 text-xs">客户年龄</span>
                    <span className="text-white text-sm font-semibold">{customerAge} 岁</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-blue-100 text-xs">性别</span>
                    <span className="text-white text-sm font-semibold">{customerGender === 'male' ? '男' : '女'}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-blue-100 text-xs">年缴保费</span>
                    <span className="text-white text-sm font-semibold">{paymentAmount.toLocaleString('zh-CN')} 元</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-blue-100 text-xs">缴费年限</span>
                    <span className="text-white text-sm font-semibold">{paymentYears} 年</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="p-4 md:p-6 overflow-x-auto bg-gradient-to-b from-gray-50 to-white">
              <table className="w-full min-w-max text-sm shadow-sm">
                <thead>
                  <tr className="border-b-2 border-indigo-200 bg-gradient-to-r from-blue-50 to-indigo-50">
                    <th className="px-1 py-3 text-center text-xs font-bold text-gray-800 sticky left-0 bg-gradient-to-r from-blue-50 to-indigo-50 z-10 border-r-2 border-indigo-200">
                      <div className="leading-tight">
                        <div>保单</div>
                        <div>年度</div>
                        <div>终结</div>
                      </div>
                    </th>
                    <th className="px-1 py-3 text-center text-xs font-bold text-gray-800 bg-gradient-to-r from-blue-50 to-indigo-50 border-r-2 border-indigo-200">
                      <div className="leading-tight">
                        <div>客户</div>
                        <div>年龄</div>
                      </div>
                    </th>
                    <th className="px-2 py-3 text-center text-xs font-bold text-gray-800 bg-gradient-to-r from-blue-50 to-indigo-50 border-r-2 border-indigo-200">已缴</th>
                    {comparisonData.companies.map((company, index) => (
                      <th key={company.id} className={`px-2 py-3 text-center bg-gradient-to-r from-blue-50 to-indigo-50 ${index < comparisonData.companies.length - 1 ? 'border-r-2 border-indigo-200' : ''}`} colSpan="5">
                        <div className="flex items-center justify-center gap-2">
                          {company.icon && (
                            company.icon.includes('http') || company.icon.includes('/') || company.icon.includes('.') ? (
                              <img
                                src={company.icon}
                                alt={company.name}
                                className="w-5 h-5 object-contain"
                                onError={(e) => {
                                  // 图片加载失败时隐藏
                                  e.target.style.display = 'none';
                                }}
                              />
                            ) : (
                              <span className="text-lg">{company.icon}</span>
                            )
                          )}
                          <div className="text-sm font-bold text-gray-800 truncate" title={company.name}>{company.name}</div>
                        </div>
                      </th>
                    ))}
                  </tr>
                  <tr className="border-b-2 border-gray-200 bg-gradient-to-r from-slate-50 to-gray-50">
                    <th className="px-1 py-2 text-center text-xs font-medium text-gray-600 sticky left-0 bg-gradient-to-r from-slate-50 to-gray-50 z-10 border-r-2 border-indigo-200"></th>
                    <th className="px-1 py-2 text-center text-xs font-medium text-gray-600 bg-gradient-to-r from-slate-50 to-gray-50 border-r-2 border-indigo-200"></th>
                    <th className="px-2 py-2 text-center text-xs font-medium text-gray-600 bg-gradient-to-r from-slate-50 to-gray-50 border-r-2 border-indigo-200"></th>
                    {comparisonData.companies.map((company, pIndex) => (
                      <React.Fragment key={`${company.id}-headers`}>
                        <th className="px-2 py-2 text-center text-xs font-semibold text-gray-700 whitespace-nowrap bg-gradient-to-r from-slate-50 to-gray-50">
                          保证
                        </th>
                        <th className="px-2 py-2 text-center text-xs font-semibold text-orange-700 whitespace-nowrap bg-gradient-to-r from-slate-50 to-gray-50">
                          非保证
                        </th>
                        <th className="px-2 py-2 text-center text-xs font-semibold text-indigo-700 whitespace-nowrap bg-gradient-to-r from-slate-50 to-gray-50">
                          总额
                        </th>
                        <th className="px-2 py-2 text-center text-xs font-semibold text-purple-700 whitespace-nowrap bg-gradient-to-r from-slate-50 to-gray-50">
                          单利
                        </th>
                        <th className={`px-2 py-2 text-center text-xs font-semibold text-green-700 whitespace-nowrap bg-gradient-to-r from-slate-50 to-gray-50 ${pIndex < comparisonData.companies.length - 1 ? 'border-r-2 border-indigo-200' : ''}`}>
                          IRR
                        </th>
                      </React.Fragment>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {comparisonData.targetYears.map(year => {
                    // 从第一家公司的数据中获取已缴保费（所有公司应该相同）
                    const firstCompanyData = comparisonData.companies[0]?.yearData[year];
                    const premiumsPaid = firstCompanyData?.premiums_paid !== undefined
                      ? firstCompanyData.premiums_paid
                      : annualPremium * year; // 备用计算

                    return (
                      <tr key={year} className="border-b border-gray-100 hover:bg-blue-50/50 transition-colors">
                        <td className="px-1 py-2.5 text-sm font-bold text-gray-900 whitespace-nowrap sticky left-0 bg-white z-10 border-r-2 border-indigo-200 text-center">
                          {year}
                        </td>
                        <td className="px-1 py-2.5 text-sm text-purple-600 font-bold text-center whitespace-nowrap bg-gradient-to-r from-purple-50 to-pink-50 border-r-2 border-indigo-200">
                          {customerAge + year}
                        </td>
                        <td className="px-2 py-2.5 text-sm text-gray-700 font-semibold text-center whitespace-nowrap bg-blue-50/50 border-r-2 border-indigo-200">
                          {premiumsPaid.toLocaleString('zh-CN')}
                        </td>
                        {comparisonData.companies.map((company, pIndex) => {
                          const data = company.yearData[year];
                          const totalValue = data?.total || 0;
                          const holdingYears = year;

                          // 使用数据中的已缴保费，如果没有则使用计算值
                          const actualPremiumsPaid = data?.premiums_paid !== undefined
                            ? data.premiums_paid
                            : annualPremium * holdingYears;

                          // 计算年化单利（使用实际已缴保费）
                          const simpleReturn = totalValue && actualPremiumsPaid && holdingYears > 0
                            ? ((totalValue - actualPremiumsPaid) / actualPremiumsPaid / holdingYears) * 100
                            : null;

                          // 计算IRR（使用实际的所有年份已缴保费数据）
                          let irr = null;
                          if (totalValue > 0 && actualPremiumsPaid > 0 && holdingYears > 0) {
                            // 收集该公司从第1年到第N年的所有已缴保费数据
                            const yearlyPremiums = [];

                            // 使用 allYearData 获取所有年份的数据
                            let missingYears = [];
                            for (let y = 1; y <= holdingYears; y++) {
                              const allYearDataItem = company.allYearData?.[y];
                              if (allYearDataItem?.premiums_paid !== undefined) {
                                yearlyPremiums.push(allYearDataItem.premiums_paid);
                              } else {
                                // 如果没有数据，使用计算值（向后兼容）
                                yearlyPremiums.push(annualPremium * y);
                                missingYears.push(y);
                              }
                            }

                            // 记录缺失的年份（用于调试）
                            if (missingYears.length > 0 && (holdingYears === 80 || holdingYears === 100)) {
                              console.log(`[数据检查] ${company.name} 第${holdingYears}年 缺失年份:`, missingYears.slice(0, 10));
                            }

                            // 检查数据合理性（放宽限制，保险产品长期持有回报可能较高）
                            const returnRatio = totalValue / actualPremiumsPaid;
                            if (returnRatio > 0 && yearlyPremiums.length > 0) {
                              irr = calculateIRRFromActualPayments(yearlyPremiums, totalValue, holdingYears);

                              // 调试日志
                              if (irr === null && (holdingYears === 80 || holdingYears === 100)) {
                                console.log(`[IRR调试] 第${holdingYears}年:`, {
                                  company: company.name,
                                  totalValue,
                                  actualPremiumsPaid,
                                  returnRatio,
                                  yearlyPremiusLength: yearlyPremiums.length,
                                  firstPremium: yearlyPremiums[0],
                                  lastPremium: yearlyPremiums[yearlyPremiums.length - 1]
                                });
                              }
                            }
                          }

                          return (
                            <React.Fragment key={`${company.id}-${year}`}>
                              <td className="px-2 py-2.5 text-sm text-gray-800 font-semibold text-center whitespace-nowrap">
                                {data?.guaranteed !== undefined && data?.guaranteed !== null
                                  ? parseInt(data.guaranteed).toLocaleString('zh-CN')
                                  : '-'}
                              </td>
                              <td className="px-2 py-2.5 text-sm text-orange-600 font-semibold text-center whitespace-nowrap">
                                {data?.non_guaranteed !== undefined && data?.non_guaranteed !== null
                                  ? parseInt(data.non_guaranteed).toLocaleString('zh-CN')
                                  : '-'}
                              </td>
                              <td className="px-2 py-2.5 text-sm text-indigo-700 font-bold text-center whitespace-nowrap bg-indigo-50/30">
                                {data?.total !== undefined && data?.total !== null
                                  ? parseInt(data.total).toLocaleString('zh-CN')
                                  : '-'}
                              </td>
                              <td className="px-2 py-2.5 text-sm text-purple-600 font-bold text-center whitespace-nowrap">
                                {simpleReturn !== null ? `${simpleReturn.toFixed(2)}%` : '-'}
                              </td>
                              <td className={`px-2 py-2.5 text-sm text-green-600 font-bold text-center whitespace-nowrap bg-green-50/30 ${pIndex < comparisonData.companies.length - 1 ? 'border-r-2 border-indigo-200' : ''}`}>
                                {irr !== null ? `${irr.toFixed(2)}%` : '-'}
                              </td>
                            </React.Fragment>
                          );
                        })}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // 列表视图
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 px-3 md:px-4 pt-3 md:pt-6 pb-4 md:pb-8">
      <div className="max-w-[98%] mx-auto">
        {/* 头部 */}
        <div className="mb-4 md:mb-8">
          {/* 标题 */}
          <div className="mb-3 md:mb-6 text-center">
            <h1 className="text-2xl md:text-3xl lg:text-4xl font-bold text-gray-800 tracking-wide">保险公司标准退保数据对比</h1>
          </div>

          {/* 按钮栏 */}
          <div className="mb-3 md:mb-6 flex items-center justify-between gap-2">
            <button
              onClick={() => onNavigate('dashboard')}
              className="flex items-center gap-1.5 md:gap-2 px-4 md:px-6 py-2 md:py-3 bg-white/90 backdrop-blur-sm rounded-xl shadow-lg hover:shadow-xl transition-all text-sm md:text-base font-semibold hover:bg-white"
            >
              <ArrowLeft className="w-4 h-4 md:w-5 md:h-5" />
              <span className="hidden sm:inline">返回Dashboard</span>
              <span className="sm:hidden">返回</span>
            </button>

            {/* 对比按钮 */}
            <button
              onClick={handleCompareCompanies}
              className="flex items-center gap-2 md:gap-3 px-4 md:px-8 py-2 md:py-4 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:via-indigo-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl text-base md:text-lg font-bold"
            >
              <GitCompare className="w-5 h-5 md:w-7 md:h-7" />
              <span>对比 {selectedIds.length > 0 ? `(${selectedIds.length})` : ''}</span>
            </button>
          </div>

          {/* 客户演示信息 */}
          <div className="mb-3 md:mb-6 bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl p-3 md:p-6 border border-gray-100">
            <div className="space-y-2 md:space-y-3">
              {/* 第一行：客户基本信息 */}
              <div className="flex items-center gap-3 md:gap-8 flex-wrap">
                {/* 客户年龄 */}
                <div className="flex items-center gap-2 md:gap-3">
                  <label className="text-gray-700 font-semibold text-sm md:text-base">客户年龄：</label>
                  <input
                    type="number"
                    value={customerAge}
                    onChange={(e) => setCustomerAge(Number(e.target.value))}
                    placeholder="30"
                    min="0"
                    max="100"
                    className="w-16 md:w-24 px-2 md:px-4 py-2 md:py-2.5 border-2 border-gray-200 rounded-lg text-gray-900 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-sm md:text-base"
                  />
                  <span className="text-gray-600 font-medium text-sm md:text-base">岁</span>
                </div>

                {/* 客户性别 */}
                <div className="flex items-center gap-2 md:gap-3">
                  <label className="text-gray-700 font-semibold text-sm md:text-base">性别：</label>
                  <div className="flex items-center gap-2 md:gap-4">
                    <label className="flex items-center gap-1.5 cursor-pointer px-2 md:px-4 py-1.5 md:py-2 rounded-lg hover:bg-blue-50 transition-colors">
                      <input
                        type="radio"
                        value="male"
                        checked={customerGender === 'male'}
                        onChange={(e) => setCustomerGender(e.target.value)}
                        className="w-4 h-4 text-blue-600"
                      />
                      <span className="text-gray-700 font-medium text-sm md:text-base">男</span>
                    </label>
                    <label className="flex items-center gap-1.5 cursor-pointer px-2 md:px-4 py-1.5 md:py-2 rounded-lg hover:bg-pink-50 transition-colors">
                      <input
                        type="radio"
                        value="female"
                        checked={customerGender === 'female'}
                        onChange={(e) => setCustomerGender(e.target.value)}
                        className="w-4 h-4 text-blue-600"
                      />
                      <span className="text-gray-700 font-medium text-sm md:text-base">女</span>
                    </label>
                  </div>
                </div>

                {/* 年缴保费 */}
                <div className="flex items-center gap-2 md:gap-3">
                  <label className="text-gray-700 font-semibold text-sm md:text-base">年缴保费：</label>
                  <input
                    type="number"
                    value={paymentAmount}
                    onChange={(e) => setPaymentAmount(Number(e.target.value))}
                    placeholder="10000"
                    min="2000"
                    className="w-24 md:w-36 px-2 md:px-4 py-2 md:py-2.5 border-2 border-gray-200 rounded-lg text-gray-900 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-sm md:text-base"
                  />
                  <span className="text-gray-600 font-medium text-sm md:text-base">元</span>
                </div>

                {/* 缴费年限 */}
                <div className="flex items-center gap-2 md:gap-3">
                  <label className="text-gray-700 font-semibold text-sm md:text-base">缴费年限：</label>
                  <div className="flex items-center gap-2 md:gap-4">
                    <label className="flex items-center gap-1.5 cursor-pointer px-2 md:px-4 py-1.5 md:py-2 rounded-lg hover:bg-blue-50 transition-colors">
                      <input
                        type="radio"
                        value="2"
                        checked={paymentYears === 2}
                        onChange={(e) => setPaymentYears(Number(e.target.value))}
                        className="w-4 h-4 text-blue-600"
                      />
                      <span className="text-gray-700 font-medium text-sm md:text-base">2年</span>
                    </label>
                    <label className="flex items-center gap-1.5 cursor-pointer px-2 md:px-4 py-1.5 md:py-2 rounded-lg hover:bg-blue-50 transition-colors">
                      <input
                        type="radio"
                        value="5"
                        checked={paymentYears === 5}
                        onChange={(e) => setPaymentYears(Number(e.target.value))}
                        className="w-4 h-4 text-blue-600"
                      />
                      <span className="text-gray-700 font-medium text-sm md:text-base">5年</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 保险公司列表 */}
        {loading ? (
          <div className="flex items-center justify-center py-12 md:py-20">
            <Loader2 className="w-12 h-12 text-indigo-600 animate-spin" />
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3 md:gap-6">
            {companies.map((company) => (
              <div
                key={company.id}
                onClick={() => handleSelectOne(company.id)}
                className={`
                  relative rounded-xl md:rounded-2xl shadow-lg p-3 md:p-6 transition-all cursor-pointer border-2
                  ${!company.has_data
                    ? 'opacity-50 cursor-not-allowed border-gray-200 bg-white/95 backdrop-blur-sm'
                    : selectedIds.includes(company.id)
                      ? 'bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 border-blue-400 ring-2 md:ring-4 ring-blue-500 shadow-2xl scale-105'
                      : 'bg-white/95 backdrop-blur-sm hover:shadow-2xl hover:scale-105 border-transparent hover:bg-gradient-to-br hover:from-blue-50/50 hover:to-indigo-50/50'
                  }
                `}
              >
                {/* 选中标记 */}
                {selectedIds.includes(company.id) && (
                  <div className="absolute top-2 right-2 md:top-3 md:right-3 bg-blue-600 rounded-lg p-1 md:p-1.5 shadow-lg">
                    <Check className="w-5 h-5 md:w-7 md:h-7 text-white stroke-[3]" />
                  </div>
                )}

                {/* 公司图标/Logo */}
                <div className="flex items-center justify-center mb-2 md:mb-4">
                  {company.icon ? (
                    // 判断是图片URL还是emoji
                    company.icon.includes('http') || company.icon.includes('/') || company.icon.includes('.') ? (
                      <img
                        src={company.icon}
                        alt={company.name}
                        className="w-12 h-12 md:w-20 md:h-20 object-contain"
                        onError={(e) => {
                          // 图片加载失败时显示首字母
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'flex';
                        }}
                      />
                    ) : (
                      <span className="text-3xl md:text-5xl">{company.icon}</span>
                    )
                  ) : (
                    <div className="w-12 h-12 md:w-20 md:h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl md:rounded-2xl flex items-center justify-center text-white text-xl md:text-3xl font-bold shadow-lg">
                      {company.name.charAt(0)}
                    </div>
                  )}
                  {/* 图片加载失败时的备用显示 */}
                  <div className="hidden w-12 h-12 md:w-20 md:h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl md:rounded-2xl items-center justify-center text-white text-xl md:text-3xl font-bold shadow-lg">
                    {company.name.charAt(0)}
                  </div>
                </div>

                {/* 公司名称 */}
                <div className="text-center">
                  <h3 className="text-sm md:text-xl font-bold text-gray-800 mb-1 md:mb-2 line-clamp-2">{company.name}</h3>
                  {company.name_en && (
                    <p className="text-xs md:text-sm text-gray-500 mb-2 md:mb-3 line-clamp-1">{company.name_en}</p>
                  )}
                </div>

                {/* 数据状态 */}
                <div className="text-center mt-2 md:mt-4">
                  {company.has_data ? (
                    <span className="inline-flex items-center gap-1 md:gap-1.5 px-2 md:px-4 py-1 md:py-2 bg-gradient-to-r from-green-50 to-emerald-50 text-green-700 text-xs md:text-sm font-bold rounded-full border border-green-200 md:border-2">
                      <CheckCircle className="w-3 h-3 md:w-4 md:h-4" />
                      <span className="hidden sm:inline">有数据</span>
                      <span className="sm:hidden">✓</span>
                    </span>
                  ) : (
                    <span className="inline-block px-2 md:px-4 py-1 md:py-2 bg-gray-100 text-gray-500 text-xs md:text-sm font-semibold rounded-full border border-gray-200 md:border-2">
                      <span className="hidden sm:inline">暂无数据</span>
                      <span className="sm:hidden">-</span>
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* 自定义对比年度 - 移到最下面 */}
        <div className="mt-4 md:mt-6 bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl p-3 md:p-6 border border-gray-100">
          <div className="flex items-center gap-2 md:gap-4">
            <label className="flex items-center gap-2 md:gap-3 cursor-pointer px-2 md:px-3 py-1 md:py-1.5 rounded-lg hover:bg-blue-50 transition-colors">
              <input
                type="checkbox"
                checked={useCustomAges}
                onChange={(e) => setUseCustomAges(e.target.checked)}
                className="w-4 h-4 rounded"
              />
              <span className="text-gray-700 font-semibold text-sm md:text-base whitespace-nowrap">自定义年度</span>
            </label>
            {useCustomAges && (
              <div className="flex-1 flex items-center gap-2">
                <input
                  type="text"
                  value={customAgesInput}
                  onChange={(e) => setCustomAgesInput(e.target.value)}
                  placeholder="例如: 1 2 3 4 5"
                  className="flex-1 px-2 md:px-4 py-2 md:py-2.5 border-2 border-gray-200 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-sm md:text-base"
                />
              </div>
            )}
            {!useCustomAges && (
              <span className="text-xs md:text-sm text-gray-500 hidden sm:inline">默认：1-9, 10, 15, 20, 25, 30, 35, 40, 60, 80, 100</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default CompanyComparison;
