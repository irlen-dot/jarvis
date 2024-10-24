import os
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description='Display current working directory information')
    
    parser.add_argument('-a', '--all', action='store_true',
                       help='Show both current working directory and script location')
    parser.add_argument('--writecode', type=str, metavar='STRING',
                       help='Accept a string argument after --writecode, which has to explain what exactly do you want the LLM to write')
    
    args = parser.parse_args()
    
    if args.all:
        print(f"Current working directory: {os.getcwd()}")
        print(f"Script location: {os.path.dirname(os.path.abspath(__file__))}")
    
    if args.writecode:
        print(f"Received string argument: {args.writecode}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())