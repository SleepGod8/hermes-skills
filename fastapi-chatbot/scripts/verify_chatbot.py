#!/usr/bin/env python3
"""
FastAPI 多轮对话机器人 - 验证脚本
测试所有核心功能
"""

import requests
import json
import sys
import time

BASE_URL = "http://localhost:8090"

def test_health():
    """测试健康检查"""
    r = requests.get(f"{BASE_URL}/health", timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert "providers" in data
    print("✅ 健康检查通过")
    return data

def test_providers():
    """测试提供商列表"""
    r = requests.get(f"{BASE_URL}/providers", timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert "aslnet" in data
    print("✅ 提供商列表获取成功")
    return data

def test_chat(provider="aslnet", model="gpt-5.5"):
    """测试普通对话"""
    full_model = f"{provider}-{model}"
    r = requests.post(f"{BASE_URL}/chat", json={
        "message": "你好，请用一句话介绍你自己",
        "model": full_model
    }, timeout=30)
    assert r.status_code == 200
    data = r.json()
    assert "message" in data
    assert len(data["message"]) > 0
    print(f"✅ {full_model} 对话正常: {data['message'][:50]}...")
    return data

def test_multiturn():
    """测试多轮对话"""
    sid = "test_multiturn"
    r1 = requests.post(f"{BASE_URL}/chat", json={
        "message": "第一次对话",
        "session_id": sid,
        "model": "aslnet-gpt-5.5"
    }, timeout=30)
    r2 = requests.post(f"{BASE_URL}/chat", json={
        "message": "第二次对话",
        "session_id": sid,
        "model": "aslnet-gpt-5.5"
    }, timeout=30)
    assert r1.status_code == 200 and r2.status_code == 200
    print("✅ 多轮对话正常")
    return sid

def test_persistence():
    """测试持久化存储"""
    r = requests.get(f"{BASE_URL}/sessions", timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert data["count"] >= 1
    print(f"✅ 持久化存储正常，共 {data['count']} 个会话")
    return data

def test_stream():
    """测试流式输出"""
    r = requests.post(f"{BASE_URL}/chat/stream", json={
        "message": "流式测试",
        "model": "aslnet-gpt-5.5"
    }, timeout=30)
    assert r.status_code == 200
    chunks = list(r.iter_lines())
    assert len(chunks) > 0
    print(f"✅ 流式输出正常，共 {len(chunks)} 个 chunk")

def test_rag_flow():
    """测试 RAG 流程图"""
    r = requests.get(f"{BASE_URL}/rag-flow", timeout=5)
    assert r.status_code == 200
    assert "RAG" in r.text
    print("✅ RAG 流程图页面正常")

def cleanup():
    """清理测试会话"""
    r = requests.get(f"{BASE_URL}/sessions", timeout=5)
    sessions = r.json()["sessions"]
    for sid in sessions:
        requests.delete(f"{BASE_URL}/session/{sid}")
    print(f"✅ 已清理 {len(sessions)} 个测试会话")

def main():
    print("=" * 50)
    print("🧪 FastAPI 多轮对话机器人 - 验证测试")
    print("=" * 50)
    
    tests = [
        ("健康检查", test_health),
        ("提供商列表", test_providers),
        ("GPT-5.5 对话", lambda: test_chat("aslnet", "gpt-5.5")),
        ("GPT-5.6-Sol 对话", lambda: test_chat("aslnet", "gpt-5.6-sol")),
        ("多轮对话", test_multiturn),
        ("持久化存储", test_persistence),
        ("流式输出", test_stream),
        ("RAG 流程图", test_rag_flow),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {name}: {e}")
            failed += 1
    
    print("=" * 50)
    print(f"📊 结果: {passed} 通过, {failed} 失败")
    print("=" * 50)
    
    # 清理测试数据
    cleanup()
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
