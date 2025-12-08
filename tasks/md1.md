plan-management頁面的產品對比，實現邏輯是什麼，簡要回答我
核心函数：handleCompareProducts
检查选中文档是否都有 table1（年度价值表）数据
table1（年度价值表）数据
{"standard": [{"policy_year": 1, "guaranteed": 0, "non_guaranteed": 0, "total": 0}, {"policy_year": 2, "guaranteed": 2500, "non_guaranteed": 19200, "total": 21700}, {"policy_year": 3, "guaranteed": 12500, "non_guaranteed": 40068, "total": 52568}]}

數據庫開闢專門的一個表，記錄是每個保險公司的標準，1年到100年的数据

比較的是什麼，格式是什麼
比如每一個保險公司有一個表格

/home/ubuntu/miniconda3/envs/harry-insurance/bin/python manage.py

