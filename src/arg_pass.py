import argparse

class arg_pass:
    def __init__(self):
        # Create the argument parser
        custom_usage = "%(prog)s input output [-h] [-l] [-c] [-q QUALITY] [-e EFFORT]"
        self.parser = argparse.ArgumentParser(description="Convert a nef file to jxl format.", usage=custom_usage)
        self.parser.add_argument("input_file", metavar="input", type=str, help="Path to the input nef file.")
        self.parser.add_argument("output_file", metavar="output", type=str, help="Path to the output jxl file.")
        # Create a group where only ONE of these arguments can be selected
        group = self.parser.add_mutually_exclusive_group()
        group.add_argument("-l", "--lossless", dest="lossless", action="store_true", help="Use lossless compression for the output jxl file.")
        group.add_argument("-c", "--compression", dest="compression",action="store_true", help="Compress the image to save disk space with minimal visible quality loss.")
        group.add_argument("-q", "--quality", dest="quality", type=int, default=90, help="Set compression level from 1 (smallest file size) to 100 (highest quality), (default: 90).")
        
        self.parser.add_argument("-e", "--effort", dest="effort", type=int, default=4, help="Set CPU optimization effort from 1 (fastest conversion) to 9 (best compression, uses more CPU), (default: 4).")
        
        self.args = self.parser.parse_args()

