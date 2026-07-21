---
name: fastapi-middleware
description: "FastAPI/Starlette middleware: what it is, the onion execution model, how to determine inner vs outer layer, auth patterns, and reproducible TestClient demos. Encodes the very common registration-order mistake (last-registered = outermost = runs first in request phase)."
version: 1.0.0
author: Hermes Agent
tags: [fastapi, starlette, middleware, python, web, auth]
---

# FastAPI Middleware

Middleware is a layer sitting between every incoming request and your route handlers
(and between every response and the client). It runs for ALL routes on the app — it does
not matter whether the route function is defined above or below the middleware in code.

## The #1 confusion: registration order ≠ execution order

**WRONG intuition (easy to fall into):** "the first-registered middleware runs first in the
request phase."

**REALITY (verified by actually running it):** The LAST-registered middleware is the
**outermost** layer. It runs **FIRST** in the request phase and **LAST** in the response phase.

Why: under the hood Starlette inserts each new middleware at list index 0, then wraps the
app with `reversed(...)`, so the last-registered ends up outermost.

Real TestClient output (middleware A registered first, B registered second):
```
[B] 请求阶段：进来啦~        <- B registered LAST  -> outermost -> request FIRST
[A] 请求阶段：进来啦~        <- A registered FIRST -> inner
[路由] 真正干活中...
[A] 响应阶段：出去啦~        <- inner finishes response first
[B] 响应阶段：出去啦~        <- outermost finishes response LAST
```

Mnemonic for the user: **"后写的是外层；请求先进外层，响应后出外层。"**
(translation: the one written LOWER is the outer layer; requests enter the outer layer
first, responses leave the outer layer last.)

## How to determine inner/outer
- **By code:** the middleware written LOWER (registered later) is the outer layer.
- **By test:** print one line in the request phase of each; whoever prints first is outer.

## Key facts
- Route functions defined ABOVE or BELOW a middleware are ALL wrapped — code position only
  affects execution ORDER, never whether the middleware runs.
- `await call_next(request)` is what passes the request to the next layer. If you `return`
  WITHOUT calling `call_next`, the request never reaches the route (used to intercept /
  return 401 / 403). This is the mechanism for blocking.
- `request.state.x = value` carries data from middleware into the route handler.
- Multiple middlewares form an onion. Inside a middleware, short-circuit specific paths
  (e.g. `if request.url.path in ("/docs", "/openapi.json"): return await call_next(request)`)
  to skip auth for public endpoints.
- Middleware does NOT know per-route requirements. For fine-grained "this route needs
  admin, that route is public" use `Depends` instead (see below).

## Middleware vs Depends
| Use middleware when... | Use `Depends` when... |
|---|---|
| Global concern across ALL routes (request logging, global auth, CORS, rate-limit) | Per-route / per-permission control (some routes public, some admin-only) |
| You want to intercept BEFORE the route runs, unconditionally | You want the framework to enforce which routes require auth |

## Reproducible demo
See `references/demo.md` for two copy-pasteable TestClient scripts (auth + ordering) with
their real outputs. Run them with `python demo_middleware.py` / `python demo_order.py`.

## Pitfalls
- NEVER tell the user "first-registered runs first." It is the opposite — see above.
- Do not print secret values (tokens, API keys) when demoing; print `len(value)` only.
- A middleware that returns before `call_next` means downstream middlewares AND the route
  never run — so a logging middleware placed OUTER than an auth middleware will still log
  rejected requests, while one placed INNER will not (the auth block short-circuits first).
- Prefer `Depends` for per-route auth; middleware auth is coarse (all-or-nothing unless you
  hand-code path whitelists).
