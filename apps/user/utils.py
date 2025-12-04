from apps.user.models import UserActivity

def log_user_activity(request, user, action_type, description, metadata=None):
    ip = (
        request.META.get('HTTP_X_FORWARDED_FOR')
        or request.META.get('REMOTE_ADDR') or None
    )
    if ip and ',' in ip:
        ip = ip.split(',')[0].strip()
    
    print('\n' * 10)
    print(user)
    print(ip)
    print('\n' * 10)
    UserActivity.log_activity(
        user=user if user.is_authenticated else None,
        action_type=action_type,
        description=description,
        metadata=metadata,
        ip=ip
    )