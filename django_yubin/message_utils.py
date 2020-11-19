import hashlib


class Attachment(object):
    """
    Utility class to contain the attachment information
    """

    def __init__(self, mailpart):
        self.filename = mailpart.sanitized_filename
        self.type = mailpart.type
        self.charset = mailpart.charset
        self.content_description = mailpart.part.get('Content-Description')
        self.payload = mailpart.get_payload()
        self.length = len(self.payload)
        self.signature = hashlib.md5(self.payload).hexdigest()


def get_attachments(msg):
    """
    Returns a list with all the mail attachments
    """
    attachments = []
    for mailpart in msg.mailparts:
        if not mailpart.is_body and mailpart.disposition == 'attachment':
            attachment = Attachment(mailpart)
            attachments.append(attachment)
    return attachments


def get_attachment(msg, key):
    """
    Given a msg returns the attachment who's signature (md5 key) matches
    the key value
    """
    for mailpart in msg.mailparts:
        if not mailpart.is_body and mailpart.disposition == 'attachment':
            attachment = Attachment(mailpart)
            if attachment.signature == key:
                return attachment
    return None


def is_part_encoded(pyz_msg, part='html_part'):
    """
    Detect whether the part is encoded or not. We'll check for known encoding headers
    """
    if part == 'html_part':
        return any(is_header_encoding(header[1]) for header in pyz_msg.html_part.part._headers)
    elif part == 'text_part':
        return any(is_header_encoding(header[1]) for header in pyz_msg.text_part.part._headers)
    return False


def is_header_encoding(header_name):
    return header_name in ('base64', 'quoted-printable')
