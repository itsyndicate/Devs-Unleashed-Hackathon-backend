from rest_framework.exceptions import ValidationError


def validate_request(request):
    """
    Validate request data to contain project_id and account_id.
    Raises ValidationError if not found
    """
    account_id = request.GET.get('account_id') or request.data.get('account_id')
    project_id = request.GET.get('project_id') or request.data.get('project_id')
    if not account_id or not project_id:
        raise ValidationError(detail={'error': 'account_id and project_id are required'})
