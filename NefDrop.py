import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        return iterable

from src.arg_pass import arg_pass
from src.converter import convert_nef_to_jxl


def find_nef_files(input_path, excluded_path=None):
    if input_path.is_file():
        return [input_path]

    excluded_path = excluded_path.resolve() if excluded_path else None
    return (
        path
        for path in input_path.rglob("*")
        if path.is_file()
        and path.suffix.lower() == ".nef"
        and (excluded_path is None or excluded_path not in path.resolve().parents)
    )


def convert_batch(nef_files, output_path, args):
    nef_files = list(nef_files)
    max_workers = min(os.cpu_count() or 1, 4)

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                convert_nef_to_jxl,
                nef_file,
                output_path / f"{nef_file.stem}.jxl",
                args.lossless,
                args.compression,
                args.quality,
                args.effort,
                args.size_mb,
                args.jpg,
            ): nef_file
            for nef_file in nef_files
        }

        for future in tqdm(as_completed(futures), total=len(futures), desc="Converting NEF files"):
            future.result()


def main():
    args = arg_pass().args
    input_path = Path(args.input_file)

    if not input_path.exists():
        raise FileNotFoundError(f"Input path does not exist: {input_path}")

    if input_path.is_dir():
        output_path = Path(args.output_file) if args.output_file else input_path / "jxl"
        output_path.mkdir(parents=True, exist_ok=True)
        convert_batch(find_nef_files(input_path, output_path), output_path, args)
        if args.upload:
            from src.discord_uploader import upload_jxl_files

            webhook_url = args.upload if isinstance(args.upload, str) else None
            upload_jxl_files(output_path, webhook_url=webhook_url)
        return

    output_path = Path(args.output_file) if args.output_file else input_path.parent / "jxl" / f"{input_path.stem}.jxl"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    convert_nef_to_jxl(
        input_path,
        output_path,
        args.lossless,
        args.compression,
        args.quality,
        args.effort,
        args.size_mb,
        args.jpg,
    )
    if args.upload:
        from src.discord_uploader import upload_jxl_files

        webhook_url = args.upload if isinstance(args.upload, str) else None
        upload_jxl_files(output_path.parent, webhook_url=webhook_url)

if __name__ == "__main__":
    main()
    