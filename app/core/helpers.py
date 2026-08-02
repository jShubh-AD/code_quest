from pathlib import Path


def delete_local_file(url: str | None):
    if not url:
        return

    # /static/... maps to /app/data/...
    relative_path = url.removeprefix("/static/")
    file_path = Path("/app/data") / relative_path

    if file_path.exists() and file_path.is_file():
        file_path.unlink()