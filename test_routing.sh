#!/bin/bash

echo "=================================="
echo "文档详情页面路由测试"
echo "=================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试 1: 检查 Django 服务器
echo "测试 1: 检查 Django 服务器是否运行..."
if ps aux | grep -v grep | grep "manage.py runserver" > /dev/null; then
    echo -e "${GREEN}✓${NC} Django 服务器正在运行"
else
    echo -e "${RED}✗${NC} Django 服务器未运行"
    echo "   请运行: python3 manage.py runserver 0.0.0.0:8017"
fi
echo ""

# 测试 2: 检查前端构建文件
echo "测试 2: 检查前端构建文件..."
if [ -f "frontend/dist/index.html" ]; then
    echo -e "${GREEN}✓${NC} index.html 存在"
else
    echo -e "${RED}✗${NC} index.html 不存在"
    echo "   请运行: cd frontend && npm run build"
fi

if [ -d "frontend/dist/assets" ]; then
    asset_count=$(ls frontend/dist/assets/*.js 2>/dev/null | wc -l)
    if [ $asset_count -gt 0 ]; then
        echo -e "${GREEN}✓${NC} 静态资源文件存在 ($asset_count 个 JS 文件)"
    else
        echo -e "${RED}✗${NC} 静态资源目录为空"
    fi
else
    echo -e "${RED}✗${NC} assets 目录不存在"
fi
echo ""

# 测试 3: 测试 API 端点
echo "测试 3: 测试 API 端点..."
api_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8017/api/ocr/documents/43/)
if [ "$api_response" = "200" ]; then
    echo -e "${GREEN}✓${NC} API 端点正常 (HTTP $api_response)"
elif [ "$api_response" = "404" ]; then
    echo -e "${YELLOW}⚠${NC} 文档 ID 43 不存在 (HTTP $api_response)"
    echo "   这是正常的，尝试其他文档 ID"
else
    echo -e "${RED}✗${NC} API 端点异常 (HTTP $api_response)"
fi
echo ""

# 测试 4: 测试前端路由
echo "测试 4: 测试前端路由..."
route_response=$(curl -s http://localhost:8017/document/43 | head -1)
if echo "$route_response" | grep -q "<!doctype html>"; then
    echo -e "${GREEN}✓${NC} 前端路由返回 HTML"
else
    echo -e "${RED}✗${NC} 前端路由返回异常"
    echo "   响应: $route_response"
fi
echo ""

# 测试 5: 测试静态资源加载
echo "测试 5: 测试静态资源加载..."
if [ -d "frontend/dist/assets" ]; then
    js_file=$(ls frontend/dist/assets/index-*.js 2>/dev/null | head -1)
    if [ -n "$js_file" ]; then
        js_filename=$(basename "$js_file")
        static_response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8017/assets/$js_filename")
        if [ "$static_response" = "200" ]; then
            echo -e "${GREEN}✓${NC} 静态资源可访问 (HTTP $static_response)"
        else
            echo -e "${RED}✗${NC} 静态资源访问失败 (HTTP $static_response)"
        fi
    else
        echo -e "${YELLOW}⚠${NC} 找不到 JS 文件"
    fi
else
    echo -e "${RED}✗${NC} assets 目录不存在"
fi
echo ""

# 测试 6: 检查配置文件
echo "测试 6: 检查配置文件..."

# 检查 backend/urls.py
if grep -q "index_view" backend/urls.py; then
    echo -e "${GREEN}✓${NC} backend/urls.py 包含 index_view"
else
    echo -e "${RED}✗${NC} backend/urls.py 未配置 index_view"
fi

# 检查 backend/views.py
if [ -f "backend/views.py" ]; then
    echo -e "${GREEN}✓${NC} backend/views.py 存在"
else
    echo -e "${RED}✗${NC} backend/views.py 不存在"
fi

# 检查 settings.py TEMPLATES
if grep -q "frontend.*dist" backend/settings.py; then
    echo -e "${GREEN}✓${NC} settings.py TEMPLATES 配置正确"
else
    echo -e "${RED}✗${NC} settings.py TEMPLATES 未配置"
fi

# 检查 App.jsx 路由
if grep -q '/document/:id' frontend/src/App.jsx; then
    echo -e "${GREEN}✓${NC} App.jsx 包含文档详情路由"
else
    echo -e "${RED}✗${NC} App.jsx 缺少文档详情路由"
fi

echo ""
echo "=================================="
echo "测试完成"
echo "=================================="
echo ""
echo "如果所有测试都通过，现在可以："
echo "1. 访问 http://your-domain/plan-management"
echo "2. 点击任意文档的'详情'按钮"
echo "3. 应该能正常跳转到详情页"
echo ""
echo "如果有测试失败，请查看 FIXED_DOCUMENT_DETAIL_ROUTING.md 获取解决方案"
