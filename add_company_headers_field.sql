-- 为 insurance_companies 表添加 headers 字段

USE insurancetools;

-- 添加 headers 字段
ALTER TABLE insurance_companies
ADD COLUMN headers LONGTEXT
COMMENT '公司级别的通用HTTP Headers（JSON格式或键值对格式）'
AFTER description;

-- 验证字段已添加
DESC insurance_companies;

-- 查看现有数据
SELECT
    id,
    code,
    name,
    LENGTH(headers) as headers_length,
    LENGTH(bearer_token) as bearer_token_length,
    LENGTH(cookie) as cookie_length
FROM insurance_companies;
