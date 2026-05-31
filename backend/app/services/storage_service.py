from __future__ import annotations

import asyncio
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from PIL import Image


class StorageService:
    def __init__(self, upload_dir: str) -> None:
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, file: UploadFile, *, prefix: str) -> tuple[str, str]:
        suffix = Path(file.filename or "").suffix or ".bin"
        stored_name = f"{prefix}-{uuid4().hex}{suffix}"
        stored_path = self.upload_dir / stored_name
        content = await file.read()
        await asyncio.to_thread(stored_path.write_bytes, content)
        return f"/uploads/{stored_name}", stored_name

    async def save_avatar(self, file: UploadFile) -> tuple[str, str]:
        suffix = ".png"
        stored_name = f"avatar-{uuid4().hex}{suffix}"
        stored_path = self.upload_dir / stored_name
        content = await file.read()

        def resize_avatar() -> None:
            image = Image.open(BytesIO(content))
            image = image.convert("RGB")
            image.thumbnail((512, 512))
            image.save(stored_path, format="PNG")

        await asyncio.to_thread(resize_avatar)
        return str(stored_path), stored_name
