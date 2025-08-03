#!/usr/bin/env python3
"""
Test script for RBAC decorators and middleware
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models.user import User
from services.rbac_service import (
    rbac_service, require_permission, require_any_permission, 
    require_role, require_own_resource_or_permission, Permission
)
from services.auth_service import auth_service
from database import setup_database, seed_if_empty

def test_rbac_decorators():
    """Test RBAC decorators functionality"""
    print("Testing RBAC Decorators and Middleware...")
    
    # Setup database and Flask app
    setup_database()
    seed_if_empty()
    
    app = Flask(__name__)
    
    # Create test users
    try:
        student = User.create_user("test_student", "student@test.com", "pass", "student")
        teacher = User.create_user("test_teacher", "teacher@test.com", "pass", "teacher")
        admin = User.create_user("test_admin", "admin@test.com", "pass", "admin")
        print("   ✓ Created test users")
    except Exception as e:
        print(f"   ✗ Failed to create test users: {e}")
        return False
    
    # Test 1: Test require_permission decorator
    print("\n1. Testing require_permission decorator...")
    
    @require_permission(Permission.VIEW_USERS)
    def view_users_endpoint(current_user):
        return {"message": "success", "user": current_user.name}
    
    with app.app_context():
        # Mock request context for student (should fail)
        class MockRequest:
            def __init__(self, user):
                self.headers = {"Authorization": f"Bearer {auth_service.generate_token(user)}"}
        
        # Test student access (should be denied)
        with app.test_request_context(headers={"Authorization": f"Bearer {auth_service.generate_token(student)}"}):
            try:
                result = view_users_endpoint()
                print("   ✗ Student incorrectly allowed access")
                return False
            except Exception:
                print("   ✓ Student correctly denied access")
        
        # Test teacher access (should be allowed)
        with app.test_request_context(headers={"Authorization": f"Bearer {auth_service.generate_token(teacher)}"}):
            try:
                result = view_users_endpoint()
                if result and result.get("message") == "success":
                    print("   ✓ Teacher correctly allowed access")
                else:
                    print("   ✗ Teacher access failed")
                    return False
            except Exception as e:
                print(f"   ✗ Teacher access error: {e}")
                return False
    
    # Test 2: Test require_role decorator
    print("\n2. Testing require_role decorator...")
    
    @require_role("admin")
    def admin_only_endpoint(current_user):
        return {"message": "admin_success", "user": current_user.name}
    
    with app.app_context():
        # Test student access (should be denied)
        with app.test_request_context(headers={"Authorization": f"Bearer {auth_service.generate_token(student)}"}):
            try:
                result = admin_only_endpoint()
                print("   ✗ Student incorrectly allowed admin access")
                return False
            except Exception:
                print("   ✓ Student correctly denied admin access")
        
        # Test admin access (should be allowed)
        with app.test_request_context(headers={"Authorization": f"Bearer {auth_service.generate_token(admin)}"}):
            try:
                result = admin_only_endpoint()
                if result and result.get("message") == "admin_success":
                    print("   ✓ Admin correctly allowed access")
                else:
                    print("   ✗ Admin access failed")
                    return False
            except Exception as e:
                print(f"   ✗ Admin access error: {e}")
                return False
    
    # Test 3: Test require_any_permission decorator
    print("\n3. Testing require_any_permission decorator...")
    
    @require_any_permission(Permission.VIEW_USERS, Permission.VIEW_STUDENT_PROGRESS)
    def flexible_endpoint(current_user):
        return {"message": "flexible_success", "user": current_user.name}
    
    with app.app_context():
        # Test student access (should be denied - has neither permission)
        with app.test_request_context(headers={"Authorization": f"Bearer {auth_service.generate_token(student)}"}):
            try:
                result = flexible_endpoint()
                print("   ✗ Student incorrectly allowed flexible access")
                return False
            except Exception:
                print("   ✓ Student correctly denied flexible access")
        
        # Test teacher access (should be allowed - has VIEW_STUDENT_PROGRESS)
        with app.test_request_context(headers={"Authorization": f"Bearer {auth_service.generate_token(teacher)}"}):
            try:
                result = flexible_endpoint()
                if result and result.get("message") == "flexible_success":
                    print("   ✓ Teacher correctly allowed flexible access")
                else:
                    print("   ✗ Teacher flexible access failed")
                    return False
            except Exception as e:
                print(f"   ✗ Teacher flexible access error: {e}")
                return False
    
    # Test 4: Test require_own_resource_or_permission decorator
    print("\n4. Testing require_own_resource_or_permission decorator...")
    
    @require_own_resource_or_permission('user_id', Permission.VIEW_USERS)
    def user_profile_endpoint(current_user, user_id):
        return {"message": "profile_success", "user": current_user.name, "target_id": user_id}
    
    with app.app_context():
        # Test student accessing own profile (should be allowed)
        with app.test_request_context(headers={"Authorization": f"Bearer {auth_service.generate_token(student)}"}):
            try:
                result = user_profile_endpoint(user_id=student.id)
                if result and result.get("message") == "profile_success":
                    print("   ✓ Student can access own profile")
                else:
                    print("   ✗ Student own profile access failed")
                    return False
            except Exception as e:
                print(f"   ✗ Student own profile error: {e}")
                return False
        
        # Test student accessing other's profile (should be denied)
        with app.test_request_context(headers={"Authorization": f"Bearer {auth_service.generate_token(student)}"}):
            try:
                result = user_profile_endpoint(user_id=teacher.id)
                print("   ✗ Student incorrectly allowed access to other's profile")
                return False
            except Exception:
                print("   ✓ Student correctly denied access to other's profile")
        
        # Test teacher accessing student profile (should be allowed - has VIEW_USERS permission)
        with app.test_request_context(headers={"Authorization": f"Bearer {auth_service.generate_token(teacher)}"}):
            try:
                result = user_profile_endpoint(user_id=student.id)
                if result and result.get("message") == "profile_success":
                    print("   ✓ Teacher can access student profile")
                else:
                    print("   ✗ Teacher student profile access failed")
                    return False
            except Exception as e:
                print(f"   ✗ Teacher student profile error: {e}")
                return False
    
    # Test 5: Test permission validation logic
    print("\n5. Testing permission validation logic...")
    
    # Test specific permission checks
    test_cases = [
        (student, Permission.VIEW_OWN_PROGRESS, True),
        (student, Permission.VIEW_USERS, False),
        (teacher, Permission.VIEW_STUDENT_PROGRESS, True),
        (teacher, Permission.DELETE_USERS, False),
        (admin, Permission.MANAGE_SYSTEM, True),
        (admin, Permission.VIEW_OWN_PROGRESS, True),
    ]
    
    for user, permission, expected in test_cases:
        result = rbac_service.has_permission(user.role, permission)
        if result == expected:
            status = "✓" if expected else "✓"
            action = "has" if expected else "doesn't have"
            print(f"   {status} {user.role.capitalize()} correctly {action} {permission.value}")
        else:
            print(f"   ✗ {user.role.capitalize()} permission check failed for {permission.value}")
            return False
    
    # Test 6: Test error handling
    print("\n6. Testing error handling...")
    
    @require_permission(Permission.VIEW_USERS)
    def protected_endpoint(current_user):
        return {"message": "success"}
    
    with app.app_context():
        # Test no authorization header
        with app.test_request_context():
            try:
                result = protected_endpoint()
                print("   ✗ No auth header incorrectly allowed")
                return False
            except Exception:
                print("   ✓ No auth header correctly denied")
        
        # Test invalid token
        with app.test_request_context(headers={"Authorization": "Bearer invalid_token"}):
            try:
                result = protected_endpoint()
                print("   ✗ Invalid token incorrectly allowed")
                return False
            except Exception:
                print("   ✓ Invalid token correctly denied")
    
    print("\n✅ RBAC decorators test completed successfully!")
    
    # Summary
    print(f"\nRBAC System Summary:")
    print(f"   Student permissions: {len(rbac_service.get_user_permissions('student'))}")
    print(f"   Teacher permissions: {len(rbac_service.get_user_permissions('teacher'))}")
    print(f"   Admin permissions: {len(rbac_service.get_user_permissions('admin'))}")
    print(f"   Total permission types: {len(Permission)}")
    
    return True

if __name__ == "__main__":
    success = test_rbac_decorators()
    sys.exit(0 if success else 1)