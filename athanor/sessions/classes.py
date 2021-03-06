from evennia.server.serversession import ServerSession
from evennia.utils import lazy_property
from athanor.sessions.managers import SessionManager


class Session(ServerSession):

    @lazy_property
    def ath(self):
        return SessionManager(self)

    def at_sync(self):
        super(Session, self).at_sync()
        self.ath.at_sync()

    def at_login(self, account):
        super(Session, self).at_login(account)
        self.ath.at_login(account)

    def at_disconnect(self, reason=None):
        super(Session, self).at_disconnect(reason)
        self.ath.at_disconnect(reason)

    def at_parse_command(self, command):
        pass
