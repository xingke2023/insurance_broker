-- 更新AXA利益表计算的headers配置
UPDATE insurance_company_requests 
SET headers = '{"Content-Type":"application/json","Accept":"application/json, text/plain, */*","Language":"zh-Hant","X-Compcode":"AXAHK","X-Device-Type":"web","X-Device-Version":"1.41.0.4.30","Origin":"https://atk.axahk.digital","Referer":"https://atk.axahk.digital/"}'
WHERE company_id = (SELECT id FROM insurance_companies WHERE code = 'axa')
AND request_name = '利益表计算';

-- 更新AXA提取金额计算的headers配置
UPDATE insurance_company_requests 
SET headers = '{"Content-Type":"application/json","Accept":"application/json, text/plain, */*","Language":"zh-Hant","X-Compcode":"AXAHK","X-Device-Type":"web","X-Device-Version":"1.41.0.4.30","Origin":"https://atk.axahk.digital","Referer":"https://atk.axahk.digital/"}'
WHERE company_id = (SELECT id FROM insurance_companies WHERE code = 'axa')
AND request_name = '提取金额计算';

-- 查询更新后的结果
SELECT 
    ic.name AS company_name,
    icr.request_name,
    icr.headers
FROM insurance_company_requests icr
JOIN insurance_companies ic ON icr.company_id = ic.id
WHERE ic.code = 'axa';
