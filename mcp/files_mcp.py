import os
from typing import List, Optional

from mcp.server import MCPServer

mcp = MCPServer("files-mcp")

def _normalize_path(path: str) -> str:
    return os.path.abspath(os.path.expanduser(path))

def _safe_join(root: str, user_path: str) -> str:
    root_abs = _normalize_path(root)
    target = _normalize_path(os.path.join(root_abs, user_path))
    if os.path.commonpath([root_abs, target]) != root_abs:
        raise ValueError("Path escapes root directory")
    return target

@mcp.tool()
def read_file(path: str, root: Optional[str] = None) -> str:
    base = root or os.getcwd()
    abs_path = _safe_join(base, path) if root else _normalize_path(path)

    with open(abs_path, "r", encoding="utf-8") as f:
        return f"File contents of {abs_path}:\n{f.read()}"

@mcp.tool()
def list_files(path: str = ".", root: Optional[str] = None) -> str:
    base = root or os.getcwd()
    abs_path = _safe_join(base, path) if root else _normalize_path(path)

    if not os.path.exists(abs_path):
        return f"Path not found: {abs_path}"

    items: List[str] = []
    for item in sorted(os.listdir(abs_path)):
        item_path = os.path.join(abs_path, item)
        if os.path.isdir(item_path):
            items.append(f"[DIR]  {item}/")
        else:
            items.append(f"[FILE] {item}")

    if not items:
        return f"Empty directory: {abs_path}"

    return f"Contents of {abs_path}:\n" + "\n".join(items)

@mcp.tool()
def edit_file(path: str, old_text: str, new_text: str, root: Optional[str] = None) -> str:
    base = root or os.getcwd()
    abs_path = _safe_join(base, path) if root else _normalize_path(path)

    if os.path.exists(abs_path) and old_text:
        with open(abs_path, "r", encoding="utf-8") as f:
            content = f.read()

        if old_text not in content:
            return f"Text not found in file: {old_text}"

        content = content.replace(old_text, new_text)

        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"Successfully edited {abs_path}"

    dir_name = os.path.dirname(abs_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(new_text)

    return f"Successfully created {abs_path}"

if __name__ == "__main__":
    port = 8000
    url = f"http://localhost:{port}"
    print(f"[TEST] Starting files-mcp server on port {port}")
    print(f"[TEST] Server URL: {url}")
    print(f"[TEST] Logging initialized - server is running for testing")
    mcp.run(port=port)
