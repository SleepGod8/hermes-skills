# 贡献者口径核查：侧边栏 4 人 vs API 3 人（dsh-liang-skin 实测案例 2026-08）

用户质疑：「https://github.com/kingOfSoySauce/dsh-liang-skin 页面 Contributors 显示 4 人，体检工具只统计 3 人，统计错了？」

## 结论

工具没统计错。GitHub 六个数据源交叉验证：

| 数据源 | 人数 | 口径 |
|--------|------|------|
| REST `GET /contributors`（不带 anon） | 3 | 按账号聚合提交者 |
| GraphQL `history.nodes[].author.user.login` 去重 | 3 | 同上 |
| Insights → Contributors 图表页 | 3 | 排除 merge commits 的提交者 |
| **主页右侧边栏「Contributors (4)」** | **4** | **宽口径展示数（虚标）** |

侧边栏多出的第 4 人 = **Lichtspektrum**，在目标仓库**完全没有贡献痕迹**：
- 34 条 commit 的 author/committer 账号与邮箱：无他
- `search/commits?q=repo:...+author:Lichtspektrum` 和 `+committer:Lichtspektrum` → total=0
- PR 列表（state=all，3 个）与 issues 列表（2 个）：无他
- 非 fork 关系：dsh-liang-skin `fork:false`；kingOfSoySauce 也没 fork 过 Lichtspektrum 的仓库
- 邮箱零交集：Lichtspektrum 在自己仓库用的邮箱（sebastiiiiiiii@gmail.com / huanghuaishan@126.com / 64409687+Lichtspektrum@users.noreply.github.com）与目标 repo 全部提交邮箱完全不同
- 他的 events 里对该 repo 只有 `WatchEvent started`（= star 过）

**他上榜的唯一原因**：README 里写了「灵感与素材来源：Lichtspektrum/liang-intensity-calibrator」（素材致谢）。

## 关键教训

1. **不要假设侧边栏多出来的人 = 「通过 commit email 关联的提交者」**。旧版 skill 曾这样写，实测推翻：Lichtspektrum 邮箱与仓库提交邮箱零交集。
2. 侧边栏 Contributors 是 GitHub 的展示口径，会包含 README 致谢/star 过的账号。**真实提交者数以 API 三方一致为准**。
3. 被质疑时不要只抛结论，要交证据链（下表 probes），并解释「侧边栏把素材致谢人也计入了」。

## 验证 probes（curl，带 GITHUB_PERSONAL_ACCESS_TOKEN）

```bash
H="Authorization: Bearer $GITHUB_PERSONAL_ACCESS_TOKEN"
# 1. contributors 官方口径
curl -s -H "$H" "https://api.github.com/repos/{o}/{r}/contributors?per_page=100"
# 2. commits 聚合 author/committer 账号 + 邮箱
curl -s -H "$H" "https://api.github.com/repos/{o}/{r}/commits?per_page=100"
# 3. commit 搜索（查特定人）
curl -s -H "$H" -H "Accept: application/vnd.github+json" \
  "https://api.github.com/search/commits?q=repo:{o}/{r}+author:{login}"
# 4. PR / issues 全量
curl -s -H "$H" "https://api.github.com/repos/{o}/{r}/pulls?state=all&per_page=100"
curl -s -H "$H" "https://api.github.com/repos/{o}/{r}/issues?state=all&per_page=100"
# 5. fork 双向 + repo 元数据
curl -s -H "$H" "https://api.github.com/repos/{o}/{r}/forks?per_page=100"
curl -s -H "$H" "https://api.github.com/users/{login}/repos?per_page=100"
curl -s -H "$H" "https://api.github.com/repos/{o}/{r}"   # 看 fork/parent
# 6. 用户公开事件（找对该 repo 的 Push/PR/Fork 事件）
curl -s -H "$H" "https://api.github.com/users/{login}/events/public?per_page=100"
# 7. 嫌疑人在自己仓库的提交邮箱（对比用）
curl -s -H "$H" "https://api.github.com/repos/{login}/{his-repo}/commits?per_page=100"
```

GraphQL 交叉验证：

```graphql
{ repository(owner:"{o}", name:"{r}") {
    defaultBranchRef { target { ... on Commit {
      history(first:100) { totalCount nodes { author { email user { login } } } } } } } } }
```

## 坑：未认证 curl 会限流

本机匿名打 GitHub API 会命中 `API rate limit exceeded for <公网IP>`。**所有验证请求必须带 token**，不要先匿名试。
