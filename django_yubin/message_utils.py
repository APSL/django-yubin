import hashlib


class Attachment:
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


def get_attachments(pyz_msg):
    """
    Returns a list with all the mail attachments
    """
    attachments = []
    for mailpart in pyz_msg.mailparts:
        if not mailpart.is_body and mailpart.disposition == 'attachment':
            attachment = Attachment(mailpart)
            attachments.append(attachment)
    return attachments


def get_attachment(pyz_msg, key):
    """
    Given a msg returns the attachment who's signature (md5 key) matches
    the key value
    """
    for mailpart in pyz_msg.mailparts:
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


def get_address(pyz_msg, header_name):
    """
    Returns 'Foo Bar <foo.bar@baz.com>' or 'foo.bar@baz.com'.

    @header_name can be 'from', 'to', 'cc', 'bcc'.
    """
    addresses = get_addresses(pyz_msg, header_name)
    return addresses[0] if addresses else None


def get_addresses(pyz_msg, header_name):
    """
    Returns ['Foo Bar <foo.bar@baz.com>', ...] or ['foo.bar@baz.com', ...].

    @header_name can be 'from', 'to', 'cc', 'bcc'.
    """
    addresses = []
    for address in pyz_msg.get_addresses(header_name):
        if not address[0] or '@' in address[0]:
            addresses.append(address[1])
        else:
            addresses.append('{} <{}>'.format(address[0], address[1]))
    return addresses


def get_body(pyz_msg):
    if pyz_msg.text_part:
        return pyz_msg.text_part.part.get_payload(decode=is_part_encoded(pyz_msg, 'text_part'))
    return ''
