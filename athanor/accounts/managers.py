"""
Contains the simplest implementation of a Manager for Accounts.
"""

from athanor.base.managers import __BaseManager


class AccountManager(__BaseManager):
    """
    Athanor basic Account Manager.

    Implements all of the Account hooks that Handlers need.
    """
    mode = 'account'

    def at_account_creation(self):
        for handler in self.ordered_handlers:
            handler.at_account_creation()

    def at_post_login(self, session, **kwargs):
        for handler in self.ordered_handlers:
            handler.at_post_login(session, **kwargs)

    def at_true_login(self, session, **kwargs):
        for handler in self.ordered_handlers:
            handler.at_true_login(session, **kwargs)

    def at_failed_login(self, session, **kwargs):
        for handler in self.ordered_handlers:
            handler.at_failed_login(session, **kwargs)

    def at_init(self):
        for handler in self.ordered_handlers:
            handler.at_init()

    def at_disconnect(self, reason, **kwargs):
        for handler in self.ordered_handlers:
            handler.at_disconnect(reason, **kwargs)

    def at_true_logout(self, **kwargs):
        for handler in self.ordered_handlers:
            handler.at_true_logout(**kwargs)

    def render_login(self, session, viewer):
        message = []
        for handler in self.ordered_handlers:
            message.append(handler.render_login(session, viewer))
        return '\n'.join([str(line) for line in message if line])