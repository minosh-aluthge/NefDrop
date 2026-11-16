import argparse

class arg_pass:
    def __init__(self):
        # Create the argument parser
        custom_usage = "%(prog)s input [output] [-h] [-l] [-c] [-q QUALITY] [-s SIZE_MB] [-e EFFORT] [-j] [-u [WEBHOOK_URL]]"
        self.parser = argparse.ArgumentParser(description="Convert a nef file to jxl format.", usage=custom_usage)
        self.parser.add_argument("input_file", metavar="input", type=str, help="Path to the input nef file.")
        self.parser.add_argument("output_file", metavar="output", type=str, nargs="?", help="Output .jxl file or batch output folder. Defaults to an jxl folder beside the input.")
        # Lossless and aggressive compression are mutually exclusive.
        group = self.parser.add_mutually_exclusive_group()
        group.add_argument("-l", "--lossless", dest="lossless", action="store_true", help="Use lossless compression for the output jxl file.")
        group.add_argument("-c", "--compression", dest="compression",action="store_true", help="Compress the image to save disk space with minimal visible quality loss.")
        self.parser.add_argument("-q", "--quality", dest="quality", type=int, default=95, help="Set compression level from 1 (smallest file size) to 100 (highest quality), (default: 95).")
        self.parser.add_argument("-s", "--size-mb", dest="size_mb", type=float, help="Target an output size in megabytes, for example 10 for about 10 MB per image.")
        
        self.parser.add_argument("-e", "--effort", dest="effort", type=int, default=4, help="Set CPU optimization effort from 1 (fastest conversion) to 9 (best compression, uses more CPU), (default: 4).")
        self.parser.add_argument("-j", "--jpg", action="store_true", help="Also create a JPEG copy for compatibility.")
        self.parser.add_argument(
            "-u",
            "--upload",
            nargs="?",
            const=True,
            default=False,
            metavar="WEBHOOK_URL",
            help="Upload JXL files; optionally save this webhook URL to .env.",
        )
        
        self.args = self.parser.parse_args()
        if not 1 <= self.args.quality <= 100:
            self.parser.error("--quality must be between 1 and 100")
        if not 1 <= self.args.effort <= 10:
            self.parser.error("--effort must be between 1 and 10")
        if self.args.size_mb is not None and self.args.size_mb <= 0:
            self.parser.error("--size-mb must be greater than 0")
        if self.args.size_mb is not None and (self.args.lossless or self.args.compression):
            self.parser.error("--size-mb can be combined with --quality, but not --lossless or --compression")

