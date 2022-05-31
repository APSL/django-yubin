import base64
import hashlib


class Attachment:
    """
    Utility class to contain the attachment information
    """
    def __init__(self, mailpart):
        self.filename = mailpart['filename']
        self.type = mailpart['mail_content_type']
        self.charset = mailpart['charset']
        self.payload = base64.b64decode(mailpart['payload'])
        self.length = len(self.payload)
        self.signature = hashlib.md5(self.payload).hexdigest()


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
    Given a msg returns the attachment who's signature (md5 key) matches the key value
    """
    for attachment in msg.attachments:
        attachment_ = Attachment(attachment)
        if attachment_.signature == key:
            return attachment_
    return None


def get_address(mailparse_addresses):
    """
    Returns 'Foo Bar <foo.bar@baz.com>' or 'foo.bar@baz.com'.
    """
    addresses = get_addresses(mailparse_addresses)
    return addresses[0] if addresses else None


def get_addresses(mailparse_addresses):
    """
    Returns ['Foo Bar <foo.bar@baz.com>', ...] or ['foo.bar@baz.com', ...].
    """
    addresses = []
    for address_parts in mailparse_addresses:
        if not address_parts[0] or '@' in address_parts[0]:
            addresses.append(address_parts[1])
        else:
            addresses.append('{} <{}>'.format(address_parts[0], address_parts[1]))
    return addresses
