#!/usr/bin/env python3
"""
艹，这个脚本测试 ollama 集成是否正常工作
"""
import requests
import json
import sys

def test_ollama_service():
    """测试 ollama 服务是否可用"""
    print("=" * 60)
    print("测试 1: 检查 ollama 服务")
    print("=" * 60)

    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        response.raise_for_status()
        data = response.json()

        print("✓ ollama 服务正常运行")
        print(f"可用模型: {len(data.get('models', []))} 个")

        for model in data.get('models', []):
            name = model.get('name', 'unknown')
            print(f"  - {name}")

        return True
    except Exception as e:
        print(f"✗ ollama 服务连接失败: {e}")
        return False


def test_llm_local_module():
    """测试 llm_local 模块"""
    print("\n" + "=" * 60)
    print("测试 2: 导入 llm_local 模块")
    print("=" * 60)

    try:
        from sweep_autocomplete.autocomplete.llm_local import get_model, generate_completion
        print("✓ llm_local 模块导入成功")

        # 测试 get_model
        print("\n测试 get_model()...")
        model_name = get_model()
        print(f"✓ 模型验证成功: {model_name}")

        return True
    except Exception as e:
        print(f"✗ 模块导入或验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_generate_completion():
    """测试代码补全生成"""
    print("\n" + "=" * 60)
    print("测试 3: 测试代码补全生成")
    print("=" * 60)

    try:
        from sweep_autocomplete.autocomplete.llm_local import generate_completion

        # 简单的测试 prompt
        test_prompt = """def hello_world():
    print("""

        print(f"测试 prompt:\n{test_prompt}")
        print("\n生成补全中...")

        result = generate_completion(
            prompt=test_prompt,
            stop=["\n\n", "def ", "class "],
            max_tokens=50,
            temperature=0.2,
            prefix=""
        )

        text, elapsed_ms, logprobs, finish_reason = result

        print(f"\n✓ 补全生成成功!")
        print(f"耗时: {elapsed_ms}ms")
        print(f"完成原因: {finish_reason}")
        print(f"生成内容:\n{text}")

        return True
    except Exception as e:
        print(f"✗ 补全生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_autocomplete_api():
    """测试完整的 autocomplete API"""
    print("\n" + "=" * 60)
    print("测试 4: 测试 /backend/next_edit_autocomplete API 端点")
    print("=" * 60)

    try:
        payload = {
            "file_path": "test.py",
            "file_contents": "def hello():\n    print(\"",
            "cursor_position": 30,
            "recent_changes": "",
            "file_chunks": [],
            "retrieval_chunks": [],
            "recent_user_actions": []
        }

        print("发送请求到 http://localhost:8081/backend/next_edit_autocomplete")
        print(f"Payload: {json.dumps(payload, indent=2)}")

        response = requests.post(
            "http://localhost:8081/backend/next_edit_autocomplete",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            # 这是流式响应，读取第一行
            lines = response.text.strip().split('\n')
            if lines:
                data = json.loads(lines[0])
                print(f"\n✓ API 调用成功!")
                print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
                return True
            else:
                print("✗ 响应为空")
                return False
        else:
            print(f"✗ API 返回错误: {response.status_code}")
            print(f"响应: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器 (http://localhost:8081)")
        print("提示: 请先启动服务: sweep-autocomplete")
        return False
    except Exception as e:
        print(f"✗ API 调用失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "=" * 60)
    print("Ollama 集成测试")
    print("=" * 60 + "\n")

    results = []

    # 测试 1: ollama 服务
    results.append(("ollama 服务", test_ollama_service()))

    # 测试 2: llm_local 模块
    results.append(("llm_local 模块", test_llm_local_module()))

    # 测试 3: 代码补全生成
    results.append(("代码补全生成", test_generate_completion()))

    # 测试 4: API 端点（可选，需要服务运行）
    results.append(("API 端点", test_autocomplete_api()))

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)

    if all_passed:
        print("\n艹，所有测试都通过了！服务正常！")
        return 0
    else:
        print("\n艹，有测试失败了，检查上面的错误信息！")
        return 1


if __name__ == "__main__":
    sys.exit(main())
