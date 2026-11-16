import platform
import rawpy
import subprocess
import os
import shutil


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


def convert_nef_to_jxl(input_path, output_path, lossless, compression, quality, effort):

    cjxl_cmd = get_cxjl_path()
    if not cjxl_cmd:
        return

    with rawpy.imread(input_path) as raw:
        rgb = raw.postprocess(use_camera_wb=True, output_color=rawpy.ColorSpace.sRGB)

    height, width, _ = rgb.shape
    ppm_header = f"P6\n{width} {height}\n255\n".encode()

    cmd = [cjxl_cmd, "-", output_path]

    # Handle the mutually exclusive arguments
    if lossless:
        cmd.extend(["-d", "0"]) # Mathematically lossless
    elif compression:
        cmd.extend(["-q", "1"]) # Aggressive compression for lowest possible size
    elif quality is not None:
        cmd.extend(["-q", str(quality)]) # Custom quality specified by the user
    else:
        # Fallback default if the user runs the script without -l, -c, or -q
        cmd.extend(["-q", "90"]) 
    
    cmd.extend(["-e", str(effort)])

    process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    process.stdin.write(ppm_header)
    process.stdin.write(rgb.tobytes())
    process.stdin.close()
    process.wait()
    
    if process.returncode == 0:
        print(f"Successfully converted: {output_path}")
    else:
        print("Error occurred during cjxl compression.")
