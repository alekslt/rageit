""":mod:`irclog.parser` --- IRC log parser
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides a function which takes lines of log then transforms it
to message objects in :mod:`irclog.messages` module.


.. data:: PATTERN

   The :mod:`re` pattern matches to a line of IRC log message.

   .. note::

      This regular expression is originally written by
      `Kang Seonghoon`_ aka *lifthrasiir*. This pattern is posted in
      `an article of LangDev <http://langdev.net/post/93>`_.

      .. _Kang Seonghoon: http://mearie.org/

"""
import re
import datetime
import chardet
import irclog.messages


PATTERN = re.compile(r"""
    ^ (?:
        (?P<ignorable>
            ---[ ]Day[ ]changed[ ].* |
            \d\d:\d\d(?::\d\d)?[ ] (?:
                -!-[ ]Irssi:[ ] |
                -!-[ ][<;]/Netsplit[ ]   # XXX
            ) .*
        ) |
        (?P<logopenmsg>
            ---[ ]Log[ ]opened[ ]...[ ](?:[\d ]\d...|...)[ ]\d\d[ ]
            (?P<logopenwhen>\d\d:\d\d:\d\d)[ ]\d\d\d\d
        ) |
        (?P<logclosemsg>
            ---[ ]Log[ ]closed[ ]...[ ](?:[\d ]\d...|...)[ ]\d\d[ ]
            (?P<logclosewhen>\d\d:\d\d:\d\d)[ ]\d\d\d\d
        ) |
        (?P<when>\d\d:\d\d(?::\d\d)?)[ ](?:
            -!- [ ](?:
                (?P<nickmsg>
                    (?P<nickfrom>.*?)[ ]is[ ]now[ ]known[ ]as[ ](?P<nickto>.*?)
                ) |
                (?P<selfnickmsg>
                    You're[ ]now[ ]known[ ]as[ ](?P<selfnickto>.*?)
                ) |
                (?P<joinmsg>
                    (?P<joinnick>.*?)[ ]\[(?P<joinident>.*?)\][ ]
                    has[ ]joined[ ](?P<joinchan>.*?)
                ) |
                (?P<modemsg>
                    (?:mode|(?P<modeserver></ServerMode))
                    (?P<modechan>.*?)[ ]\[(?P<modelist>.*?)\][ ]
                    by[ ](?P<modenick>.*?)
                ) |
                (?P<partmsg>
                    (?P<partnick>.*?)[ ]
                    \[(?P<partident>.*?)\][ ]
                    has[ ]left[ ](?P<partchan>.*?)[ ]
                    \[(?P<partreason>.*?)/\]
                ) |
                (?P<quitmsg>
                    (?P<quitnick>.*?)[ ] \[(?P<quitident>.*?)\][ ]
                    has[ ]quit[ ]\[(?P<quitreason>.*?)\]
                ) |
                (?P<kickmsg>
                    (?P<kicknick>.*?)[ ]
                    was[ ]kicked[ ]from[ ](?P<kickchan>.*?)[ ]
                    by[ ](?P<kickby>.*?)[ ] \[(?P<kickreason>.*?)\]
                ) |
                (?P<topicmsg>
                    (?P<topicnick>.*?)[ ]changed[ ]
                    the[ ]topic[ ]of[ ](?P<topicchan>.*?)
                    [ ]to:[ ](?P<topicline>.*?)
                ) |
                (?P<notopicmsg>
                    Topic[ ]unset[ ]by[ ](?P<notopicnick>.*?)
                    [ ]on[ ](?P<notopicchan>.*?)
                ) |
            ) |
            (?P<pubmsg>
                <[ +@~]?(?P<pubnick>.*?)>[ ](?P<publine>.*?)
            ) |
            (?P<actmsg>
                [ ]\*[ ](?P<actnick>.*?)[ ](?P<actline>.*?)
            ) |
            (?P<noticemsg>
                -(?P<noticenick>.*?):
                (?:[+@~ ])?(?P<noticechan>.*?)
                -[ ](?P<noticeline>.*?)
            )
        )
    ) $
""", re.VERBOSE | re.IGNORECASE)

RULES = {}


def parse(lines, date=None, encoding="utf-8"):
    """Transforms lines of log to message objects in :mod:`irclog.messages`
    module.

    :param lines: lines of code
    :type lines: iterable object, file object
    :param date: a date of the log. default is today
    :type date: :class:`datetime.date`
    :param encoding: a text encoding. default is ``"utf-8"``
    :returns: a list of :class:`irclog.messages.BaseMessage` instances

    .. note:: This is exactly a generator function.

    """
    date = date or datetime.date.today()
    for line in lines:
        try:
            line = line.decode(encoding)
        except UnicodeDecodeError:
            enc = chardet.detect(line).get("encoding") or "utf-8"
            line = line.decode(enc, "replace")
        match = PATTERN.match(line.strip())
        if not match:
            continue
        for group_name, function in RULES.iteritems():
            if match.group(group_name):
                groups = match.groupdict()
                time = datetime.time(*map(int, groups["when"].split(":")))
                groups["when"] = datetime.datetime.combine(date, time)
                yield function(**groups)
                break


def parser(function):
    """Registers a parser function.
    
    :param function: a function parses to register
    :type function: callable object
    :returns: passed ``function``

    """
    if not callable(function):
        raise TypeError("function must be callable")
    RULES[function.__name__] = function
    return function


@parser
def nickmsg(when, nickfrom, nickto, **_):
    """Parses :class:`irclog.messages.NickMessage`."""
    return irclog.messages.NickMessage(when, nickfrom, nickto)


@parser
def selfnickmsg(when, selfnickto, **_):
    """Parses :class:`irclog.messages.SelfNickMessage`."""
    return irclog.messages.SelfNickMessage(when, selfnickto)


@parser
def joinmsg(when, joinnick, joinident, joinchan, **_):
    """Parses :class:`irclog.messages.JoinMessage`."""
    return irclog.messages.JoinMessage(when, joinnick, joinident, joinchan)


@parser
def modemsg(when, modeserver, modechan, modelist, modenick, **_):
    """Parses :class:`irclog.messages.ModeMessage`."""
    return irclog.messages.ModeMessage(when, modeserver, modechan,
                                       modelist, modenick)


@parser
def partmsg(when, partnick, partident, partchan, partreason, **_):
    """Parses :class:`irclog.messages.PartMessage`."""
    return irclog.messages.PartMessage(partnick, partident,
                                       partchan, partreason)


@parser
def quitmsg(when, quitnick, quitident, quitreason, **_):
    """Parses :class:`irclog.messages.QuitMessage`."""
    return irclog.messages.QuitMessage(when, quitnick, quitident, quitreason)


@parser
def kickmsg(when, kicknick, kickchan, kickby, kickreason, **_):
    """Parses :class:`irclog.messages.KickMessage`."""
    return irclog.messages.KickMessage(when, kicknick, kickchan,
                                       kickby, kickreason)


@parser
def topicmsg(when, topicnick, topicchan, topicline, **_):
    """Parses :class:`irclog.messages.TopicMessage`."""
    return irclog.messages.TopicMessage(when, topicnick, topicchan, topicline)


@parser
def notopicmsg(when, notopicnick, notopicchan, **_):
    """Parses :class:`irclog.messages.NoTopicMessage`."""
    return irclog.messages.TopicMessage(when, notopicnick, notopicchan)


@parser
def pubmsg(when, pubnick, publine, **_):
    """Parses :class:`irclog.messages.PublicMessage`."""
    return irclog.messages.PublicMessage(when, pubnick, publine)


@parser
def actmsg(when, actnick, actline, **_):
    """Parses :class:`irclog.messages.ActionMessage`."""
    return irclog.messages.ActionMessage(when, actnick, actline)


@parser
def noticemsg(when, noticenick, noticechan, noticeline, **_):
    """Parses :class:`irclog.messages.ActionMessage`."""
    return irclog.messages.NoticeMessage(when, noticenick,
                                         noticechan, noticeline)

