#!/bin/bash
# GEO 资源库自动同步脚本
# 每天凌晨 2:20 运行

set -e

SCRIPT_DIR="/Users/lvguofei/workspaces/openclaw/GEO-Resources"
LOG_FILE="$SCRIPT_DIR/memory/auto-sync.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== GEO 资源库自动更新开始 ==="

cd "$SCRIPT_DIR"

# 1. 更新 GitHub 项目
log "🔍 检索 GitHub 项目..."
python3 scripts/update-github.py 2>&1 | tee -a "$LOG_FILE"

# 2. 更新微信文章（通过 OpenClaw 技能）
log "📰 检索微信公众号文章..."
python3 scripts/update-wechat.py 2>&1 | tee -a "$LOG_FILE"

# 3. Git 提交更新
log "📦 提交 Git 更新..."
if git status --porcelain | grep -q "."; then
    git add .
    git commit -m "chore: 自动更新 GEO 资源 [$(date '+%Y-%m-%d')]"
    git push origin main 2>&1 | tee -a "$LOG_FILE" || log "⚠️ Git push 失败，可能需要手动处理"
else
    log "ℹ️  无变更，跳过提交"
fi

log "=== GEO 资源库自动更新完成 ==="
