import sys
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_error(error, message):
    print("ComfortZone: %s%s:%s %s" % (bcolors.FAIL, error, bcolors.ENDC, message), file=sys.stderr)

def print_exception(exception):
    print(bcolors.FAIL, file=sys.stderr, end="")
    print(exception, file=sys.stderr, end="")
    print(bcolors.ENDC, file=sys.stderr)
