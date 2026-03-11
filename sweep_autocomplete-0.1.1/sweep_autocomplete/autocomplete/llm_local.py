import os
import threading
import time
from typing import Any

import requests
from loguru import logger

# 艹，ollama配置，别tm乱改
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL_NAME = os.environ.get("OLLAMA_MODEL_NAME", "sweep-next-edit-1.5b")

_model_verified: bool = False
_model_lock = threading.Lock()
_request_lock = threading.Lock()
_latest_request_id = 0


class RequestCancelled(Exception):
    """Raised when a queued request is superseded by a newer one."""
    pass


def get_model() -> str:
    """验证ollama服务是否可用，返回模型名

    艹，这个函数现在只是检查服务，不下载模型了！
    """
    global _model_verified
    if not _model_verified:
        logger.info(f"检查 ollama 服务: {OLLAMA_BASE_URL}")
        try:
            # 检查ollama服务是否运行
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            response.raise_for_status()

            # 检查模型是否存在
            models = response.json().get("models", [])
            model_names = [m.get("name", "").split(":")[0] for m in models]

            if OLLAMA_MODEL_NAME not in model_names:
                logger.warning(f"艹！模型 {OLLAMA_MODEL_NAME} 不在 ollama 中，可用模型: {model_names}")
                logger.warning(f"继续尝试使用 {OLLAMA_MODEL_NAME}，可能会报错")
            else:
                logger.info(f"找到模型 {OLLAMA_MODEL_NAME}，服务正常")

            _model_verified = True
        except requests.exceptions.RequestException as e:
            logger.error(f"艹！连接 ollama 服务失败: {e}")
            logger.error(f"确保 ollama 服务运行在 {OLLAMA_BASE_URL}")
            raise RuntimeError(f"无法连接到 ollama 服务: {e}")

    return OLLAMA_MODEL_NAME


def generate_completion(
    prompt: str,
    stop: list[str],
    max_tokens: int,
    temperature: float,
    prefix: str = "",
) -> tuple[str, int, list[Any], str | None]:
    """使用 ollama API 生成代码补全

    艹，这个函数改成调用 ollama 的 /api/generate 接口了！

    Only the latest request will actually run inference. If a newer request
    arrives while this one is waiting for the model lock, this request is
    cancelled (raises RequestCancelled).

    Returns (completion_text, elapsed_ms, logprobs, finish_reason)
    matching the signature of fetch_next_edits_http.
    """
    global _latest_request_id

    model_name = get_model()
    full_prompt = prompt + prefix if prefix else prompt

    # Claim a request ID — always monotonically increasing
    with _request_lock:
        _latest_request_id += 1
        my_id = _latest_request_id

    # Wait for the model. When we get the lock, check if we're still latest.
    with _model_lock:
        if my_id != _latest_request_id:
            logger.info(f"Request {my_id} cancelled (latest is {_latest_request_id})")
            raise RequestCancelled()

        # 估算token数量（简单按字符数/3.5估算）
        estimated_tokens = int(len(full_prompt) / 3.5)
        logger.info(f"Prompt length: {len(full_prompt)} chars, ~{estimated_tokens} tokens (estimated)")

        start = time.time()

        # 调用 ollama API
        try:
            payload = {
                "model": model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "stop": stop,
                }
            }

            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            elapsed_ms = int((time.time() - start) * 1000)

            # 解析响应
            text = result.get("response", "")
            if prefix:
                text = prefix + text

            # ollama 的 done_reason 对应 finish_reason
            finish_reason = result.get("done_reason", "stop")

            logger.info(f"生成完成，耗时 {elapsed_ms}ms，生成 {len(text)} 字符")

            return text, elapsed_ms, [], finish_reason

        except requests.exceptions.RequestException as e:
            logger.error(f"艹！调用 ollama API 失败: {e}")
            raise RuntimeError(f"ollama API 调用失败: {e}")
