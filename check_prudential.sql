-- 查询Prudential的配置
SELECT 
    ic.id AS company_id,
    ic.code AS company_code,
    ic.name AS company_name,
    ic.bearer_token IS NOT NULL AS has_bearer_token,
    LENGTH(ic.bearer_token) AS bearer_token_length,
    ic.cookie IS NOT NULL AS has_cookie
FROM insurance_companies ic
WHERE ic.code = 'prudential';

-- 查询Prudential的API请求配置
SELECT 
    icr.id,
    icr.request_name,
    LENGTH(icr.headers) AS headers_length,
    LEFT(icr.headers, 100) AS headers_preview,
    icr.configurable_fields,
    icr.is_active
FROM insurance_company_requests icr
JOIN insurance_companies ic ON icr.company_id = ic.id
WHERE ic.code = 'prudential'
  AND icr.request_name = '核对';
