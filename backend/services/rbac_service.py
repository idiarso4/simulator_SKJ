"""
Role-Based Access Control (RBAC) Service
"""

from enum import Enum
from functools import wraps
from flask import jsonify
from services.auth_service import auth_service

class Role(Enum):
    """User roles with hierarchy"""
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class Permission(Enum):
    """System permissions"""
    # User management
    VIEW_USERS = "view_users"
    CREATE_USERS = "create_users"
    EDIT_USERS = "edit_users"
    DELETE_USERS = "delete_users"
    
    # Class management
    VIEW_CLASSES = "view_classes"
    CREATE_CLASSES = "create_classes"
    EDIT_CLASSES = "edit_classes"
    DELETE_CLASSES = "delete_classes"
    MANAGE_CLASS_MEMBERS = "manage_class_members"
    
    # Challenge management
    VIEW_CHALLENGES = "view_challenges"
    CREATE_CHALLENGES = "create_challenges"
    EDIT_CHALLENGES = "edit_challenges"
    DELETE_CHALLENGES = "delete_challenges"
    
    # Content management
    VIEW_CONTENT = "view_content"
    CREATE_CONTENT = "create_content"
    EDIT_CONTENT = "edit_content"
    DELETE_CONTENT = "delete_content"
    PUBLISH_CONTENT = "publish_content"
    
    # Analytics and progress
    VIEW_OWN_PROGRESS = "view_own_progress"
    VIEW_STUDENT_PROGRESS = "view_student_progress"
    VIEW_ALL_PROGRESS = "view_all_progress"
    EXPORT_REPORTS = "export_reports"
    
    # Team challenges
    JOIN_TEAM_CHALLENGES = "join_team_challenges"
    CREATE_TEAM_CHALLENGES = "create_team_challenges"
    
    # Achievements
    VIEW_ACHIEVEMENTS = "view_achievements"
    MANAGE_ACHIEVEMENTS = "manage_achievements"
    
    # System administration
    MANAGE_SYSTEM = "manage_system"
    VIEW_LOGS = "view_logs"

class RBACService:
    """Role-Based Access Control Service"""
    
    def __init__(self):
        self.role_permissions = self._define_role_permissions()
    
    def _define_role_permissions(self):
        """Define permissions for each role"""
        return {
            Role.STUDENT: {
                # Basic user permissions
                Permission.VIEW_OWN_PROGRESS,
                Permission.VIEW_CHALLENGES,
                Permission.VIEW_CONTENT,
                Permission.VIEW_ACHIEVEMENTS,
                Permission.JOIN_TEAM_CHALLENGES,
            },
            
            Role.TEACHER: {
                # All student permissions
                Permission.VIEW_OWN_PROGRESS,
                Permission.VIEW_CHALLENGES,
                Permission.VIEW_CONTENT,
                Permission.VIEW_ACHIEVEMENTS,
                Permission.JOIN_TEAM_CHALLENGES,
                
                # Teacher-specific permissions
                Permission.VIEW_USERS,
                Permission.VIEW_CLASSES,
                Permission.CREATE_CLASSES,
                Permission.EDIT_CLASSES,
                Permission.MANAGE_CLASS_MEMBERS,
                Permission.VIEW_STUDENT_PROGRESS,
                Permission.CREATE_CHALLENGES,
                Permission.EDIT_CHALLENGES,
                Permission.CREATE_CONTENT,
                Permission.EDIT_CONTENT,
                Permission.PUBLISH_CONTENT,
                Permission.CREATE_TEAM_CHALLENGES,
                Permission.EXPORT_REPORTS,
            },
            
            Role.ADMIN: {
                # All permissions
                Permission.VIEW_USERS,
                Permission.CREATE_USERS,
                Permission.EDIT_USERS,
                Permission.DELETE_USERS,
                Permission.VIEW_CLASSES,
                Permission.CREATE_CLASSES,
                Permission.EDIT_CLASSES,
                Permission.DELETE_CLASSES,
                Permission.MANAGE_CLASS_MEMBERS,
                Permission.VIEW_CHALLENGES,
                Permission.CREATE_CHALLENGES,
                Permission.EDIT_CHALLENGES,
                Permission.DELETE_CHALLENGES,
                Permission.VIEW_CONTENT,
                Permission.CREATE_CONTENT,
                Permission.EDIT_CONTENT,
                Permission.DELETE_CONTENT,
                Permission.PUBLISH_CONTENT,
                Permission.VIEW_OWN_PROGRESS,
                Permission.VIEW_STUDENT_PROGRESS,
                Permission.VIEW_ALL_PROGRESS,
                Permission.EXPORT_REPORTS,
                Permission.JOIN_TEAM_CHALLENGES,
                Permission.CREATE_TEAM_CHALLENGES,
                Permission.VIEW_ACHIEVEMENTS,
                Permission.MANAGE_ACHIEVEMENTS,
                Permission.MANAGE_SYSTEM,
                Permission.VIEW_LOGS,
            }
        }
    
    def has_permission(self, user_role, permission):
        """Check if a role has a specific permission"""
        try:
            role_enum = Role(user_role)
            permission_enum = Permission(permission) if isinstance(permission, str) else permission
            return permission_enum in self.role_permissions.get(role_enum, set())
        except ValueError:
            return False
    
    def get_user_permissions(self, user_role):
        """Get all permissions for a user role"""
        try:
            role_enum = Role(user_role)
            return [perm.value for perm in self.role_permissions.get(role_enum, set())]
        except ValueError:
            return []
    
    def can_access_user_data(self, current_user, target_user_id):
        """Check if current user can access target user's data"""
        # Handle None user
        if not current_user:
            return False
        
        # Users can always access their own data
        if current_user.id == target_user_id:
            return True
        
        # Admins can access all user data
        if current_user.role == "admin":
            return self.has_permission(current_user.role, Permission.VIEW_ALL_PROGRESS)
        
        # Teachers can access student data but not admin data
        if current_user.role == "teacher":
            # Need to check if target user is a student
            # For now, teachers can access data if they have the permission
            # but we should add logic to prevent accessing admin data
            from models.user import User
            target_user = User.find_by_id(target_user_id)
            if target_user and target_user.role == "admin":
                return False  # Teachers cannot access admin data
            return self.has_permission(current_user.role, Permission.VIEW_STUDENT_PROGRESS)
        
        return False
    
    def can_manage_class(self, current_user, class_id=None):
        """Check if user can manage a specific class"""
        if current_user.role == "admin":
            return True
        
        if current_user.role == "teacher":
            if class_id is None:
                return self.has_permission(current_user.role, Permission.CREATE_CLASSES)
            
            # Check if teacher owns this class (would need to query database)
            return self.has_permission(current_user.role, Permission.EDIT_CLASSES)
        
        return False

# Global RBAC service instance
rbac_service = RBACService()

def require_permission(permission):
    """Decorator to require specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            current_user = auth_service.get_current_user()
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            if not rbac_service.has_permission(current_user.role, permission):
                return jsonify({
                    'error': 'Insufficient permissions',
                    'required_permission': permission.value if hasattr(permission, 'value') else permission
                }), 403
            
            return f(current_user=current_user, *args, **kwargs)
        return decorated
    return decorator

def require_any_permission(*permissions):
    """Decorator to require any of the specified permissions"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            current_user = auth_service.get_current_user()
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            has_any_permission = any(
                rbac_service.has_permission(current_user.role, perm) 
                for perm in permissions
            )
            
            if not has_any_permission:
                return jsonify({
                    'error': 'Insufficient permissions',
                    'required_permissions': [
                        perm.value if hasattr(perm, 'value') else perm 
                        for perm in permissions
                    ]
                }), 403
            
            return f(current_user=current_user, *args, **kwargs)
        return decorated
    return decorator

def require_role(*allowed_roles):
    """Decorator to require specific roles (backward compatibility)"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            current_user = auth_service.get_current_user()
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            if current_user.role not in allowed_roles:
                return jsonify({
                    'error': 'Insufficient permissions',
                    'required_roles': list(allowed_roles),
                    'current_role': current_user.role
                }), 403
            
            return f(current_user=current_user, *args, **kwargs)
        return decorated
    return decorator

def require_own_resource_or_permission(resource_user_id_param, permission):
    """Decorator to require access to own resource or specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            current_user = auth_service.get_current_user()
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            # Get the resource user ID from kwargs
            resource_user_id = kwargs.get(resource_user_id_param)
            
            # Allow access to own resource
            if current_user.id == resource_user_id:
                return f(current_user=current_user, *args, **kwargs)
            
            # Check for required permission
            if not rbac_service.has_permission(current_user.role, permission):
                return jsonify({
                    'error': 'Insufficient permissions',
                    'message': 'You can only access your own resources or need higher permissions'
                }), 403
            
            return f(current_user=current_user, *args, **kwargs)
        return decorated
    return decorator