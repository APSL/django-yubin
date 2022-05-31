#!/usr/bin/env python
# encoding: utf-8
# ----------------------------------------------------------------------------

import hashlib
import base64


def unimplemented(*args, **kwargs):
    raise NotImplementedError


class Attachment(object):
    """
    Utility class to contain the attachment information
    """

    def __init__(self, mailpart):
        self.filename = mailpart['filename']
        self.tipus = mailpart['mail_content_type']
        self.charset = mailpart['charset']
        self.payload = base64.b64decode(mailpart['payload'])
        self.length = len(self.payload)
        self.firma = hashlib.md5(self.payload).hexdigest()


def get_attachments(msg):
    """
    Returns a list with all the mail attachments
    """

    attachments = []
    for attachment in msg.attachments:
        attachment_ = Attachment(attachment)
        attachments.append(attachment_)
    return attachments


def get_attachment(msg, key):
    """
    Given a msg returns the attachment who's signature (md5 key) matches
    the key value
    """

    for attachment in msg.attachments:
        attachment_ = Attachment(attachment)
        if attachment_.firma == key:
            return attachment_
    return None
