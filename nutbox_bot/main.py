import os
import signal
import sys
import argparse
import json
from nutbox_bot import metadata
from nutbox_bot.server import BotServer


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
    arg_parser.add_argument('command', choices=['bot'], nargs='?', help='the command to run')
    arg_parser.add_argument('-V', '--version', action='version', version='{0} {1}'.format(metadata.project, metadata.version))
    arg_parser.add_argument('-D', '--debug', action='store_true', help='debug mode')

    args = arg_parser.parse_args(args=argv[1:])
    config_info = procConfig(args.config)
    if args.command == "bot":
        server = BotServer(config_info, debug=args.debug)

        def handler(__signalnum: int, __frame) -> None:
            server.stop()

        signal.signal(signal.SIGINT, handler)
        server.start()
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