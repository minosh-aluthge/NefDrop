# NefDrop

Convert Nikon NEF photos to JPEG XL, optionally create a compatible JPEG copy,
and upload the results to a Discord channel.

NefDrop uses the camera's embedded full-resolution preview when it is available.
That keeps the colors, exposure, and portrait orientation close to the image you
see in the camera preview.

## Features

- Convert one NEF file or an entire folder tree.
- Produce compact `.jxl` files by default.
- Create a compatible `.jpg` copy with `-j`.
- Preserve camera preview colors and orientation.
- Upload JXL and JPG files to Discord in batches of 10.
- Retry Discord HTTP 429 rate limits automatically.
- Save or update the Discord webhook securely in `.env`.

## Install

Create or activate a Python virtual environment, then install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

The project also needs the `cjxl` executable. NefDrop checks the system PATH
first, then the bundled `x64-windows-static\bin\cjxl.exe` file.

## Quick Start

Convert one NEF file. The result is written to a `jxl` folder beside the input:

```powershell
python NefDrop.py "D:\Photos\image.NEF"
```

Convert every NEF file in a folder, including subfolders:

```powershell
python NefDrop.py "D:\Photos"
```

Create a JPEG copy as well as the JXL file:

```powershell
python NefDrop.py "D:\Photos" -j
```

## Discord Uploads

Create a webhook in the Discord text channel where the files should appear.
On the first upload, pass the webhook URL. NefDrop creates or updates `.env`
automatically:

```powershell
python NefDrop.py "D:\Photos" -j -u "https://discord.com/api/webhooks/WEBHOOK_ID/WEBHOOK_TOKEN"
```

After the URL is saved, reuse it without typing it again:

```powershell
python NefDrop.py "D:\Photos" -j -u
```

To switch to another Discord channel, pass that channel's new webhook URL:

```powershell
python NefDrop.py "D:\Photos" -j -u "https://discord.com/api/webhooks/NEW_ID/NEW_TOKEN"
```

Keep the webhook URL private. The `.env` file is ignored by Git.

## Options

| Option | Description |
| --- | --- |
| `-l`, `--lossless` | Create lossless JXL output. |
| `-c`, `--compression` | Use stronger compression with minimal visible quality loss. |
| `-q`, `--quality QUALITY` | Set quality from 1 to 100. Default: `95`. |
| `-s`, `--size-mb SIZE_MB` | Target an approximate output size in megabytes. |
| `-e`, `--effort EFFORT` | Set encoder effort from 1 to 10. Default: `4`. |
| `-j`, `--jpg` | Also create a compatible JPEG file. |
| `-u`, `--upload [WEBHOOK_URL]` | Upload files, optionally saving a webhook URL. |

Examples:

```powershell
# Custom output folder
python NefDrop.py "D:\Photos" "D:\Converted-JXL"

# Target approximately 10 MB per image
python NefDrop.py "D:\Photos" -s 10

# Lossless JXL output
python NefDrop.py "D:\Photos" -l
```

`-s` cannot be combined with `-l` or `-c`, and the target size is approximate.

