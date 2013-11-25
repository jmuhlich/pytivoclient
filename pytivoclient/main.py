import sys
from cliff.app import App
from cliff.commandmanager import CommandManager


class ClientApp(App):

    def __init__(self):
        super(ClientApp, self).__init__(
            description='pytivoclient app',
            version='0.1',
            command_manager=CommandManager('pytivoclient.app'),
            )
        #self.parser.add_argument(
        #    '-s', '--server',
        #    action='store',
        #    help='TiVO server IP.',
        #    )
        #self.parser.add_argument(
        #    '-m', '--mak',
        #    action='store',
        #    help='Media Access Key.',
        #    )


def main(argv=sys.argv[1:]):
    app = ClientApp()
    return app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
