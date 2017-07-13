#
# This file is part of pyasn1 software.
#
# Copyright (c) 2005-2017, Ilya Etingof <etingof@gmail.com>
# License: http://pyasn1.sf.net/license.html
#
import datetime
from pyasn1.type import univ, char, tag
from pyasn1 import error

__all__ = ['ObjectDescriptor', 'GeneralizedTime', 'UTCTime']

NoValue = univ.NoValue
noValue = univ.noValue


class ObjectDescriptor(char.GraphicString):
    __doc__ = char.GraphicString.__doc__

    #: Default :py:class:`~pyasn1.type.tag.TagSet` object for |ASN.1| objects
    tagSet = char.GraphicString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 7)
    )


class TimeMixIn(object):
    class FixedOffset(datetime.tzinfo):
        """Fixed offset in minutes east from UTC."""

        def __init__(self, offset, name):
            self.__offset = datetime.timedelta(minutes=offset)
            self.__name = name

        def utcoffset(self, dt):
            return self.__offset

        def tzname(self, dt):
            return self.__name

        def dst(self, dt):
            return datetime.timedelta(0)

    @property
    def asDateTime(self):
        string = str(self)
        if string.endswith('Z'):
            tzinfo = TimeMixIn.FixedOffset(0, 'UTC')
            string = string[:-1]

        elif string[-5] in ('-', '+'):
            try:
                minutes = int(string[-4:-2]) * 60 + int(string[:-2])
                if string[-5] == '-':
                    minutes *= -1

            except ValueError:
                raise error.PyAsn1Error('unknown time specification %s' % self)

            tzinfo = TimeMixIn.FixedOffset(minutes, '?')
            string = string[:-5]

        else:
            tzinfo = None

        if '.' in string:
            try:
                string, _, ms = string.partition('.')
                ms = int(ms) * 100000

            except ValueError:
                raise error.PyAsn1Error('bad sub-second time specification %s' % self)

        else:
            ms = 0

        dt = datetime.datetime.strptime(string, '%Y%m%d%H%M%S')
        dt.replace(microsecond=ms, tzinfo=tzinfo)

        return dt

    @classmethod
    def fromDateTime(cls, dt):
        string = dt.strftime('%Y%m%d%H%M%S.%%d')
        string = string % (dt.microsecond // 10000)
        if dt.utcoffset():
            seconds = dt.utcoffset().seconds
            if seconds < 0:
                string += '-'
            else:
                string += '+'
            string += '%.2d%.2d' % (seconds // 3600, seconds % 3600)
        else:
            string += 'Z'
        return cls(string)


class GeneralizedTime(char.VisibleString, TimeMixIn):
    __doc__ = char.VisibleString.__doc__

    #: Default :py:class:`~pyasn1.type.tag.TagSet` object for |ASN.1| objects
    tagSet = char.VisibleString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 24)
    )


class UTCTime(char.VisibleString, TimeMixIn):
    __doc__ = char.VisibleString.__doc__

    #: Default :py:class:`~pyasn1.type.tag.TagSet` object for |ASN.1| objects
    tagSet = char.VisibleString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 23)
    )
