""":mod:`irclog.archive` --- IRC log archive
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. todo:: File encoding auto-detection.

.. data:: STRPTIME_TO_GLOB

   The table for translating :func:`strptime() <time.strptime>` directives to
   :mod:`glob` patterns.

.. data:: STRPTIME_DIRECTIVE_PATTERN

   The :mod:`re` pattern object that matches to
   :func:`strptime() <time.strptime>` directives.

   .. sourcecode:: pycon

      >>> fmtstr = "%Y-%m-%d"
      >>> STRPTIME_DIRECTIVE_PATTERN.sub(lambda m: STRPTIME_TO_GLOB[m.group(0)],
      ...                                fmtstr)
      '[0-9][0-9][0-9][0-9]-[01][0-9]-[0-3][0-9]'

"""
import re
import glob
import functools
import datetime
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
import irclog.parser


STRPTIME_TO_GLOB = {"%a": "???",
                    "%A": "*",
                    "%b": "???",
                    "%B": "*",
                    "%c": "*",
                    "%d": "[0-3][0-9]",
                    "%f": "[0-9]" * 6,
                    "%H": "[0-2][0-9]",
                    "%I": "[01][0-9]",
                    "%j": "[0-3][0-9][0-9]",
                    "%m": "[01][0-9]",
                    "%M": "[0-6][0-9]",
                    "%p": "[APap][Mm]",
                    "%S": "[0-6][0-9]",
                    "%U": "[0-5][0-9]",
                    "%w": "[0-6]",
                    "%W": "[0-5][0-9]",
                    "%x": "*",
                    "%X": "*",
                    "%y": "[0-9]" * 2,
                    "%Y": "[0-9]" * 4,
                    "%z": "*",
                    "%Z": "*",
                    "%%": "%"}
STRPTIME_TO_PATTERN = {"%a": "[Mm]on|[Tt]u[eu]|[Ww]ed|[Ff]ri|[Ss](?:at|un)",
                       "%A": "[Mm]onday|[Tt]uesday|[Ww]ednesday|[Tt]hursday"
                             "|[Ff]riday|[Ss]aturday|[Ss]unday",
                       "%b": "[Jj](?:an|u[nl])|[Ff]eb|[Mm]a[ry]|[Aa](?:pr|ug)"
                             "|[Ss]ep|[Oo]ct|[Nn]ov|[Dd]ec",
                       "%B": "[Jj]anuary|[Ff]ebruary|[Mm]arch|[Aa]pril|[Mm]ay"
                             "|[Jj]une|[Jj]uly|[Aa]ugust|[Ss]eptember"
                             "|[Oo]ctober|[Nn]ovember|[Dd]ecember",
                       "%c": ".+?",
                       "%d": "[012][0-9]|3[01]",
                       "%f": "[0-9]{6}",
                       "%H": "[0-1][0-9]|2[0-4]",
                       "%I": "0[0-9]|1[012]",
                       "%j": "[0-2][0-9][0-9]|3[0-5][0-9]|36[0-6]",
                       "%m": "0[0-9]|1[012]",
                       "%M": "[0-5][0-9]|60",
                       "%p": "[APap][Mm]",
                       "%S": "[0-5][0-9]|6[01]",
                       "%U": "[0-4][0-9]|5[0-3]",
                       "%w": "[0-6]",
                       "%W": "[0-4][0-9]|5[0-3]",
                       "%x": ".+?",
                       "%X": ".+?",
                       "%y": "[0-9]{2}",
                       "%Y": "[0-9]{4}",
                       "%z": "|[+-](?:[0-1][0-9]|2[0-4])(?:[0-5][0-9]|60)",
                       "%Z": ".*?",
                       "%%": "%"}
STRPTIME_DIRECTIVE_PATTERN = re.compile("|".join(STRPTIME_TO_GLOB.iterkeys()))


class FilenamePattern(object):
    """The glob-like, but specialized to IRC log files, filename pattern
    matcher.

    .. sourcecode:: pycon

       >>> pattern = FilenamePattern("/logs/<server>"
       ...                           "/<channel>.<date:%Y-%m-%d>.log")
       >>> pattern.glob_pattern_string()
       '/logs/*/*.[0-9][0-9][0-9][0-9]-[01][0-9]-[0-3][0-9].log'
       >>> pattern.glob_pattern_string(server="Freenode")
       '/logs/Freenode/*.[0-9][0-9][0-9][0-9]-[01][0-9]-[0-3][0-9].log'

    .. data:: REPLACER_PATTERN

       The pattern of replacer e.g. ``<date:%Y-%m-%d>``, ``<channel>``.

       .. productionlist::
          replacer: "<" `name` [ ":" `format` ] ">"
          name: /[A-Za-z_]+/
          format: /[^>]*/

    """

    REPLACER_PATTERN = re.compile(r"<(?P<name>[A-Za-z_]+)"
                                  r"(?::(?P<format>[^>]*))?>")

    __slots__ = "pattern", "_re_pattern"

    def __init__(self, pattern):
        self.pattern = pattern
        self._re_pattern = None

    @property
    def replacers(self):
        """The list of replacers.

        .. sourcecode:: pycon

           >>> pattern = FilenamePattern("/logs/<server>"
           ...                           "/<channel>.<date:%Y-%m-%d>.log")
           >>> list(pattern.replacers)
           ['server', 'channel', 'date']

        """
        for m in self.REPLACER_PATTERN.finditer(self.pattern):
            yield m.group("name")

    @property
    def replacer_pairs(self):
        """The list of replacers' ``(name, format)``. (For replacers have no
        format, ``(name, None)``.)

        .. sourcecode:: pycon

           >>> pattern = FilenamePattern("/logs/<server>"
           ...                           "/<channel>.<date:%Y-%m-%d>.log")
           >>> list(pattern.replacer_pairs)
           [('server', None), ('channel', None), ('date', '%Y-%m-%d')]

        """
        for m in self.REPLACER_PATTERN.finditer(self.pattern):
            yield m.group("name"), m.group("format") or None

    @property
    def replacer_dict(self):
        """The :class:`dict` of replacers.

        .. sourcecode:: pycon

           >>> pattern = FilenamePattern("/logs/<server>"
           ...                           "/<channel>.<date:%Y-%m-%d>.log")
           >>> pattern.replacer_dict["server"]
           >>> pattern.replacer_dict["date"]
           '%Y-%m-%d'
           >>> pattern.replacer_dict["xyz"]
           Traceback (most recent call last):
             ...
           KeyError: 'xyz'

        """
        return dict(self.replacer_pairs)

    def fill_replacers(self, replacers, escape=None):
        """Fills replacers with given values.

        .. sourcecode:: pycon

           >>> pattern = FilenamePattern("/logs/<server>"
           ...                           "/<channel>.<date:%Y-%m-%d>.log")
           >>> import datetime
           >>> pattern.fill_replacers({"server": "Freenode",
           ...                         "channel": "#hongminhee",
           ...                         "date": datetime.date(2010, 8, 4)})
           '/logs/Freenode/#hongminhee.2010-08-04.log'

        When ``escape`` function has given, non-replacers are applied into
        the function:

        .. sourcecode:: pycon

           >>> pattern.fill_replacers({"server": "Freenode",
           ...                         "channel": "#hongminhee",
           ...                         "date": datetime.date(2010, 8, 4)},
           ...                        escape=lambda x: x.upper())
           '/LOGS/Freenode/#hongminhee.2010-08-04.LOG'

        It may raise :exc:`KeyError` when too few replacers has given:

        .. sourcecode:: pycon

           >>> pattern.fill_replacers({"server": "Freenode"})
           Traceback (most recent call last):
             ...
           KeyError: 'channel'

        :param replacers: a mapping object of
                          ``(replacer_name, str_to_replace)``
        :type replacers: :class:`dict`, mapping object
        :returns: a filled filename

        """
        if not isinstance(replacers, dict):
            replacers = dict(replacers)
        pos = 0
        buffer = StringIO.StringIO()
        matches = self.REPLACER_PATTERN.finditer(self.pattern)
        for m in matches:
            if pos < m.start():
                part = self.pattern[pos:m.start()]
                buffer.write(escape(part) if escape else part)
            pos = m.end()
            value = replacers[m.group("name")]
            if m.group("format") and not isinstance(value, basestring):
                value = format(value, m.group("format"))
            buffer.write(value)
        part = self.pattern[pos:]
        buffer.write(escape(part) if escape else part)
        return buffer.getvalue()

    def glob_pattern_string(self, **replacers):
        """Generates a :mod:`glob` pattern string. It takes keyword arguments
        of replacers to fill also.

        .. sourcecode:: pycon

           >>> pattern = FilenamePattern("/logs/<server>"
           ...                           "/<channel>.<date:%Y-%m-%d>.log")
           >>> pattern.glob_pattern_string()
           '/logs/*/*.[0-9][0-9][0-9][0-9]-[01][0-9]-[0-3][0-9].log'
           >>> pattern.glob_pattern_string(server="Freenode")
           '/logs/Freenode/*.[0-9][0-9][0-9][0-9]-[01][0-9]-[0-3][0-9].log'
           >>> pattern.glob_pattern_string(channel="#hongminhee")
           '/logs/*/#hongminhee.[0-9][0-9][0-9][0-9]-[01][0-9]-[0-3][0-9].log'
           >>> import datetime
           >>> pattern.glob_pattern_string(date=datetime.date(2010, 8, 4))
           '/logs/*/*.2010-08-04.log'

        :param \*\*replacers: replacers to fill. keywords go replacer names and
                              values fills them
        :returns: a glob pattern string

        """
        for name, form in self.replacer_pairs:
            if name not in replacers:
                if form:
                    replacers[name] = STRPTIME_DIRECTIVE_PATTERN.sub(
                        lambda m: STRPTIME_TO_GLOB[m.group(0)],
                        form
                    )
                else:
                    replacers[name] = "*"
        return self.fill_replacers(replacers)

    def glob(self, **replacers):
        """Globs with the pattern.

        :param \*\*replacers: replacers to fill. keywords go replacer names and
                              values fills them
        :returns: a :class:`list` of all matched paths

        .. seealso::

           - Module :mod:`glob`
           - Function :func:`glob.glob()`

        """
        return glob.glob(self.glob_pattern_string(**replacers))

    def iglob(self, **replacers):
        """Case-insensitive version of :meth:`glob()`.

        :param \*\*replacers: replacers to fill. keywords go replacer names and
                              values fills them
        :returns: a :class:`list` of all matched paths
        
        .. seealso::

           - Module :mod:`glob`
           - Function :func:`glob.iglob()`

        """
        return glob.glob(self.glob_pattern_string(**replacers))

    def re_pattern_string(self, **replacers):
        r"""Generates a :mod:`re` pattern string. It takes keyword arguments of
        replacers to fill also.

        .. sourcecode:: pycon

           >>> import datetime
           >>> pattern = FilenamePattern("/<server>/<channel>.<date:%Y%m%d>")
           >>> pattern.re_pattern_string(date=datetime.date(2010, 8, 4))
           '^\\/(?P<server>.+?)\\/(?P<channel>.+?)\\.20100804$'

        :param \*\*replacers: replacers to fill. keywords go replacer names and
                              values fills them
        :returns: a :mod:`re` pattern string

        """
        def replace(m):
            return "(?:" + STRPTIME_TO_PATTERN[m.group(0)] + ")"
        for name, form in self.replacer_pairs:
            if name not in replacers:
                if form:
                    val = STRPTIME_DIRECTIVE_PATTERN.sub(replace, form)
                    val = "(?P<{0}>{1})".format(name, val)
                else:
                    val = "(?P<{0}>.+?)".format(name)
                replacers[name] = val
        return "^" + self.fill_replacers(replacers, escape=re.escape) + "$"

    def re_pattern(self, **replacers):
        """Generates a :mod:`re` pattern object. It takes keyword arguments of
        replacers to fill also.

        :param \*\*replacers: replacers to fill. keywords go replacer names and
                              values fills them
        :returns: a :mod:`re` pattern

        .. note::

           This method is the same to following code::

               re.compile(file_pattern.re_pattern_string(**replacers))

        """
        if not self._re_pattern:
            self._re_pattern = re.compile(self.re_pattern_string(**replacers))
        return self._re_pattern

    def __str__(self):
        return self.pattern

    def __repr__(self):
        t = type(self)
        mod = "" if t.__module__ == "__main__" else t.__module__ + "."
        return "{0}{1}({2!r})".format(mod, t.__name__, self.pattern)


class BaseArchive(object):
    """Abstract base class for :class:`Archive`, :class:`Server` and
    :class:`Channel`.

    .. data:: ELEMENT_CLASS

       Should be implemented in the subclass.

    .. data:: ELEMNENT_TAG

       Should be implemented in the subclass.

    .. attribute:: pattern_replacers

       Should be implemented in the subclass.

    """

    pattern_replacers = {}

    def __iter__(self):
        regex = self.pattern.re_pattern(**self.pattern_replacers)
        files = self.pattern.glob(**self.pattern_replacers)
        files.sort()
        elements = []
        for path in files:
            match = regex.match(path)
            if match:
                try:
                    el = self.decode_element_key(match.group(self.ELEMENT_TAG))
                except IndexError:
                    continue
                if el not in elements:
                    elements.append(el)
                    yield self.ELEMENT_CLASS(self, el)

    def decode_element_key(self, element_key):
        """Decodes an element key string to element key.

        :param element_key: an element key string
        :type element_key: :class:`basestring`
        :returns: an element key

        """
        return element_key

    def encode_element_key(self, element_key):
        """Encodes am element key to element key string.

        :param element_key: an element key
        :returns: an element key string

        """
        form = self.pattern.replacer_dict[self.ELEMENT_TAG]
        if form:
            return format(element_key, form)
        return str(element_key)

    def __contains__(self, element):
        replacers = dict(self.pattern_replacers)
        replacers[self.ELEMENT_TAG] = self.encode_element_key(element)
        paths = self.pattern.glob(**replacers)
        return bool(paths)

    def __getitem__(self, element):
        if element in self:
            return self.ELEMENT_CLASS(self, element)
        raise KeyError(element)

    def __len__(self):
        cnt = 0
        for _ in self:
            cnt += 1
        return cnt


class Archive(BaseArchive):
    """Log archive.

    :param pattern: logs filename pattern
                    e.g. ``"/logs/<server>/<channel>.<date:%Y-%m-%d>.log"``
    :type pattern: :class:`FilenamePattern`, :class:`basestring`

    """

    ELEMENT_CLASS = lambda *a, **k: Server(*a, **k)
    ELEMENT_TAG = "server"

    __slots__ = "pattern",

    def __init__(self, pattern):
        if not isinstance(pattern, FilenamePattern):
            pattern = FilenamePattern(pattern)
        self.pattern = pattern

    def __repr__(self):
        t = type(self)
        mod = "" if t.__module__ == "__main__" else t.__module__ + "."
        return "{0}{1}({2!r})".format(mod, t.__name__, str(self.pattern))


class Server(BaseArchive):
    """IRC server.

    :param archive: an archive
    :type archive: :class:`Archive`
    :param server: a server name
    :type server: :class:`basestring`

    """

    ELEMENT_CLASS = lambda *a, **k: Channel(*a, **k)
    ELEMENT_TAG = "channel"

    __slots__ = "archive", "server"

    def __init__(self, archive, server):
        self.archive = archive
        self.server = server

    @property
    def pattern(self):
        return self.archive.pattern

    @property
    def pattern_replacers(self):
        replacers = dict(self.archive.pattern_replacers)
        replacers["server"] = self.server
        return replacers

    def __eq__(self, other):
        return self.archive == other.archive and self.server == other.server

    def __ne__(self, other):
        return not (self == other)

    def __str__(self):
        return self.server

    def __repr__(self):
        t = type(self)
        mod = "" if t.__module__ == "__main__" else t.__module__ + "."
        clsname = mod + t.__name__
        return "{0}({1!r}, {2!r})".format(clsname, self.archive, self.server)


class Channel(BaseArchive):
    """IRC channel or nick.

    :param server: a server
    :type server: :class:`Server`
    :param channel: a channel name or a nick
    :type channel: :class:`basestring`

    """

    ELEMENT_CLASS = lambda *a, **k: Log(*a, **k)
    ELEMENT_TAG = "date"

    __slots__ = "server", "channel"

    def __init__(self, server, channel):
        self.server = server
        self.channel = channel

    @property
    def archive(self):
        return self.server.archive

    @property
    def pattern(self):
        return self.archive.pattern

    @property
    def pattern_replacers(self):
        replacers = dict(self.server.pattern_replacers)
        replacers["channel"] = self.channel
        return replacers

    def decode_element_key(self, element_key):
        """Decodes an element key string to element key.

        :param element_key: an element key string
        :type element_key: :class:`basestring`
        :returns: an element key

        """
        form = self.pattern.replacer_dict[self.ELEMENT_TAG] or "%Y-%m-%d"
        time = datetime.datetime.strptime(element_key, form)
        return time.date()

    def encode_element_key(self, element_key):
        """Encodes am element key to element key string.

        :param element_key: an element key
        :returns: an element key string

        """
        if not isinstance(element_key, datetime.date):
            raise TypeError("expected a datetime.date instance, "
                            "not " + repr(element_key))
        return super(Channel, self).encode_element_key(element_key)

    def __contains__(self, date):
        return True

    def __eq__(self, other):
        return self.server == other.server and self.channel == other.channel

    def __ne__(self, other):
        return not (self == other)

    def __str__(self):
        return self.channel

    def __unicode__(self):
        try:
            return self.channel.decode("utf-8")
        except UnicodeDecodeError:
            from os import environ
            try:
                _, enc = environ["LANG"].split(".")
            except (LookupError, ValueError):
                return self.channel.decode("utf-8", "replace")
            return self.channel.decode(enc, "replace")

    def __repr__(self):
        t = type(self)
        mod = "" if t.__module__ == "__main__" else t.__module__ + "."
        clsname = mod + t.__name__
        return "{0}({1!r}, {2!r})".format(clsname, self.server, self.channel)


class Log(object):
    """IRC log.

    :param channel: a channel logged
    :type channel: :class:`Channel`
    :param date: a date logged
    :type date: :class:`datetime.date`

    """

    __slots__ = "channel", "date"

    def __init__(self, channel, date):
        self.channel = channel
        self.date = date

    @property
    def server(self):
        """The server."""
        return self.channel.server

    @property
    def archive(self):
        """The archive."""
        return self.server.archive

    @property
    def pattern(self):
        """The filename pattern."""
        return self.archive.pattern

    @property
    def yesterday_log(self):
        """The yesterday log of the same channel."""
        return self.channel[self.date - datetime.timedelta(days=1)]

    @property
    def tomorrow_log(self):
        """The tomorrow log of the same channel."""
        return self.channel[self.date + datetime.timedelta(days=1)]

    def is_logged(self):
        """Returns ``True`` if the channel of the day has logged.

        :returns: ``True`` or ``False``

        """
        replacers = dict(self.channel.pattern_replacers)
        replacers["date"] = self.channel.encode_element_key(self.date)
        files = self.pattern.glob(**replacers)
        return bool(files)

    def __eq__(self, other):
        return self.channel == other.channel and self.date == other.date

    def __ne__(self, other):
        return not (self == other)

    def __iter__(self):
        replacers = dict(self.channel.pattern_replacers)
        replacers["date"] = self.channel.encode_element_key(self.date)
        files = self.pattern.glob(**replacers)
        if not files:
            return
        with open(files[0]) as file:
            for msg in irclog.parser.parse(file, self.date):
                yield msg

    def __repr__(self):
        t = type(self)
        mod = "" if t.__module__ == "__main__" else t.__module__ + "."
        clsname = mod + t.__name__
        return "{0}({1!r}, {2!r})".format(clsname, self.channel, self.date)


Archive.ELEMENT_CLASS = Server
Server.ELEMENT_CLASS = Channel
Channel.ELEMENT_CLASS = Log

