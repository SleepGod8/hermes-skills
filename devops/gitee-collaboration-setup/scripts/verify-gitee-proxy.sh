#!/usr/bin/env bash
# 验证 Gitee 是否绕过 git 代理直连（Windows git-bash 可用）
# 用法: bash verify-gitee-proxy.sh
set -u

echo "=== 1. 配置 key 是否存在 ==="
if git config --global --get http.https://gitee.com.proxy >/dev/null 2>&1; then
  echo "OK: http.https://gitee.com.proxy 存在 (exit 0)"
else
  echo "FAIL: key 不存在 — 未配置 Gitee 绕代理"
  echo "修复: 编辑 ~/.gitconfig, 添加:"
  echo "  [http \"https://gitee.com\"]"
  echo "      proxy ="
fi

echo ""
echo "=== 2. 真实连接测试 (GIT_TRACE_CURL) ==="
LOG=$(GIT_TRACE_CURL=1 git ls-remote https://gitee.com/mirrors/gitee.git HEAD 2>&1)
echo "$LOG" | grep -iE "proxy tunnel|Established connection|Could not|fatal" | head -10

echo ""
echo "=== 3. 判定 ==="
if echo "$LOG" | grep -qE "proxy tunnel|port 12450"; then
  echo "❌ 仍在走代理（若 12450 是你本地代理端口，说明绕开未生效）"
elif echo "$LOG" | grep -qE "Established connection to gitee.com"; then
  echo "✅ 直连 Gitee 成功"
else
  echo "⚠️ 无法确认（网络或仓库地址问题），查看上方 trace"
fi
