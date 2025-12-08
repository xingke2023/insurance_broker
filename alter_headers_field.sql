-- 修改 insurance_company_requests 表的 headers 字段为 LONGTEXT
-- 这个脚本会安全地转换现有数据

USE insurancetools;

-- 查看当前字段类型
SELECT
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'insurancetools'
  AND TABLE_NAME = 'insurance_company_requests'
  AND COLUMN_NAME = 'headers';

-- 修改字段类型为 LONGTEXT
ALTER TABLE insurance_company_requests
MODIFY COLUMN headers LONGTEXT
COMMENT 'HTTP请求头（JSON格式字符串）';

-- 验证修改后的字段类型
SELECT
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'insurancetools'
  AND TABLE_NAME = 'insurance_company_requests'
  AND COLUMN_NAME = 'headers';

-- 查看现有数据（如果有）
SELECT
    id,
    request_name,
    LENGTH(headers) as headers_length,
    LEFT(headers, 100) as headers_preview
FROM insurance_company_requests
WHERE headers IS NOT NULL AND headers != '';
