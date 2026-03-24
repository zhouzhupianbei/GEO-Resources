#!/usr/bin/env python3
"""
微信公众号文章检索脚本
搜索 GEO 相关文章并更新资源文档
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

# 输出目录
OUTPUT_DIR = Path("/Users/lvguofei/workspaces/openclaw/GEO-Resources")
MEMORY_DIR = OUTPUT_DIR / "memory"
RESOURCES_DIR = OUTPUT_DIR / "resources"

# 搜索关键词
GEO_KEYWORDS = [
    "GEO 大模型",
    "生成式引擎优化",
    "GEO 搜索优化",
    "AI 搜索优化",
    "大模型 SEO",
    "生成式搜索",
    "AIGC 优化",
    "LLM 内容优化",
]


def search_wechat_articles(keyword: str, limit: int = 10) -> list:
    """搜索微信公众号文章"""
    try:
        # 使用 wechat-article-search 技能
        cmd = ['python3', '-c', f'''
import sys
sys.path.insert(0, "/Users/lvguofei/.openclaw/workspace/skills/wechat-article-search-0.1.0")
# 简化搜索，直接返回模拟数据
print("搜索：{keyword}")
''']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        print(result.stdout)
    except Exception as e:
        print(f"搜索失败 {keyword}: {e}")
    
    # 由于微信搜索需要特定技能，这里先返回占位数据
    # 实际使用时会调用 wechat-article-search 技能
    return []


def search_with_skill(keyword: str) -> list:
    """使用 wechat-article-search 技能搜索"""
    # 这个函数会在 cron 任务中通过 OpenClaw 调用
    # 返回格式：
    return [
        {
            'title': f'{keyword}相关文章',
            'account': 'AI 前沿观察',
            'publish_date': datetime.now().strftime('%Y-%m-%d'),
            'url': 'https://mp.weixin.qq.com/s/xxx',
            'summary': f'关于{keyword}的深度解析...',
        }
    ]


def format_markdown_list(articles: list) -> str:
    """格式化为 Markdown 列表"""
    if not articles:
        return "暂无数据\n"
    
    lines = []
    for article in articles[:30]:  # 最多显示 30 篇
        lines.append(
            f"- **[{article['title']}]({article['url']})**\n"
            f"  - 公众号：{article.get('account', '未知')}\n"
            f"  - 发布：{article.get('publish_date', '未知')}\n"
            f"  - 摘要：{article.get('summary', '')[:80]}..."
        )
    
    return "\n".join(lines) + "\n"


def update_wechat_resources(articles: list = None):
    """更新微信资源文档"""
    print(f"🔍 开始检索微信公众号文章...")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if articles is None:
        articles = []
        # 搜索多个关键词
        for keyword in GEO_KEYWORDS:
            print(f"  搜索：{keyword}")
            # 实际会调用 wechat-article-search 技能
            # 这里先留空，由 cron 任务处理
            pass
    
    print(f"\n📊 找到 {len(articles)} 篇文章")
    
    # 生成 Markdown 内容
    markdown_content = f"""# 微信公众号文章精选

> 自动收集的 GEO 相关优质文章

最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 📰 最新文章

{format_markdown_list(articles) if articles else "待更新...\n"}

## 📚 分类文章

### GEO 基础
<!-- 基础概念类文章 -->

### 实战技巧
<!-- 实操类文章 -->

### 案例分析
<!-- 案例研究类文章 -->

### 工具教程
<!-- 工具使用类文章 -->

---

## 📝 收录标准

- 内容质量高，有实操价值
- 作者有相关经验背书
- 发布时间在 1 年内
- 阅读量和互动较好

## 🔄 更新说明

每日凌晨自动检索更新，如需手动刷新请运行：
```bash
python3 scripts/update-wechat.py
```
"""
    
    # 写入文件
    output_file = RESOURCES_DIR / "wechat-articles.md"
    output_file.write_text(markdown_content, encoding='utf-8')
    print(f"✅ 已更新：{output_file}")
    
    # 保存更新记录
    if articles:
        save_update_record(articles)
    
    return articles


def save_update_record(articles: list):
    """保存更新记录"""
    MEMORY_DIR.mkdir(exist_ok=True)
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    record_file = MEMORY_DIR / f"wechat-updates-{date_str}.md"
    
    content = f"""# 微信文章更新记录 - {date_str}

更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 新增文章

"""
    
    for article in articles[:20]:
        content += f"- [{article['title']}]({article['url']}) - {article.get('account', '')}\n"
    
    content += f"\n## 统计\n\n总计：{len(articles)} 篇文章\n"
    
    record_file.write_text(content, encoding='utf-8')
    print(f"📝 已保存记录：{record_file}")


def main():
    """主函数"""
    print("=" * 60)
    print("🔍 GEO 微信公众号文章检索")
    print("=" * 60)
    
    articles = update_wechat_resources()
    
    print("\n" + "=" * 60)
    print("✅ 检索完成")
    print("=" * 60)
    
    return articles


if __name__ == '__main__':
    main()
