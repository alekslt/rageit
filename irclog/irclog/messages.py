""":mod:`irclog.messages` --- Various message types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Hierarchy
---------

It provides a hierarchy of IRC log message types.

- :class:`BaseMessage`

 - :class:`Message`

  - :class:`PublicMessage`
  - :class:`ActionMessage`
  - :class:`NoticeMessage`

 - :class:`BaseNickMessage`

  - :class:`NickMessage`
  - :class:`SelfNickMessage`

 - :class:`JoinMessage`
 - :class:`ModeMessage`
 - :class:`PartMessage`
 - :class:`QuitMessage`
 - :class:`KickMessage`
 - :class:`BaseTopicMessage`

  - :class:`TopicMessage`
  - :class:`NoTopicMessage`


Objects
-------

"""
import datetime


class BaseMessage(object):
    """Abstract base type for all IRC log messages.

    :param messaged_at: a :class:`datetime.datetime` logged
    :type messaged_at: :class:`datetime.datetime`


    .. attribute:: messaged_at

       The naive :class:`datetime.datetime` logged.

    """

    __slots__ = "messaged_at",

    def __init__(self, messaged_at):
        if not isinstance(messaged_at, datetime.datetime):
            raise TypeError("messaged_at must be a datetime.datetime, not " +
                            repr(messaged_at))
        self.messaged_at = messaged_at


class Message(BaseMessage):
    """Abstract base type for :class:`PublicMessage`, :class:`ActionMessage`
    and :class:`NoticeMessage`.

    :param messaged_at: a :class:`datetime.datetime` logged
    :type messaged_at: :class:`datetime.datetime`
    :param nick: a nickname
    :type nick: :class:`basestring`
    :param line: a message body
    :type line: :class:`basestring`


    .. attribute:: nick

       The nickname.

    .. attribute:: line

       The message body.

    """

    __slots__ = "nick", "line"

    def __init__(self, messaged_at, nick, line):
        BaseMessage.__init__(self, messaged_at)
        self.nick = unicode(nick)
        self.line = unicode(line)


class PublicMessage(Message):
    """Most commonly used message type.

    :param messaged_at: a :class:`datetime.datetime` logged
    :type messaged_at: :class:`datetime.datetime`
    :param nick: a nickname
    :type nick: :class:`basestring`
    :param line: a message body
    :type line: :class:`basestring`

    """


class ActionMessage(Message):
    """``ACTION`` message type.

    :param messaged_at: a :class:`datetime.datetime` logged
    :type messaged_at: :class:`datetime.datetime`
    :param nick: a nickname
    :type nick: :class:`basestring`
    :param line: a message body
    :type line: :class:`basestring`

    """

class NoticeMessage(Message):
    """Notice message type.

    :param messaged_at: a :class:`datetime.datetime` logged
    :type messaged_at: :class:`datetime.datetime`
    :param nick: a nickname
    :type nick: :class:`basestring`
    :param line: a message body
    :type line: :class:`basestring`
    :param channel: a channel name
    :type channel: :class:`basestring`


    .. attribute:: channel

       The channel name.

    """

    __slots__ = "channel",

    def __init__(self, messaged_at, nick, line, channel):
        Message.__init__(self, messaged_at, nick, line)
        self.channel = unicode(channel)


class BaseNickMessage(BaseMessage):
    """Abstract base type for nickname changing message types.

    :param messaged_at: a :class:`datetime.datetime` logged
    :type messaged_at: :class:`datetime.datetime`
    :param to: a new nickname
    :type to: :class:`basestring`


    .. attribute:: to

       The new nickname.

    """

    __slots__ = "to",

    def __init__(self, messaged_at, to):
        BaseMessage.__init__(self, messaged_at)
        self.to = unicode(to)


class NickMessage(BaseNickMessage):
    """Nickname changing message type.

    :param messaged_at: a :class:`datetime.datetime` logged
    :type messaged_at: :class:`datetime.datetime`
    :param from_: a old nickname
    :type from_: :class:`basestring`
    :param to: a new nickname
    :type to: :class:`basestring`

    .. attribute:: from_

       The old nickname.

    """

    __slots__ = "from_",

    def __init__(self, messaged_at, from_, to):
        BaseNickMessage.__init__(self, messaged_at, to)
        self.from_ = unicode(from_)


class SelfNickMessage(BaseNickMessage):
    """My nickname chaning message type.

    :param messaged_at: a :class:`datetime.datetime` logged
    :type messaged_at: :class:`datetime.datetime`
    :param to: a new nickname
    :type to: :class:`basestring`

    """


class JoinMessage(BaseMessage):
    """Join message type.

    :param messaged_at: a :class:`datetime.datetime` logged
    :type messaged_at: :class:`datetime.datetime`
    :param nick: a nickname
    :type nick: :class:`basestring`
    :param ident: an ident
    :type ident: :class:`basestring`
    :param channel: a channel name
    :type channel: :class:`basestring`


    .. attribute:: nick

       The nickname.

    .. attribute:: ident

       The ident.

    .. attribute:: channel

       The channel name.

    """

    __slots__ = "nick", "ident", "channel"

    def __init__(self, messaged_at, nick, ident, channel):
        BaseMessage.__init__(self, messaged_at)
        self.nick = unicode(nick)
        self.ident = unicode(ident)
        self.channel = unicode(channel)


class ModeMessage(BaseMessage):
    """``MODE`` message type.

    :param messaged_at: a :class:`datetime.datetime` logged
    :type messaged_at: :class:`datetime.datetime`
    :param server: a server
    :type server: :class:`basestring`
    :param channel: a channel name
    :type channel: :class:`basestring`
    :param modelist: a mode list
    :param nick: a nickname
    :type nick: :class:`basestring`


    .. attribute:: server

       The server.

    .. attribute:: channel

       The channel name.

    .. attribute:: modelist

       The mode list.

    .. attribute:: nick

       The nickname.


    """

    __slots__ = "server", "channel", "modelist", "nick"

    def __init__(self, messaged_at, server, channel, modelist, nick):
        BaseMessage.__init__(self, messaged_at)
        self.server = unicode(server)
        self.channel = unicode(channel)
        self.modelist = unicode(modelist)
        self.channel = unicode(channel)
        self.nick = unicode(nick)


class PartMessage(BaseMessage):
    """``PART`` message type.

    :param nick: a nickname
    :type nick: :class:`basestring`
    :param ident: an ident
    :type ident: :class:`basestring`
    :param channel: a channel name
    :type channel: :class:`basestring`
    :param reason: a reason
    :type reason: :class:`basestring`


    .. attribute:: nick

       The nickname.

    .. attribute:: ident

       The ident.

    .. attribute:: channel

       The channel name.

    .. attribute:: reason

       The reason.

    """

    __slots__ = "nick", "ident", "channel", "reason"

    def __init__(self, messaged_at, nick, ident, channel, reason):
        BaseMessage.__init__(self, messaged_at)
        self.nick = unicode(nick)
        self.ident = unicode(ident)
        self.channel = unicode(channel)
        self.reason = unicode(reason)


class QuitMessage(BaseMessage):
    """Quiting message type.

    :param nick: a nickname
    :type nick: :class:`basestring`
    :param ident: an ident
    :type ident: :class:`basestring`
    :param reason: a reason
    :type reason: :class:`basestring`


    .. attribute:: nick

       The nickname.

    .. attribute:: ident

       The ident.

    .. attribute:: reason

       The reason.

    """

    __slots__ = "nick", "ident", "reason"

    def __init__(self, messaged_at, nick, ident, reason):
        BaseMessage.__init__(self, messaged_at)
        self.nick = unicode(nick)
        self.ident = unicode(ident)
        self.reason = unicode(reason)


class KickMessage(BaseMessage):
    """Kick message type.

    :param nick: a nickname that was kicked
    :type nick: :class:`basestring`
    :param channel: a channel name
    :type channel: :class:`basestring`
    :param by: a nickname that kicks
    :type by: :class:`basestring`
    :param reason: a reason
    :type reason: :class:`basestring`


    .. attribute:: nick

       The nickname that was kicked.

    .. attribute:: channel

       The channel name.

    .. attribute:: by

       The nickname that kicks.

    .. attribute:: reason

       The reason.

    """

    __slots__ = "nick", "channel", "by", "reason",

    def __init__(self, messaged_at, nick, channel, by, reason):
        BaseMessage.__init__(self, messaged_at)
        self.nick = unicode(nick)
        self.channel = unicode(channel)
        self.by = unicode(by)
        self.reason = unicode(reason)


class BaseTopicMessage(BaseMessage):
    """Abstract base class for topic changing message types.

    :param messaged_at: a :class:`datetime.datetime` logged
    :type messaged_at: :class:`datetime.datetime`
    :param nick: a nickname
    :type nick: :class:`basestring`
    :param channel: a channel name
    :type channel: :class:`basestring`


    .. attribute:: nick

       The nickname.

    .. attribute:: channel

       The channel name.

    """

    __slots__ = "nick", "channel"

    def __init__(self, messaged_at, nick, channel):
        BaseMessage.__init__(self, messaged_at)
        self.nick = unicode(nick)
        self.channel = unicode(channel)


class TopicMessage(BaseTopicMessage):
    """Topic changing message types.

    :param messaged_at: a :class:`datetime.datetime` logged
    :type messaged_at: :class:`datetime.datetime`
    :param nick: a nickname
    :type nick: :class:`basestring`
    :param channel: a channel name
    :type channel: :class:`basestring`
    :param topic: a new topic
    :type topic: :class:`basestring`


    .. attribute:: topic

       The new topic

    """

    __slots__ = "topic"

    def __init__(self, messaged_at, nick, channel, topic):
        BaseTopicMessage.__init__(self, messaged_at, nick, channel)
        self.topic = unicode(topic)


class NoTopicMessage(BaseTopicMessage):
    """Empty topic message types.

    :param messaged_at: a :class:`datetime.datetime` logged
    :type messaged_at: :class:`datetime.datetime`
    :param nick: a nickname
    :type nick: :class:`basestring`
    :param channel: a channel name
    :type channel: :class:`basestring`

    """

