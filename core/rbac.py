from fastapi import Depends
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.shared.enums import UserRole
from api.core.exceptions import PermissionDeniedException

def require_role(*required_roles: UserRole):
    """
    Dependency to enforce role-based access control.
    Admin always has access.
    """
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role == UserRole.ADMIN:
            return current_user
        
        if current_user.role not in required_roles:
             raise PermissionDeniedException()
        
        return current_user
    return role_checker
