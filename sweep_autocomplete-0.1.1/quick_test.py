#!/usr/bin/env python3
"""
艹，快速测试 ollama 集成
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("快速测试 ollama 集成")
print("=" * 60)

# 测试 1: 导入模块
print("\n[1/3] 导入模块...")
try:
    from sweep_autocomplete.autocomplete.llm_local import get_model, generate_completion
    print("✓ 模块导入成功")
except Exception as e:
    print(f"✗ 模块导入失败: {e}")
    sys.exit(1)

# 测试 2: 验证模型
print("\n[2/3] 验证 ollama 服务和模型...")
try:
    model_name = get_model()
    print(f"✓ 模型验证成功: {model_name}")
except Exception as e:
    print(f"✗ 模型验证失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试 3: 生成补全
print("\n[3/3] 测试代码补全生成...")
try:
    test_prompt = 'def hello():\n    print("'

    print(f"测试 prompt: {repr(test_prompt)}")
    print("生成中...")

    text, elapsed_ms, logprobs, finish_reason = generate_completion(
        prompt=test_prompt,
        stop=['"', "\n\n"],
        max_tokens=30,
        temperature=0.2,
        prefix=""
    )

    print(f"\n✓ 生成成功!")
    print(f"  耗时: {elapsed_ms}ms")
    print(f"  完成原因: {finish_reason}")
    print(f"  生成内容: {repr(text)}")
    print(f"  完整代码: {repr(test_prompt + text)}")

except Exception as e:
    print(f"✗ 生成失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("艹，测试全部通过！ollama 集成正常工作！")
print("=" * 60)
