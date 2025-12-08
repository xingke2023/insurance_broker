#!/bin/bash
# 测试headers是否正确显示

echo "========================================"
echo "测试从数据库读取headers"
echo "========================================"

# 1. 检查数据库中的headers字段
echo -e "\n1️⃣ 检查数据库中AXA利益表计算的headers配置："
mysql -h localhost -P 8510 -u root -p'Mwq..0018' insurancetools -e "
SELECT
    ic.name AS '保险公司',
    icr.request_name AS '请求名称',
    LENGTH(icr.headers) AS 'headers长度',
    LEFT(icr.headers, 200) AS 'headers内容预览'
FROM insurance_company_requests icr
JOIN insurance_companies ic ON icr.company_id = ic.id
WHERE ic.code = 'axa'
  AND icr.request_name = '利益表计算';
" 2>/dev/null

# 2. 测试API端点
echo -e "\n2️⃣ 测试API端点是否正确返回headers："
echo "访问: http://localhost:8007/api/insurance-companies/axa/requests/利益表计算/"
echo ""

# 获取token（假设有测试用户）
echo "提示：请手动访问页面或使用以下命令测试："
echo "curl -H 'Authorization: Bearer YOUR_TOKEN' http://localhost:8007/api/insurance-companies/axa/requests/%E5%88%A9%E7%9B%8A%E8%A1%A8%E8%AE%A1%E7%AE%97/"

echo -e "\n3️⃣ 查看Django日志（实时）："
echo "sudo supervisorctl tail -f harry-insurance:harry-insurance-django"

echo -e "\n========================================"
echo "测试完成"
echo "========================================"
