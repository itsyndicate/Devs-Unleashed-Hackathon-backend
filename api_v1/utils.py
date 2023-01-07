from rest_framework.exceptions import ValidationError


def validate_request(request, *field_names):
    """
    Validate request data to contain project_id and account_id.
    Raises ValidationError if not found
    """
    for field_name in field_names:
        if field_name not in request.data and field_name not in request.GET:
            raise ValidationError(f'{field_name} not found in request data')
