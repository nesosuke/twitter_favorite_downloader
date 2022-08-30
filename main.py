import sys

from get import main


def run(event, context):
    if main() is None:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    event=None
    context=None
    run(event, context)
