import sys

from get import main


def run(event, context):

    print(event)
    print(context)
    if main() == 0:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    run(event, context)
