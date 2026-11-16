# nef to jxl

Install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

To upload converted JXL files to Discord for the first time, pass the webhook
URL with `-u`. This creates or updates `.env` automatically:

```powershell
python NefDrop.py "D:\Photos" -u "https://discord.com/api/webhooks/WEBHOOK_ID/WEBHOOK_TOKEN"
```

After that, use `-u` without a URL. To switch channels, pass the new webhook
URL and `.env` will be updated:

```powershell
python NefDrop.py "D:\Photos" -u
python NefDrop.py "D:\Photos" -u "https://discord.com/api/webhooks/NEW_ID/NEW_TOKEN"
```

JXL is the default output. Add `-j` to also create a compatible JPEG file;
uploads with `-u` include any generated JPEG files and are sent in batches of
10 files:

```powershell
python NefDrop.py "D:\Photos" -j -u
```

Convert one NEF file. The result is saved to a `jxl` folder beside the input:

```powershell
python NefDrop.py "D:\Photos\image.NEF"
```

Convert every NEF file in a folder, including subfolders. The results are saved
to `<input-folder>\jxl`:

```powershell
python NefDrop.py "D:\Photos"
```

Set a custom output folder:

```powershell
python NefDrop.py "D:\Photos" "D:\Converted-JXL"
```

Target approximately 10 MB per output image:

```powershell
python NefDrop.py "D:\Photos" -s 10
```

The target size is approximate. Lossless mode cannot guarantee a requested file
size, so `-s` should be used instead of `-l`.

