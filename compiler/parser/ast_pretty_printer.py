import sys

def ast_pretty_print(filename):
    try:
        input_file = open(filename, 'r')
    except IOError:
        print("Unable to open file. Exiting...")
        sys.exit()

    ast = input_file.read()
    for line in ast.split('\n'):
        leading = len(line) - len(line.lstrip('|'))
        print('\033[' + str(90 + leading % 8)  + 'm'+ line + '\x1b[0m')


if __name__ == "__main__":
    ast_pretty_print(sys.argv[1])
