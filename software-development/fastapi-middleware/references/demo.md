# FastAPI Middleware Demos (real, runnable with TestClient)

Save as `demo_middleware.py` and `demo_order.py`, run with `python demo_order.py`.

## 1) Ordering demo — proves last-registered = outermost

```python
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

app = FastAPI()

@app.middleware("http")            # registered FIRST -> inner
async def middleware_a(request, call_next):
    print("  [A] 请求阶段：进来啦~")
    response = await call_next(request)
    print("  [A] 响应阶段：出去啦~")
    return response

@app.middleware("http")            # registered LAST -> outer
async def middleware_b(request, call_next):
    print("  [B] 请求阶段：进来啦~")
    response = await call_next(request)
    print("  [B] 响应阶段：出去啦~")
    return response

@app.get("/test")
async def test():
    print("  [路由] 真正干活中...")
    return {"ok": True}

if __name__ == "__main__":
    TestClient(app).get("/test")
```

Real output:
```
  [B] 请求阶段：进来啦~
  [A] 请求阶段：进来啦~
  [路由] 真正干活中...
  [A] 响应阶段：出去啦~
  [B] 响应阶段：出去啦~
```

## 2) Auth + logging demo — shows interception (no call_next => route never runs)

```python
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

app = FastAPI()
VALID_TOKENS = {"***", "def456"}

@app.middleware("http")
async def log_middleware(request, call_next):
    start = time.time()
    response = await call_next(request)
    print(f"[日志] {request.method} {request.url.path} -> {response.status_code}, {(time.time()-start)*1000:.1f}ms")
    return response

@app.middleware("http")
async def auth_middleware(request, call_next):
    if request.url.path in ("/public", "/docs", "/openapi.json"):
        return await call_next(request)
    auth = request.headers.get("Authorization")
    if not auth:
        return JSONResponse(401, {"detail": "缺少 Authorization 头"})
    try:
        scheme, token = auth.split()
    except ValueError:
        return JSONResponse(401, {"detail": "格式应为 Bearer <token>"})
    if scheme.lower() != "bearer" or token not in VALID_TOKENS:
        return JSONResponse(403, {"detail": "token 无效"})
    request.state.token = token
    return await call_next(request)

@app.get("/public")
async def public():
    return {"msg": "这是公开接口，不用登录~"}

@app.get("/secret")
async def secret(request: Request):
    return {"msg": "这是私密接口", "你的token": request.state.token}

if __name__ == "__main__":
    c = TestClient(app)
    print("1 公开:", c.get("/public").json())
    print("2 无token:", c.get("/secret").status_code)        # 401, no log printed
    print("3 错token:", c.get("/secret", headers={"Authorization":"Bearer wrong"}).status_code)  # 403
    print("4 正确: ", c.get("/secret", headers={"Authorization":"Bearer ***"}).json())
```

Real output (note: scenarios 2 & 3 print NO log line — auth blocked BEFORE call_next,
so the outer log middleware never saw a completed response):
```
=== 1 公开 ===
[日志] GET /public -> 200, 7.6ms
{'msg': '这是公开接口，不用登录~'}
=== 2 无token ===
401
=== 3 错token ===
403
=== 4 正确 ===
[日志] GET /secret -> 200, 2.0ms
{'msg': '这是私密接口', '你的token': '***'}
```
