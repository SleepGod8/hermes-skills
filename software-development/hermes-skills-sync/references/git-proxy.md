# Git via Proxy (China / Restricted Networks)

When GitHub is unreachable from China, configure git to use a local proxy.

## Configure Git Proxy

```bash
# Set proxy for git
git config --global http.proxy http://127.0.0.1:PORT
git config --global https.proxy http://127.0.0.1:PORT
```

## Common Proxy Ports

| Proxy | Port |
|-------|------|
| Clash | 7890 |
| V2Ray | 10809 |
| Custom | varies (ask user) |

## Test Proxy

```bash
curl -s --max-time 5 -x http://127.0.0.1:PORT https://github.com -o /dev/null -w "%{http_code}"
# Should return: 200
```

## Remove Proxy (when not needed)

```bash
git config --global --unset http.proxy
git config --global --unset https.proxy
```

## Proxy-free Alternatives

When proxy is unavailable, try these mirrors (YMMV):
- `https://ghproxy.com/https://github.com/...` — GitHub mirror
- `https://gitclone.com/github.com/...` — Git clone mirror
- npm: `--registry=https://registry.npmmirror.com`

Note: mirrors often go offline. A local proxy is the most reliable approach.

## Cloning with Proxy

```bash
# Set proxy first, then clone
git config --global http.proxy http://127.0.0.1:12450
git config --global https.proxy http://127.0.0.1:12450
git clone https://github.com/User/repo.git
```
