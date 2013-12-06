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



# Here we jump through some hoops to disable most of the build-in cmd and cmd2
# command handlers. They are really overkill for this little app. There is no
# mechanism to disable an existing command, but a Cmd subclass with the
# following two features appears to do the trick:
# 1. Override Cmd.get_names to filter out the unwanted do_* method names. This
#    hides the commands from help output and tab completion lists.
# 2. Assign an empty property() to the actual do_* attributes of the class. An
#    empty property() raises an AttributeError on access, which mimics a
#    nonexistent method so that the commands can't actually be called. (Cmd is
#    not a new-style class so __getattribute__ is not an option.) Is there any
#    other way for a subclass to hide its ancestors methods from them?

# List of commands to disable.
_commands_to_discard = ('cmdenvironment edit hi history l list pause r save '
                        'shell show ed li load py run set shortcuts q quit'
                        ).split(' ')
# Prefix with 'do_' and store as a set for efficient membership testing.
_discard_methods = set('do_' + n for n in _commands_to_discard)

class InteractiveApp(cliff.interactive.InteractiveApp):
    # Feature #1 described above.
    def get_names(self):
        names = cliff.interactive.InteractiveApp.get_names(self)
        names = [n for n in names if n not in _discard_methods]
        return names

# Feature #2. This is done outside the class definition so that we can just
# iterate over the set of method names we already have, and use setattr. Could
# probably achieve this with a metaclass but this is simple and clear.
for name in _discard_methods:
    setattr(InteractiveApp, name, property())



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
