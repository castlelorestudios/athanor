"""
Contains the simplest implementation of a Manager for Characters.
"""

from athanor.base.managers import __BaseManager


class CharacterManager(__BaseManager):
    """
    Athanor basic Character Manager.

    Implements all of the Character hooks that Handlers need.
    """
    mode = 'character'

    def at_object_creation(self):
        for handler in self.ordered_handlers:
            handler.at_object_creation()

    def at_init(self):
        for handler in self.ordered_handlers:
            handler.at_init()

    def at_post_unpuppet(self, account, session, **kwargs):
        for handler in self.ordered_handlers:
            handler.at_post_unpuppet(account, session, **kwargs)

    def at_true_logout(self, account, session, **kwargs):
        for handler in self.ordered_handlers:
            handler.at_true_logout(account, session, **kwargs)

    def at_true_login(self, **kwargs):
        for handler in self.ordered_handlers:
            handler.at_true_login(**kwargs)

    def at_post_puppet(self, **kwargs):
        for handler in self.ordered_handlers:
            handler.at_post_puppet(**kwargs)