"""
Minimal example script to run the sweep-next-edit-1.5B model using GGUF format.

This script demonstrates how to use the Sweep Next Edit training format to construct
prompts for next-edit autocomplete predictions.

Install dependencies:
    pip install llama-cpp-python huggingface-hub

Usage:
    python run_model.py
"""
import time
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

# Download model from Hugging Face if not already cached
MODEL_REPO = "sweepai/sweep-next-edit-1.5B"
MODEL_FILENAME = "sweep-next-edit-1.5b.q8_0.v2.gguf"

print("Downloading model from Hugging Face (cached after first download)...")
MODEL_PATH = hf_hub_download(
    repo_id=MODEL_REPO,
    filename=MODEL_FILENAME,
    repo_type="model"
)
print(f"Model loaded from: {MODEL_PATH}")


def build_prompt(
    context_files: dict[str, str],
    recent_diffs: list[dict[str, str]],
    file_path: str,
    original_content: str,
    current_content: str,
) -> str:
    """
    Build a prompt following Sweep Next Edit's training format.

    Format:
        <|file_sep|>{file_path_1}
        {file_content_1}
        <|file_sep|>{file_path_2}
        {file_content_2}
        <|file_sep|>{changed_file_1}.diff
        original:
        {before_changes_of_diff}
        updated:
        {after_changes_of_diff}
        <|file_sep|>original/{file_path}
        {contents_prior_to_most_recent_change}
        <|file_sep|>current/{file_path}
        {current_state_of_contents}
        <|file_sep|>updated/{file_path}
        {updated_state_of_contents}

    Args:
        context_files: Dict mapping file paths to their contents (related files for context)
        recent_diffs: List of dicts with 'file_path', 'original', and 'updated' keys
        file_path: Path of the file being edited
        original_content: Contents prior to most recent change
        current_content: Current state of the file being edited

    Returns:
        Formatted prompt string
    """
    prompt_parts = []

    # Add context files
    for path, content in context_files.items():
        prompt_parts.append(f"<|file_sep|>{path}")
        prompt_parts.append(content)

    # Add recent diffs
    for diff in recent_diffs:
        prompt_parts.append(f"<|file_sep|>{diff['file_path']}.diff")
        prompt_parts.append("original:")
        prompt_parts.append(diff['original'])
        prompt_parts.append("updated:")
        prompt_parts.append(diff['updated'])

    # Add original and current states
    prompt_parts.append(f"<|file_sep|>original/{file_path}")
    prompt_parts.append(original_content)
    prompt_parts.append(f"<|file_sep|>current/{file_path}")
    prompt_parts.append(current_content)
    prompt_parts.append(f"<|file_sep|>updated/{file_path}")

    return "\n".join(prompt_parts)


def generate(prompt: str) -> str:
    """Generate completion using the Sweep Next Edit model."""
    llm = Llama(model_path=MODEL_PATH, n_ctx=8192)

    output = llm(
        prompt,
        max_tokens=512,
        temperature=0.0,  # Use greedy decoding for deterministic output
        stop=["<|file_sep|>", "</s>"],
    )

    return output["choices"][0]["text"]


if __name__ == "__main__":
    # Simple example: User is writing a greeting function
    # The model predicts what they'll write next based on the pattern
    
    file_path = "greet.py"

    # Context: Other files in the codebase
    context_files = {
        "utils.py": """def get_time_of_day():
    from datetime import datetime
    hour = datetime.now().hour
    if hour < 12:
        return "morning"
    elif hour < 18:
        return "afternoon"
    else:
        return "evening"
""",
    }

    # Recent changes: User just added a personalized greeting
    recent_diffs = [
        {
            "file_path": "greet.py",
            "original": """def greet():
    print("Hello!")""",
            "updated": """def greet(name):
    print(f"Hello, {name}!")""",
        }
    ]

    # Before the most recent change
    original_content = """def greet(name):
    print(f"Hello, {name}!")

greet("Alice")"""

    # Current state: User just imported get_time_of_day
    current_content = """from utils import get_time_of_day

def greet(name):
    print(f"Hello, {name}!")

greet("Alice")"""

    prompt = build_prompt(
        context_files=context_files,
        recent_diffs=recent_diffs,
        file_path=file_path,
        original_content=original_content,
        current_content=current_content,
    )
    
    start_time = time.time()
    predicted_edit = generate(prompt)
    end_time = time.time()
    
    print("\n" + "=" * 80)
    print("CURRENT CODE:")
    print("=" * 80)
    print(current_content)

    print("\n" + "=" * 80)
    print("PREDICTED NEXT EDIT:")
    print("=" * 80)
    print(predicted_edit)

    print("\n" + "=" * 80)
    print(f"TIME TAKEN: {end_time - start_time:.2f} seconds")
    print("=" * 80)

    print("\n" + "=" * 80)
    print("DIFF (what changed):")
    print("=" * 80)

    import difflib
    diff = difflib.unified_diff(
        current_content.splitlines(keepends=True),
        predicted_edit.splitlines(keepends=True),
        fromfile=f"current/{file_path}",
        tofile=f"updated/{file_path}",
        lineterm=""
    )
    print("".join(diff))
    