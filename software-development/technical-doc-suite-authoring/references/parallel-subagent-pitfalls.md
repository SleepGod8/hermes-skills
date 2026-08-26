# 并行子代理生成文档的已知陷阱

## 陷阱 P9：参考项目角色/枚举污染

**场景**：新项目文档套件参照已有项目格式生成（如"参照 ai-talent-platform 为 job-coach-platform 写"）。

**问题**：并行子代理读取参考文档时，不仅参考格式，还**直接复制了角色名、枚举值、表名**到新文档。

**实际案例**（2026-08-26）：
- REQUIREMENTS 定义角色：`admin/consultant/job_seeker`
- 03-test-cases.md 子代理直接从 ai-talent-platform 复制了 `candidate/employee/hr`
- 05-database-design.md 表中 role 字段写 `admin/consultant/client`（混淆了数据角色与 RBAC 角色）
- 06-detail-design.md 谈判模拟角色写 `ai_hr/client` 而非 `ai_hr/job_seeker`

**根因**：
1. delegate_task 子代理无共享上下文，独立读参考文档
2. 子代理无法区分"格式模板"与"项目内容"
3. REQUIREMENTS 没有在子代理 context 中被显式引用为权威源

**防范措施**：
1. REQUIREMENTS 必须先完成且冻结，再启动并行子代理
2. 每个子代理 context 显式声明：
   - 新项目枚举清单（如 `roles = admin/consultant/job_seeker`）
   - **禁止列表**（如"禁止使用 candidate/employee/hr"）
   - "参考项目仅参考格式/结构，内容以 REQUIREMENTS 为准"
3. 生成后 grep 审计：
   ```bash
   # 检查新项目文档中是否残留参考项目角色名
   grep -rnP '\b(candidate|employee|hr)\b' docs/*.md DEVELOPMENT_GUIDE.md
   ```
4. 发现残留后用 regex replace 修复（注意语义：谈判场景中的 "hr" 可能是 AI 扮演的 HR 角色，需单独处理）

---

## 陷阱 P10：子代理写入路径笔误

**场景**：delegate_task context 中路径拼错（如 `E:\Hermes works\` 而非 `E:\Hermes workspace\`）。

**问题**：子代理按错误路径写入文件，后续 `find`/`search_files` 在正确目录找不到文件。

**实际案例**（2026-08-26）：
- 4个子代理任务的 context 中路径含 `E:\Hermes works\job-coach-platform\`
- 2个子代理正确写入 `E:\Hermes workspace\job-coach-platform\`
- 文件实际落在两个不同目录下

**防范措施**：
1. context 中路径从用户请求精确复制，不要手打
2. 生成后立即 `search_files(pattern='*.md', target='files')` 验证
3. 错位修复：
   ```bash
   cp "E:/Hermes works/job-coach-platform/DEVELOPMENT_GUIDE.md" "E:/Hermes workspace/job-coach-platform/"
   rm -rf "E:/Hermes works/job-coach-platform"
   ```

---

## 一致性修复脚本模板

当发现角色污染时，可用以下 regex 脚本批量修复：

```python
from hermes_tools import read_file, write_file
import re

path = "docs/03-test-cases.md"
r = read_file(path)
content = r["content"]

# 去除行号（read_file 格式是 "NUM|CONTENT"）
lines = [line.partition("|")[2] if "|" in line else line for line in content.split("\n")]
content = "\n".join(lines)

# 角色替换（注意顺序：长模式先替换）
replacements = [
    (r'\bcandidate_jwt\b', 'job_seeker_jwt'),
    (r'\bcandidate_id\b', 'job_seeker_id'),
    (r'(?<!\w)candidate(?!\w)', 'job_seeker'),
    (r'(?<!\w)employee(?!\w)', 'job_seeker'),
    (r'(?<!\w)hr(?=/)', 'consultant'),   # hr/ 路径
    (r'(?<!\w)hr(?=\b)', 'consultant'),   # 独立 hr
]
for old, new in replacements:
    content = re.sub(old, new, content)

# 去重修复
content = content.replace("job_seeker_id_id", "job_seeker_id")

write_file(path, content)
```
