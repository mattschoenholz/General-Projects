from pathlib import Path
from fastmcp import FastMCP

VAULT = Path("/home/matt/intel_vault").resolve()

mcp = FastMCP(name="bearclaw")


@mcp.tool()
def vault_read(path: str) -> str:
    """Read a file from intel_vault. Path is relative to vault root, e.g. '06_Ideas/ideas-inbox.md'."""
    target = (VAULT / path).resolve()
    if not str(target).startswith(str(VAULT) + "/") and str(target) != str(VAULT):
        raise ValueError("Path escapes vault root")
    if not target.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return target.read_text()


@mcp.tool()
def vault_list(folder: str = "") -> list[str]:
    """List markdown files in a vault folder. Empty string = vault root."""
    base = (VAULT / folder).resolve()
    if not str(base).startswith(str(VAULT) + "/") and str(base) != str(VAULT):
        raise ValueError("Path escapes vault root")
    if not base.exists():
        raise FileNotFoundError(f"Folder not found: {folder}")
    return sorted(str(p.relative_to(VAULT)) for p in base.rglob("*.md"))


@mcp.tool()
def vault_search(query: str, folder: str = "") -> list[dict]:
    """Grep-style search across vault markdown. Returns up to 50 matches."""
    import re
    base = (VAULT / folder).resolve()
    if not str(base).startswith(str(VAULT) + "/") and str(base) != str(VAULT):
        raise ValueError("Path escapes vault root")
    pattern = re.compile(query, re.IGNORECASE)
    results = []
    for f in sorted(base.rglob("*.md")):
        for i, line in enumerate(f.read_text(errors="replace").splitlines(), 1):
            if pattern.search(line):
                results.append({
                    "file": str(f.relative_to(VAULT)),
                    "line": i,
                    "text": line.strip()[:200],
                })
                if len(results) >= 50:
                    return results
    return results


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8765)
