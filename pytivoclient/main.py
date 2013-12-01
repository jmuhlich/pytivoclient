import sys
from cliff.app import App
from cliff.commandmanager import CommandManager
from cliff.lister import Lister
from usersettings import Settings
from pytivoclient.client import Client


class ClientApp(App):

    def __init__(self):
        super(ClientApp, self).__init__(
            description='pytivoclient app',
            version='0.1',
            command_manager=CommandManager('pytivoclient.app'),
            )
        self.parser.add_argument(
            '-n', '--hostname',
            action='store',
            help='TiVo hostname or IP address.',
            )
        self.parser.add_argument(
            '-m', '--media_access_key',
            action='store',
            help='Media Access Key.',
            metavar='KEY',
            )

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


def main(argv=sys.argv[1:]):
    app = ClientApp()
    return app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
