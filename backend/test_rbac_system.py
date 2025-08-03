#!/usr/bin/env python3
"""
Test script for Role-Based Access Control (RBAC) system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.user import User
from services.rbac_service import rbac_service, Role, Permission
from database import setup_database, seed_if_empty

def test_rbac_system():
    """Test the RBAC system functionality"""
    print("Testing Role-Based Access Control (RBAC) System...")
    
    # Setup database
    setup_database()
    seed_if_empty()
    
    # Test 1: Test role permissions definition
    print("\n1. Testing role permissions definition...")
    
    # Test student permissions
    student_permissions = rbac_service.get_user_permissions("student")
    expected_student_perms = [
        "view_own_progress", "view_challenges", "view_content", 
        "view_achievements", "join_team_challenges"
    ]
    
    if all(perm in student_permissions for perm in expected_student_perms):
        print("   ✓ Student permissions correctly defined")
        print(f"   ✓ Student has {len(student_permissions)} permissions")
    else:
        print("   ✗ Student permissions incorrect")
        return False
    
    # Test teacher permissions
    teacher_permissions = rbac_service.get_user_permissions("teacher")
    expected_teacher_perms = [
        "view_student_progress", "create_classes", "view_users"
    ]
    
    if all(perm in teacher_permissions for perm in expected_teacher_perms):
        print("   ✓ Teacher permissions correctly defined")
        print(f"   ✓ Teacher has {len(teacher_permissions)} permissions")
    else:
        print("   ✗ Teacher permissions incorrect")
        return False
    
    # Test admin permissions
    admin_permissions = rbac_service.get_user_permissions("admin")
    expected_admin_perms = [
        "delete_users", "manage_system", "view_all_progress"
    ]
    
    if all(perm in admin_permissions for perm in expected_admin_perms):
        print("   ✓ Admin permissions correctly defined")
        print(f"   ✓ Admin has {len(admin_permissions)} permissions")
    else:
        print("   ✗ Admin permissions incorrect")
        return False
    
    # Test 2: Test permission checking
    print("\n2. Testing permission checking...")
    
    # Student should have view_own_progress but not view_all_progress
    if (rbac_service.has_permission("student", Permission.VIEW_OWN_PROGRESS) and
        not rbac_service.has_permission("student", Permission.VIEW_ALL_PROGRESS)):
        print("   ✓ Student permission checking works correctly")
    else:
        print("   ✗ Student permission checking failed")
        return False
    
    # Teacher should have view_student_progress but not delete_users
    if (rbac_service.has_permission("teacher", Permission.VIEW_STUDENT_PROGRESS) and
        not rbac_service.has_permission("teacher", Permission.DELETE_USERS)):
        print("   ✓ Teacher permission checking works correctly")
    else:
        print("   ✗ Teacher permission checking failed")
        return False
    
    # Admin should have all permissions
    if (rbac_service.has_permission("admin", Permission.DELETE_USERS) and
        rbac_service.has_permission("admin", Permission.MANAGE_SYSTEM)):
        print("   ✓ Admin permission checking works correctly")
    else:
        print("   ✗ Admin permission checking failed")
        return False
    
    # Test 3: Test user data access control
    print("\n3. Testing user data access control...")
    
    # Create test users
    try:
        student = User.create_user("test_student", "student@test.com", "pass", "student")
        teacher = User.create_user("test_teacher", "teacher@test.com", "pass", "teacher")
        admin = User.create_user("test_admin", "admin@test.com", "pass", "admin")
        
        print(f"   ✓ Created test users: student(ID:{student.id}), teacher(ID:{teacher.id}), admin(ID:{admin.id})")
    except Exception as e:
        print(f"   ✗ Failed to create test users: {e}")
        return False
    
    # Test student accessing own data
    if rbac_service.can_access_user_data(student, student.id):
        print("   ✓ Student can access own data")
    else:
        print("   ✗ Student cannot access own data")
        return False
    
    # Test student accessing other's data
    if not rbac_service.can_access_user_data(student, teacher.id):
        print("   ✓ Student correctly denied access to other's data")
    else:
        print("   ✗ Student incorrectly allowed access to other's data")
        return False
    
    # Test teacher accessing student data
    if rbac_service.can_access_user_data(teacher, student.id):
        print("   ✓ Teacher can access student data")
    else:
        print("   ✗ Teacher cannot access student data")
        return False
    
    # Test admin accessing any data
    if (rbac_service.can_access_user_data(admin, student.id) and
        rbac_service.can_access_user_data(admin, teacher.id)):
        print("   ✓ Admin can access any user data")
    else:
        print("   ✗ Admin cannot access user data")
        return False
    
    # Test 4: Test class management permissions
    print("\n4. Testing class management permissions...")
    
    # Student should not be able to manage classes
    if not rbac_service.can_manage_class(student):
        print("   ✓ Student correctly denied class management")
    else:
        print("   ✗ Student incorrectly allowed class management")
        return False
    
    # Teacher should be able to manage classes
    if rbac_service.can_manage_class(teacher):
        print("   ✓ Teacher can manage classes")
    else:
        print("   ✗ Teacher cannot manage classes")
        return False
    
    # Admin should be able to manage classes
    if rbac_service.can_manage_class(admin):
        print("   ✓ Admin can manage classes")
    else:
        print("   ✗ Admin cannot manage classes")
        return False
    
    # Test 5: Test invalid role/permission handling
    print("\n5. Testing invalid role/permission handling...")
    
    # Test invalid role
    invalid_permissions = rbac_service.get_user_permissions("invalid_role")
    if len(invalid_permissions) == 0:
        print("   ✓ Invalid role returns empty permissions")
    else:
        print("   ✗ Invalid role handling failed")
        return False
    
    # Test invalid permission
    if not rbac_service.has_permission("student", "invalid_permission"):
        print("   ✓ Invalid permission correctly rejected")
    else:
        print("   ✗ Invalid permission handling failed")
        return False
    
    # Test 6: Test permission hierarchy
    print("\n6. Testing permission hierarchy...")
    
    # Admin should have more permissions than teacher
    if len(admin_permissions) > len(teacher_permissions):
        print("   ✓ Admin has more permissions than teacher")
    else:
        print("   ✗ Permission hierarchy incorrect")
        return False
    
    # Teacher should have more permissions than student
    if len(teacher_permissions) > len(student_permissions):
        print("   ✓ Teacher has more permissions than student")
    else:
        print("   ✗ Permission hierarchy incorrect")
        return False
    
    # Test 7: Test specific permission categories
    print("\n7. Testing permission categories...")
    
    # Test user management permissions
    user_mgmt_perms = [Permission.VIEW_USERS, Permission.CREATE_USERS, Permission.EDIT_USERS, Permission.DELETE_USERS]
    admin_has_all_user_mgmt = all(rbac_service.has_permission("admin", perm) for perm in user_mgmt_perms)
    student_has_no_user_mgmt = not any(rbac_service.has_permission("student", perm) for perm in user_mgmt_perms)
    
    if admin_has_all_user_mgmt and student_has_no_user_mgmt:
        print("   ✓ User management permissions correctly distributed")
    else:
        print("   ✗ User management permissions incorrect")
        return False
    
    # Test content management permissions
    content_mgmt_perms = [Permission.CREATE_CONTENT, Permission.EDIT_CONTENT, Permission.DELETE_CONTENT]
    teacher_has_some_content = any(rbac_service.has_permission("teacher", perm) for perm in content_mgmt_perms)
    student_has_no_content_mgmt = not any(rbac_service.has_permission("student", perm) for perm in content_mgmt_perms)
    
    if teacher_has_some_content and student_has_no_content_mgmt:
        print("   ✓ Content management permissions correctly distributed")
    else:
        print("   ✗ Content management permissions incorrect")
        return False
    
    print("\n✅ RBAC system test completed successfully!")
    print(f"\nPermission Summary:")
    print(f"   Student: {len(student_permissions)} permissions")
    print(f"   Teacher: {len(teacher_permissions)} permissions")
    print(f"   Admin: {len(admin_permissions)} permissions")
    
    return True

if __name__ == "__main__":
    success = test_rbac_system()
    sys.exit(0 if success else 1)