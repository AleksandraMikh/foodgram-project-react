from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


def validate_username(value):
    restricted_names = ['me', ]
    for restricted_name in restricted_names:
        if value == restricted_name:
            raise ValidationError(
                message=f'Невозможно выбрать имя пользователя "{value}"'
            )


class CustomSlugValidator(RegexValidator):
    '''
    Slug validator which restricts hyphen usage
    '''
    regex = r'^[a-zA-Z0-9_]+$'
    message = ('Slug must contain'
               ' only latin letters'
               ' or underlining')
