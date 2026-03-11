import os

NEXT_EDIT_AUTOCOMPLETE_ENDPOINT = os.environ.get(
    "NEXT_EDIT_AUTOCOMPLETE_ENDPOINT", None
)

# 艹，ollama 配置，别tm乱改
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL_NAME = os.environ.get("OLLAMA_MODEL_NAME", "sweep-next-edit-1.5b:latest")

# 旧的配置保留，但已经不用了
MODEL_REPO = os.environ.get("MODEL_REPO", "sweepai/sweep-next-edit-0.5B")
MODEL_FILENAME = os.environ.get("MODEL_FILENAME", "sweep-next-edit-0.5b.q8_0.gguf")
