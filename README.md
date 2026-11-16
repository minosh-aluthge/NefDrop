# nef to jxl

Install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

Convert one NEF file. The result is saved to a `jxl` folder beside the input:

```powershell
python main.py "D:\Photos\image.NEF"
```

Convert every NEF file in a folder, including subfolders. The results are saved
to `<input-folder>\jxl`:

```powershell
python main.py "D:\Photos"
```

Set a custom output folder:

```powershell
python main.py "D:\Photos" "D:\Converted-JXL"
```

Target approximately 10 MB per output image:

```powershell
python main.py "D:\Photos" -s 10
```

The target size is approximate. Lossless mode cannot guarantee a requested file
size, so `-s` should be used instead of `-l`.

