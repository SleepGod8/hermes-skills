# 实例：GitHub 仓库体检工具（2026-08）

实测项目：`E:/Hermes workspace/github-repo-health-checker/`（FastAPI + ECharts 5.5 本地化）

## 端点清单（GitHub REST API v3）

| 用途 | 端点 | 关键参数/header |
|------|------|-----------------|
| 仓库元数据 | `GET /repos/{owner}/{repo}` | — |
| 语言分布 | `GET /repos/{owner}/{repo}/languages` | 返回 {lang: bytes}，算百分比 |
| 贡献者数 | `GET /repos/{owner}/{repo}/contributors` | per_page=1 + Link last |
| Open PR 数 | `GET /repos/{owner}/{repo}/pulls?state=open` | per_page=1 + Link last |
| Release 数 | `GET /repos/{owner}/{repo}/releases` | per_page=1 + Link last |
| 提交活跃 | `GET /repos/{owner}/{repo}/stats/commit_activity` | 52 周数组，202 重试 |
| 最近提交 | `GET /repos/{owner}/{repo}/commits` | per_page=10 |
| Star 趋势 | `GET /repos/{owner}/{repo}/stargazers` | Accept: star+json，需 Starring scope |
| README | `GET /repos/{owner}/{repo}/readme` | Accept: application/vnd.github.raw → 纯文本 |

## 实测数据（fastapi/fastapi，2026-08-19）

- stars=101,691 | forks=9,796 | open_issues=74 | contributors=906 | open_prs=73 | releases=300
- languages: Python/JavaScript/Shell/HTML/CSS（5 种）
- commit_activity: 52 周全量返回
- 匿名 API 限流 60/h；带 token 5000/h

## payload 结构（前端契约）

```json
{
  "ok": true,
  "repo": { "full_name", "description", "stars", "forks", "watchers",
            "open_issues", "open_prs", "contributors", "releases_count",
            "license", "primary_language", "created_at", "updated_at",
            "pushed_at", "size_kb", "archived", "fork", "default_branch",
            "topics", "has_issues", "has_wiki", "homepage" },
  "languages": [{"name", "bytes", "percent"}],
  "commit_activity": [{"week", "total"}],
  "recent_commits": [{"sha", "message", "author", "date"}],
  "star_trend": [{"date", "stars"}],
  "latest_release": {"tag", "name", "published_at"},
  "readme_excerpt": "...",
  "ai_score": {"score", "grade", "summary", "pros", "cons", "suggestions", "model"},
  "meta": {"github_api_calls": [...], "cache": false, "ai_elapsed_ms": 28960}
}
```

## 踩坑过程（按时间线）

1. **stargazers 403**：`GITHUB_PERSONAL_ACCESS_TOKEN` 是 fine-grained token 无 Starring scope → 403 "Resource not accessible by personal access token"。最初误判为限流 → 改为读 `x-ratelimit-remaining` 头分流。
2. **匿名也 401**：降级匿名重试 stargazers → 401 "Requires authentication"。官方路径彻底堵死 → 引入 star-history.com SVG 代理。
3. **star-history JSON API 404**：`api.star-history.com/api/v1/repos?name=...` 与 `/api/repos?...` 都 404；**只有 `/svg?repos=owner/repo&type=Date` 可用**（ungh.cc/stars 也 404，starchart.cc 限流 400）。SVG 是白底 → 前端包白底容器。
4. **Zhipu 429**：glm-4.6v-flash 返回 429 code 1305 "访问量过大"（记忆已知坑）→ glm-4.5 提到首位，重试 2 次。
5. **ASLNet 无 gpt-4o-mini**：404 model_not_found → 换 gpt-5.4/gpt-5.5（记忆：ASLNet=gpt 纯 pro 池，ASLNetPlus=gpt-plus 池）。
7. **contributors 计数虚高（anon=true）**：`count_pages(client, "/repos/{owner}/{repo}/contributors", {"anon": "true"})` 把匿名提交者（无账号、只有 email，API login=ANON）也算进页数 → dsh-reasoning-effort 报 3 人，网页侧边栏显示 2（HanaAyane + Howardzhangdqs）。**修法：去掉 `anon=true`**（2026-08-19 实测：改后 3→2 与网页一致）。
8. **网页侧边栏 ≠ API contributors 口径**：dsh-liang-skin 网页显示 Contributors 4（含 Lichtspektrum），API 列表只有 3（kingOfSoySauce/applex250/jiaererw）；dsh-meme 网页 2（含 cursoragent=Cursor Agent 自动提交），API 只有 1（yyh-001）。网页按 commit email 关联账号聚合，API 按提交账号聚合——**以 API 为准**，向用户解释口径差异即可，勿追平网页数字。
9. **用户质疑「AI 是不是编数」**：AI 文案照抄 payload，非编造。本次用户查 3 个仓库 contributor 得 2/2/4（commit author 去重口径），工具存 3/3/2（anon 口径），AI cons「仅 3 名贡献者」即照抄。修复数据后重跑 `/api/score`，文案自动变「贡献者仅 2 人」。
10. **修数据源 bug 必须清磁盘缓存**：`.gh_cache/`（6h）`.ai_cache/`（24h）不删会继续吐旧值。`rm -rf .gh_cache .ai_cache` → 重启 → 重测。本次 3 个仓库全部重新拉取并复核通过。
7. **AI 耗时**：首次 glm-4.6v-flash 重试 3 次时接口总耗时 99.7s → 减到 2 次 + glm-4.5 优先后降到 40s（AI 部分 29s）。

## 可复用代码片段

```python
# Link header 末页解析
import re
def parse_link_last(link_header):
    if not link_header: return None
    m = re.search(r'page=(\d+)>; rel="last"', link_header)
    return int(m.group(1)) if m else 1

# 403 分流
if r.status_code == 403:
    remaining = r.headers.get("x-ratelimit-remaining", "1")
    if remaining == "0":
        raise HTTPException(429, "限流")
    # 权限问题 → 降级匿名重试一次
    last_err = "permission"; continue

# Hermes config 自动发现 Zhipu key
re.search(r'name:\s*ZhipuGLM.*?api_key:\s*(\S+)', text, re.S)
```

## 缓存策略（P0+P1 后，2026-08-19）

- 内存 dict + TTL 600s，key = `owner/repo|use_ai`，超过 200 条淘汰最旧
- **磁盘缓存（重启不丢）**：`.gh_cache/<full_name 的 / 替换成 __>.json`（GitHub 数据，TTL `GH_CACHE_TTL` 默认 6h）；`.ai_cache/<full_name>.json`（AI 评分，TTL `AI_CACHE_TTL` 默认 24h）
- **三级取数**：内存 → 磁盘(6h) → GitHub API（`load_repo_data`）；`/api/score` 优先吃缓存不重复拉 GitHub
- star-history SVG 单独缓存 key = `starh|owner/repo`
- ⚠️ 运行时缓存目录（`.gh_cache/ .ai_cache/`）日后打包/交付必须排除
