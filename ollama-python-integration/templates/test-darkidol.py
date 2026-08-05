"""
Ollama darkidol 模型测试脚本

模型信息：
- 名称: dagbs/darkidol-llama-3.1-8b-instruct-1.0-uncensored
- 别名: darkidol
- 大小: 4.9 GB
- 参数: 8B
- 量化: Q4_K_M
- 上下文: 131072 (推荐降低到4096或2048以节省内存)

内存配置：
- 系统: 32GB RAM
- 可用: ~10GB
- 8B模型需要: ~16GB (默认131072上下文)
- 解决方案: 使用 num_ctx=2048 或 4096

使用方法：
python test_darkidol.py
python test_darkidol.py --prompt "你好"
python test_darkidol.py --prompt "讲个故事" --num_ctx 2048
python test_darkidol.py --prompt "你好" --stream
"""

import argparse
import requests
import json

OLLAMA_API = "http://localhost:11434/api"

def generate(prompt: str, num_ctx: int = 4096) -> str:
    """使用generate API生成文本"""
    url = f"{OLLAMA_API}/generate"
    data = {
        "model": "darkidol",
        "prompt": prompt,
        "options": {
            "num_ctx": num_ctx
        }
    }
    response = requests.post(url, json=data, stream=True, timeout=120)
    full_response = ""
    for line in response.iter_lines():
        if line:
            chunk = json.loads(line)
            if chunk.get("response"):
                full_response += chunk["response"]
    return full_response

def chat(messages: list, num_ctx: int = 4096) -> str:
    """使用chat API进行对话"""
    url = f"{OLLAMA_API}/chat"
    data = {
        "model": "darkidol",
        "messages": messages,
        "options": {
            "num_ctx": num_ctx
        }
    }
    response = requests.post(url, json=data, timeout=120)
    result = response.json()
    return result.get("message", {}).get("content", "")

def stream_chat(messages: list, num_ctx: int = 4096):
    """流式输出对话"""
    url = f"{OLLAMA_API}/chat"
    data = {
        "model": "darkidol",
        "messages": messages,
        "stream": True,
        "options": {
            "num_ctx": num_ctx
        }
    }
    response = requests.post(url, json=data, stream=True, timeout=120)
    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            if data.get("message", {}).get("content"):
                print(data["message"]["content"], end="", flush=True)

def main():
    parser = argparse.ArgumentParser(description="测试darkidol模型")
    parser.add_argument("--prompt", "-p", default="你好，请简单介绍一下自己", help="测试提示词")
    parser.add_argument("--num_ctx", "-c", type=int, default=4096, help="上下文长度 (默认4096)")
    parser.add_argument("--stream", "-s", action="store_true", help="流式输出")
    args = parser.parse_args()

    print(f"=" * 50)
    print(f"🤖 darkidol 模型测试")
    print(f"=" * 50)
    print(f"模型: dagbs/darkidol-llama-3.1-8b-instruct-1.0-uncensored")
    print(f"大小: 4.9 GB")
    print(f"参数: 8B (Q4_K_M)")
    print(f"上下文: {args.num_ctx}")
    print(f"=" * 50)
    print(f"\n提示词: {args.prompt}\n")

    if args.stream:
        print("流式输出:", end=" ", flush=True)
        stream_chat([{"role": "user", "content": args.prompt}], args.num_ctx)
        print()
    else:
        result = generate(args.prompt, args.num_ctx)
        print(f"回复: {result}")

    print("\n✅ 测试完成")

if __name__ == "__main__":
    main()
