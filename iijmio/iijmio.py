# -*- coding:utf8 -*-
from errbot import BotPlugin, botcmd


class Iijmio(BotPlugin):
    """
    IIJmio monitor
    """

    def get_configuration_template(self):
        return {
            'username': "YOUR_IIJMIO_USERNAME",
            'password': "YOUR_IIJMIO_PASSWORD", }

    @botcmd(name='iijmio_current')
    def fetch_currently_usage(self, message, args):
        return "Example"
