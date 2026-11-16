import platform
import rawpy
import subprocess
import os
import shutil
import tempfile
from pathlib import Path

from PIL import Image, ImageOps


def get_cxjl_path():
    # Check if cjxl is installed globally in the system PATH
    system_path = shutil.which("cjxl")
    if system_path:
        return system_path
    
    # Determine the architecture of the system ('x86_64', 'arm64', etc.)
    arch = platform.machine().lower()

    # Map architecture names to the expected format for cjxl binaries
    if arch in ['x86_64', 'amd64']:
        arch = 'x64'
    elif arch in ['arm64', 'aarch64']:
        arch = 'arm64'
    elif arch in ['x86', 'i386', 'i686']:
        arch = 'x86'

    folder_name = arch+"-"+ platform.system().lower()

    if os.path.exists(folder_name +"-static"):
        folder = folder_name +"-static"
    else:
        folder = folder_name
    

    if platform.system().lower() == 'windows':
        local_windows_path = os.path.join(folder, "bin", "cjxl.exe")
        if os.path.exists(local_windows_path):
            return local_windows_path


    return None


def _encode_file(cjxl_cmd, input_path, output_path, effort, quality_args, color_space=None):
    cmd = [cjxl_cmd, str(input_path), str(output_path)]
    if color_space:
        cmd.extend(["-x", f"color_space={color_space}"])
    if input_path.suffix.lower() in {".jpg", ".jpeg"} and "-d" not in quality_args:
        cmd.append("--lossless_jpeg=0")
    cmd.extend(quality_args)
    cmd.extend(["-e", str(effort)])

    result = subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        details = result.stderr.strip()
        raise RuntimeError(f"cjxl failed: {details or 'unknown encoder error'}")
    return result.returncode


def _encode_to_target_size(cjxl_cmd, input_path, output_path, effort, size_mb, max_quality, color_space=None):
    target_bytes = round(size_mb * 1024 * 1024)
    best_size_difference = None

    with tempfile.TemporaryDirectory(dir=output_path.parent) as temp_dir:
        temporary_output = os.path.join(temp_dir, "candidate.jxl")
        best_output = os.path.join(temp_dir, "best.jxl")
        low_quality = 1
        high_quality = max(1, min(100, max_quality))

        while low_quality <= high_quality:
            quality = (low_quality + high_quality) // 2
            returncode = _encode_file(
                cjxl_cmd,
                input_path,
                temporary_output,
                effort,
                ["-q", str(quality)],
                color_space,
            )
            if returncode != 0:
                raise RuntimeError(f"cjxl failed while targeting {size_mb:g} MB")

            output_size = os.path.getsize(temporary_output)
            size_difference = abs(output_size - target_bytes)
            if best_size_difference is None or size_difference < best_size_difference:
                shutil.copyfile(temporary_output, best_output)
                best_size_difference = size_difference

            if output_size <= target_bytes:
                low_quality = quality + 1
            else:
                high_quality = quality - 1

        shutil.copyfile(best_output, output_path)


def convert_nef_to_jxl(input_path, output_path, lossless, compression, quality, effort, size_mb=None, create_jpg=False):

    cjxl_cmd = get_cxjl_path()
    if not cjxl_cmd:
        raise FileNotFoundError("cjxl executable was not found in PATH or the bundled binary folder")

    input_path = Path(input_path)
    output_path = Path(output_path)
    jpg_output_path = output_path.with_suffix(".jpg")

    with tempfile.TemporaryDirectory(dir=output_path.parent) as temp_dir:
        source_color_space = None
        with rawpy.imread(str(input_path)) as raw:
            thumbnail = raw.extract_thumb()
            if thumbnail.format == rawpy.ThumbFormat.JPEG:
                camera_jpeg_path = Path(temp_dir) / "camera.jpg"
                camera_jpeg_path.write_bytes(thumbnail.data)
                if create_jpg:
                    shutil.copyfile(camera_jpeg_path, jpg_output_path)

                with Image.open(camera_jpeg_path) as camera_image:
                    normalized_image = ImageOps.exif_transpose(camera_image)
                    source_path = Path(temp_dir) / "source.jpg"
                    normalized_image.save(source_path, format="JPEG", quality=100, subsampling=0)
            else:
                rgb = raw.postprocess(
                    use_camera_wb=True,
                    output_color=rawpy.ColorSpace.sRGB,
                    output_bps=16,
                )
                source_color_space = "sRGB"
                source_path = Path(temp_dir) / "source.ppm"
                height, width, _ = rgb.shape
                with source_path.open("wb") as source_file:
                    source_file.write(f"P6\n{width} {height}\n65535\n".encode())
                    source_file.write(rgb.astype(">u2", copy=False).tobytes())

                if create_jpg:
                    Image.fromarray((rgb >> 8).astype("uint8"), "RGB").save(
                        jpg_output_path,
                        format="JPEG",
                        quality=quality or 95,
                        optimize=True,
                    )

        if lossless:
            quality_args = ["-d", "0"]
        elif compression:
            quality_args = ["-q", "1"]
        elif size_mb is not None:
            _encode_to_target_size(cjxl_cmd, source_path, output_path, effort, size_mb, quality, source_color_space)
            print(f"Successfully converted: {output_path}")
            return
        elif quality is not None:
            quality_args = ["-q", str(quality)]
        else:
            quality_args = ["-q", "90"]

        returncode = _encode_file(cjxl_cmd, source_path, output_path, effort, quality_args, source_color_space)
    
    if returncode == 0:
        print(f"Successfully converted: {output_path}")
    else:
        raise RuntimeError(f"cjxl failed while converting {input_path}")
