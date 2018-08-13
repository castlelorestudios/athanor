"""
Builds on the Core by adding some visibility rules and support for Dark/Hide, and pretty formatting.

"""

from evennia.utils import time_format


def idle_seconds(owner, viewer, *args, **kwargs):
    if not owner.prop.get('visible_to', viewer):
        return -1
    return owner.ath['core'].idle_time


def conn_seconds(owner, viewer, *args, **kwargs):
    if not owner.prop.get('visible_to', viewer):
        return -1
    return owner.ath['core'].connection_time


def hide_idle(owner, viewer, *args, **kwargs):
    idle = owner.prop.get('idle_seconds', viewer)
    if idle == -1:
        return '|XOff|n'
    return time_format(idle, style=1)


def conn_idle(owner, viewer, *args, **kwargs):
    conn = owner.prop.get('conn_seconds', viewer)
    if conn == -1:
        return '|XOff|n'
    return time_format(conn, style=1)


def last_idle(owner, viewer, *args, **kwargs):
    idle = owner.prop.get('idle_seconds', viewer)
    last = owner.base['core'].last_played
    if idle == -1:
        return viewer.ath['core'].display_time(date=last, format='%b %d')
    return time_format(idle, style=1)


def last_conn(owner, viewer, *args, **kwargs):
    conn = owner.prop.get('conn_seconds', viewer)
    last = owner.base['core'].last_played
    if conn == -1:
        return viewer.ath['core'].display_time(date=last, format='%b %d')
    return time_format(conn, style=1)