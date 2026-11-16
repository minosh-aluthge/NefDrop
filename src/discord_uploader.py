import os
import time
from contextlib import ExitStack
from pathlib import Path

import requests
from dotenv import load_dotenv, set_key


def upload_jxl_files(directory, chunk_size=10, webhook_url=None):
    """Upload JXL and JPEG files from a directory to the configured webhook."""
    env_path = Path(".env")
    if webhook_url:
        set_key(str(env_path), "WEBHOOK_URL", webhook_url)
    load_dotenv(dotenv_path=env_path, override=True)
    webhook_url = webhook_url or os.getenv("WEBHOOK_URL")
    if not webhook_url:
        raise RuntimeError("WEBHOOK_URL is not set in the .env file")

    directory = Path(directory)
    media_files = sorted(
        path
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in {".jxl", ".jpg"}
    )

    for start in range(0, len(media_files), chunk_size):
        chunk = media_files[start:start + chunk_size]
        while True:
            with ExitStack() as stack:
                files = [
                    (
                        f"files[{index}]",
                        (
                            path.name,
                            stack.enter_context(path.open("rb")),
                            "image/jpeg" if path.suffix.lower() == ".jpg" else "image/jxl",
                        ),
                    )
                    for index, path in enumerate(chunk)
                ]
                response = requests.post(webhook_url, files=files, timeout=30)

            if response.status_code != 429:
                response.raise_for_status()
                break

            try:
                retry_after = response.json()["retry_after"]
            except (ValueError, KeyError, TypeError):
                retry_after = 1
            time.sleep(float(retry_after))

        print(f"Uploaded {len(chunk)} file(s) to Discord")