
# custom colour validator

from wtforms import ValidationError
import re

HEX_COLOUR_RE = re.compile(r'^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$')


class HexColour:
    def __init__(self, message=None):
        self.message = message or 'Invalid hex colour code.'

    def __call__(self, form, field):
        data = (field.data or '').strip()
        if not data:
            return  # Allow empty field
        if not HEX_COLOUR_RE.match(data):
            raise ValidationError(self.message)
