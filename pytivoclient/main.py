import sys
from cliff.app import App
from cliff.commandmanager import CommandManager
from cliff.command import Command
from cliff.show import ShowOne
from cliff.lister import Lister
import cliff.interactive
from usersettings import Settings
from pytivoclient.client import Client, Folder


class ClientApp(App):

    def __init__(self):
        super(ClientApp, self).__init__(
            description='pytivoclient app',
            version='0.1',
            command_manager=CommandManager('pytivoclient.app'),
            )

    def build_option_parser(self, description, version, argparse_kwargs=None):
        parser = (super(ClientApp, self).
                  build_option_parser(description, version, argparse_kwargs))
        _remove_parser_argument(parser, '-q')
        _find_parser_argument(parser, '-v').default = 0
        parser.add_argument(
            '-n', '--hostname',
            action='store',
            help='TiVo hostname or IP address.',
            )
        parser.add_argument(
            '-m', '--media_access_key',
            action='store',
            help='Media Access Key.',
            metavar='KEY',
            )
        return parser

    def initialize_app(self, argv):
        self.initialize_settings()
        self.client = Client(self.options.hostname,
                             self.options.media_access_key)
        self.folder = None
        self.update_listing()

    def initialize_settings(self):
        self.settings = Settings('pytivoclient')
        self.settings.add_setting("hostname")
        self.settings.add_setting("media_access_key")
        self.settings.load_settings()
        for optname in ('hostname', 'media_access_key'):
            if not getattr(self.options, optname):
                optvalue = self.settings.get(optname)
                setattr(self.options, optname, optvalue)

    def update_listing(self):
        self.listing = self.client.list(self.folder)


class List(Lister):

    def take_action(self, args):
        data = self.app.listing
        return (
            ('Title', 'Type'),
            ((i.display_title, i.type) for i in data)
            )


class Chdir(Command):

    def get_parser(self, prog_name):
        parser = super(Chdir, self).get_parser(prog_name)
        parser.add_argument('folder')
        return parser

    def take_action(self, args):
        matches = [i for i in self.app.listing if i.title == args.folder]
        if args.folder == '/':
            folder = None
        elif len(matches) == 0:
            raise RuntimeError("no such folder")
        elif len(matches) > 1:
            raise RuntimeError("multiple matching folders")
        elif not isinstance(matches[0], Folder):
            raise RuntimeError("not a folder")
        else:
            folder = matches[0]
        self.app.folder = folder
        self.app.update_listing()


def _find_parser_argument(parser, option):
    gen = (a for a in parser._actions if option in a.option_strings)
    return next(gen, None)

def _remove_parser_argument(parser, option):
    action = _find_parser_argument(parser, option)
    for opt in action.option_strings:
        parser._option_string_actions.pop(opt, None)
    action.container._remove_action(action)


def main(argv=sys.argv[1:]):
    app = ClientApp()
    return app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
