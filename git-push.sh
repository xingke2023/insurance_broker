#!/bin/bash

# 自动推送脚本 - Insurance Broker Project
# 使用方法: ./git-push.sh "你的提交信息"
# 或者: ./git-push.sh (使用默认提交信息)

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}    Git 自动推送脚本${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""

# 检查是否有改动
echo -e "${YELLOW}[1/4] 检查代码改动...${NC}"
if [[ -z $(git status -s) ]]; then
    echo -e "${RED}没有发现任何改动，无需推送！${NC}"
    exit 0
fi

echo -e "${GREEN}发现以下改动:${NC}"
git status -s
echo ""

# 添加所有改动
echo -e "${YELLOW}[2/4] 添加所有改动到暂存区...${NC}"
git add .
echo -e "${GREEN}✓ 已添加所有改动${NC}"
echo ""

# 创建提交
echo -e "${YELLOW}[3/4] 创建提交...${NC}"
if [ -z "$1" ]; then
    # 如果没有提供提交信息，使用默认信息
    COMMIT_MSG="Update: $(date '+%Y-%m-%d %H:%M:%S')"
    echo -e "${YELLOW}使用默认提交信息: ${COMMIT_MSG}${NC}"
else
    # 使用用户提供的提交信息
    COMMIT_MSG="$1"
    echo -e "${YELLOW}使用自定义提交信息: ${COMMIT_MSG}${NC}"
fi

git commit -m "$COMMIT_MSG"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 提交成功${NC}"
else
    echo -e "${RED}✗ 提交失败${NC}"
    exit 1
fi
echo ""

# 推送到GitHub
echo -e "${YELLOW}[4/4] 推送到GitHub...${NC}"
git push
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=====================================${NC}"
    echo -e "${GREEN}✓ 成功推送到GitHub!${NC}"
    echo -e "${GREEN}=====================================${NC}"
    echo ""
    echo -e "查看仓库: ${YELLOW}https://github.com/xingke2023/insurance_broker${NC}"
else
    echo -e "${RED}✗ 推送失败${NC}"
    exit 1
fi
