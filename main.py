from src.arg_pass import arg_pass
from src.converter import convert_nef_to_jxl
def main():
    # Create an instance of the arg_pass class to parse command-line arguments
    args = arg_pass().args

    # Call the convert function with the parsed arguments
    convert_nef_to_jxl(args.input_file, args.output_file, args.lossless, args.compression, args.quality, args.effort)

if __name__ == "__main__":
    main()
    