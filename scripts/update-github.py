#!/usr/bin/env python3
"""
GitHub 项目检索脚本
搜索 GEO 相关最新项目并更新资源文档
"""

import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

# GitHub API 配置
GITHUB_API = "https://api.github.com/search/repositories"

# 搜索关键词
GEO_KEYWORDS = [
    "GEO generative engine optimization",
    "GEO 大模型搜索优化",
    "AI search optimization",
    "LLM SEO",
    "generative search",
    "AI content optimization",
    "search generative experience",
    "SGE optimization",
]

# 输出目录
OUTPUT_DIR = Path("/Users/lvguofei/workspaces/openclaw/GEO-Resources")
MEMORY_DIR = OUTPUT_DIR / "memory"
RESOURCES_DIR = OUTPUT_DIR / "resources"


def search_github_projects(query: str, sort: str = "stars", order: str = "desc") -> list:
    """搜索 GitHub 项目"""
    params = {
        'q': query,
        'sort': sort,
        'order': order,
        'per_page': 10,
    }
    
    try:
        response = requests.get(GITHUB_API, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get('items', [])
    except Exception as e:
        print(f"搜索失败 {query}: {e}")
        return []


def filter_projects(projects: list, min_stars: int = 50) -> list:
    """过滤项目"""
    filtered = []
    six_months_ago = datetime.now() - timedelta(days=180)
    
    for proj in projects:
        # 检查 stars
        if proj.get('stargazers_count', 0) < min_stars:
            continue
        
        # 检查最近是否更新
        updated_at = datetime.strptime(proj['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
        if updated_at < six_months_ago:
            continue
        
        # 检查是否有文档
        has_docs = proj.get('has_pages', False) or proj.get('homepage')
        
        filtered.append({
            'name': proj['full_name'],
            'description': proj.get('description', '') or '无描述',
            'stars': proj['stargazers_count'],
            'forks': proj['forks_count'],
            'language': proj.get('language', 'Unknown'),
            'url': proj['html_url'],
            'updated_at': proj['updated_at'][:10],
            'has_docs': has_docs,
        })
    
    return filtered


def deduplicate_projects(projects: list) -> list:
    """去重"""
    seen = set()
    unique = []
    
    for proj in projects:
        if proj['name'] not in seen:
            seen.add(proj['name'])
            unique.append(proj)
    
    return unique


def format_markdown_table(projects: list) -> str:
    """格式化为 Markdown 表格"""
    if not projects:
        return "暂无数据\n"
    
    lines = [
        "| 项目 | 描述 | Stars | 语言 | 更新 |",
        "|------|------|-------|------|------|"
    ]
    
    for proj in projects[:20]:  # 最多显示 20 个
        desc = proj['description'][:50] + "..." if len(proj['description']) > 50 else proj['description']
        lines.append(
            f"| [{proj['name']}]({proj['url']}) | {desc} | ⭐{proj['stars']} | {proj['language']} | {proj['updated_at']} |"
        )
    
    return "\n".join(lines) + "\n"


def update_github_resources():
    """更新 GitHub 资源文档"""
    print(f"🔍 开始检索 GitHub 项目...")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_projects = []
    
    # 搜索多个关键词
    for keyword in GEO_KEYWORDS:
        print(f"  搜索：{keyword}")
        projects = search_github_projects(keyword)
        filtered = filter_projects(projects)
        all_projects.extend(filtered)
    
    # 去重和排序
    unique_projects = deduplicate_projects(all_projects)
    unique_projects.sort(key=lambda x: x['stars'], reverse=True)
    
    print(f"\n📊 找到 {len(unique_projects)} 个唯一项目")
    
    # 生成 Markdown 内容
    markdown_content = f"""# GitHub 项目资源

> 自动收集的 GEO 相关优质 GitHub 项目

最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 🔥 热门项目 (按 Stars 排序)

{format_markdown_table(unique_projects)}

## 📊 统计信息

- 总项目数：{len(unique_projects)}
- 平均 Stars: {sum(p['stars'] for p in unique_projects) // max(len(unique_projects), 1)}
- 主要语言：{get_top_languages(unique_projects)}

---

## 📝 收录标准

- ⭐ Stars > 50
- 📅 最近 6 个月有更新
- 📖 有完善的文档
- 🛠️ 可实际使用

## 🔄 更新说明

每日凌晨自动检索更新，如需手动刷新请运行：
```bash
python3 scripts/update-github.py
```
"""
    
    # 写入文件
    output_file = RESOURCES_DIR / "github-projects.md"
    output_file.write_text(markdown_content, encoding='utf-8')
    print(f"✅ 已更新：{output_file}")
    
    # 保存更新记录
    save_update_record(unique_projects)
    
    return unique_projects


def get_top_languages(projects: list) -> str:
    """获取主要语言分布"""
    lang_count = {}
    for proj in projects:
        lang = proj.get('language', 'Unknown')
        lang_count[lang] = lang_count.get(lang, 0) + 1
    
    top_langs = sorted(lang_count.items(), key=lambda x: -x[1])[:3]
    return ", ".join([f"{lang}({count})" for lang, count in top_langs])


def save_update_record(projects: list):
    """保存更新记录"""
    MEMORY_DIR.mkdir(exist_ok=True)
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    record_file = MEMORY_DIR / f"github-updates-{date_str}.md"
    
    content = f"""# GitHub 更新记录 - {date_str}

更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 新增项目

"""
    
    for proj in projects[:10]:
        content += f"- [{proj['name']}]({proj['url']}) - ⭐{proj['stars']} {proj['language']}\n"
    
    content += f"\n## 统计\n\n总计：{len(projects)} 个项目\n"
    
    record_file.write_text(content, encoding='utf-8')
    print(f"📝 已保存记录：{record_file}")


def main():
    """主函数"""
    print("=" * 60)
    print("🔍 GEO GitHub 项目检索")
    print("=" * 60)
    
    projects = update_github_resources()
    
    print("\n" + "=" * 60)
    print("✅ 检索完成")
    print("=" * 60)
    
    return projects


if __name__ == '__main__':
    main()
