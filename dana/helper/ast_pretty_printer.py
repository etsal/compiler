import sys

colored_list = ['\033[0m', '\033[91m', '\033[92m', '\033[93m', '\033[94m','\033[95m',]

try:
    input_file = open(sys.argv[1], 'r')
except IOError:
    print("Unable to open file. Exiting...")
    sys.exit()

ast = input_file.read()
for line in ast.split('\n'):
    leading = len(line) - len(line.lstrip('|'))
    print('\033[' + str(90 + leading % 8)  + 'm'+ line + '\x1b[0m')
