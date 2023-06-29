import base64
import hashlib


def get_content(attachment):
    return base64.b64decode(attachment['payload'])


def get_signature(attachment):
    return hashlib.md5(get_content(attachment)).hexdigest()


def get_attachment(mailparser, signature):
    """
    Given a msg returns the attachment with the given signature.
    """
    for attachment in mailparser.attachments:
        if get_signature(attachment) == signature:
            return attachment
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
