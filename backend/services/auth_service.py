"""
Authentication service for JWT token management and user authentication
"""

import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from models.user import User

class AuthService:
    def __init__(self, secret_key=None, algorithm='HS256'):
        self.secret_key = secret_key or os.environ.get("SKJ_SECRET", "dev-secret-change-me")
        self.algorithm = algorithm
    
    def generate_token(self, user, expires_in_hours=24):
        """Generate JWT token for user"""
        payload = {
            'user_id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token):
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_current_user(self):
        """Get current user from request headers"""
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        payload = self.verify_token(token)
        
        if not payload:
            return None
        
        # Update user's last active time
        user = User.find_by_id(payload.get('user_id'))
        if user:
            user.update_last_active()
        
        return user
    
    def authenticate_user(self, identifier, password):
        """Authenticate user by name/email and password"""
        # Try to find user by name first, then by email
        user = User.find_by_name(identifier)
        if not user and '@' in identifier:
            user = User.find_by_email(identifier)
        
        if not user:
            return None
        
        if not user.check_password(password):
            return None
        
        return user
    
    def register_user(self, name, email=None, password=None, role='student'):
        """Register a new user"""
        try:
            user = User.create_user(
                name=name,
                email=email,
                password=password,
                role=role
            )
            return user
        except ValueError as e:
            raise e

# Global auth service instance
auth_service = AuthService()

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = auth_service.get_current_user()
        if not user:
            return jsonify({'error': 'Token is missing or invalid'}), 401
        return f(current_user=user, *args, **kwargs)
    return decorated

def role_required(*allowed_roles):
    """Decorator to require specific user roles"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = auth_service.get_current_user()
            if not user:
                return jsonify({'error': 'Token is missing or invalid'}), 401
            
            if user.role not in allowed_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(current_user=user, *args, **kwargs)
        return decorated
    return decorator

def optional_auth(f):
    """Decorator for optional authentication (user can be None)"""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = auth_service.get_current_user()
        return f(current_user=user, *args, **kwargs)
    return decorated