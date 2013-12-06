import sys
from cliff.app import App
from cliff.commandmanager import CommandManager
from cliff.lister import Lister
import cliff.interactive
from usersettings import Settings
from pytivoclient.client import Client


class ClientApp(App):

    def __init__(self):
        super(ClientApp, self).__init__(
            description='pytivoclient app',
            version='0.1',
            command_manager=CommandManager('pytivoclient.app'),
            interactive_app_factory=InteractiveApp,
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

    def initialize_settings(self):
        self.settings = Settings('pytivoclient')
        self.settings.add_setting("hostname")
        self.settings.add_setting("media_access_key")
        self.settings.load_settings()
        for optname in ('hostname', 'media_access_key'):
            if not getattr(self.options, optname):
                optvalue = self.settings.get(optname)
                setattr(self.options, optname, optvalue)


class List(Lister):

    def take_action(self, parsed_args):
        return (('Title', 'Type'),
                ((i.title, i.content_type) for i in self.app.client.list())
                )


_commands_to_discard = ('cmdenvironment edit hi history l list pause r save '
                        'shell show ed li load py run set shortcuts EOF eof q '
                        'quit').split(' ')
_discard_set = set('do_' + n for n in _commands_to_discard)

class InteractiveApp(cliff.interactive.InteractiveApp):

    # This isn't enough to disable the commands, it just hides them
    # from the help listing!
    def get_names(self):
        names = cliff.interactive.InteractiveApp.get_names(self)
        names = [n for n in names if n not in _discard_set]
        return names


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
