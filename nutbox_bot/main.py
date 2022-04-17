import os
import sys
import argparse
import getpass
import json
from nutbox_bot import metadata


def main(argv):
    """Program entry point.

    :param argv: command-line arguments
    :type argv: :class:`list`
    """
    author_strings = []
    for name, email in zip(metadata.authors, metadata.emails):
        author_strings.append('Author: {0} <{1}>'.format(name, email))

    epilog = '''
{project} {version}

{authors}
URL: <{url}>
'''.format(project=metadata.project, version=metadata.version, authors='\n'.join(author_strings), url=metadata.url)

    arg_parser = argparse.ArgumentParser(prog=argv[0], formatter_class=argparse.RawDescriptionHelpFormatter, description=metadata.description, epilog=epilog)
    arg_parser.add_argument('--config', type=argparse.FileType('r'), help='config file for console')
    arg_parser.add_argument('command', choices=['create'], nargs='?', help='the command to run')
    arg_parser.add_argument('-V', '--version', action='version', version='{0} {1}'.format(metadata.project, metadata.version))

    args = arg_parser.parse_args(args=argv[1:])
    config_info = procConfig(args.config)
    if args.command == "create":
        print("Hello console!")
    else:
        print(epilog)
    return 0


def procConfig(cf):
    config_info = {}
    if not cf:
        cf = open("./config.json", "r")
    config_info = json.load(cf)
    return config_info


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    entry_point()