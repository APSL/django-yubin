#!/usr/bin/env python
# encoding: utf-8
# ----------------------------------------------------------------------------

import hashlib


def unimplemented(*args, **kwargs):
    raise NotImplementedError


class Attachment(object):
    """
    Utility class to contain the attachment information
    """

    def __init__(self, mailpart):
        self.filename = mailpart.get("filename")
        self.tipus = mailpart.get("mail_content_type")
        self.charset = mailpart.get("charset")
        # self.content_description = mailpart.part.get("Content-Description")
        self.payload = mailpart.get("payload")
        self.length = len(self.payload)
        self.firma = hashlib.md5(self.payload.encode()).hexdigest()


def get_attachments(msg):
    """
    Returns a list with all the mail attachments
    """

    attachments = []

    for attachment in msg.attachments:
        attachments.append(Attachment(attachment))
    return attachments


def get_attachment(msg, key):
    """
    Given a msg returns the attachment who's signature (md5 key) matches
    the key value
    """

    for attachment in msg.attachments:
        attachment = Attachment(attachment)
        if attachment.firma == key:
            return attachment
    return None
