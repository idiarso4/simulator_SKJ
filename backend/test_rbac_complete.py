#!/usr/bin/env python3
"""
Complete test for RBAC system functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.user import User
from services.rbac_service import rbac_service, Permission, Role
from services.auth_service import auth_service
from database import setup_database, seed_if_empty

def test_complete_rbac():
    """Complete test of RBAC system"""
    print("Testing Complete RBAC System...")
    
    # Setup database
    setup_database()
    seed_if_empty()
    
    # Test 1: Create users and verify roles
    print("\n1. Testing user creation and role assignment...")
    
    try:
        student = User.create_user("rbac_student", "student@rbac.com", "pass", "student")
        teacher = User.create_user("rbac_teacher", "teacher@rbac.com", "pass", "teacher")
        admin = User.create_user("rbac_admin", "admin@rbac.com", "pass", "admin")
        
        print(f"   ✓ Created users: {student.name}({student.role}), {teacher.name}({teacher.role}), {admin.name}({admin.role})")
    except Exception as e:
        print(f"   ✗ User creation failed: {e}")
        return False
    
    # Test 2: Verify permission assignments
    print("\n2. Testing permission assignments...")
    
    # Student permissions
    student_perms = rbac_service.get_user_permissions(student.role)
    expected_student = ["view_own_progress", "view_challenges", "view_content", "view_achievements", "join_team_challenges"]
    
    if all(perm in student_perms for perm in expected_student):
        print(f"   ✓ Student has correct permissions ({len(student_perms)} total)")
    else:
        print(f"   ✗ Student permissions incorrect. Expected: {expected_student}, Got: {student_perms}")
        return False
    
    # Teacher permissions (should include student permissions plus more)
    teacher_perms = rbac_service.get_user_permissions(teacher.role)
    expected_teacher_extra = ["view_users", "create_classes", "view_student_progress"]
    
    if (all(perm in teacher_perms for perm in expected_student) and 
        all(perm in teacher_perms for perm in expected_teacher_extra)):
        print(f"   ✓ Teacher has correct permissions ({len(teacher_perms)} total)")
    else:
        print(f"   ✗ Teacher permissions incorrect")
        return False
    
    # Admin permissions (should have all permissions)
    admin_perms = rbac_service.get_user_permissions(admin.role)
    expected_admin_extra = ["delete_users", "manage_system", "view_all_progress"]
    
    if all(perm in admin_perms for perm in expected_admin_extra):
        print(f"   ✓ Admin has correct permissions ({len(admin_perms)} total)")
    else:
        print(f"   ✗ Admin permissions incorrect")
        return False
    
    # Test 3: Test specific permission checks
    print("\n3. Testing specific permission checks...")
    
    permission_tests = [
        # (user, permission, expected_result, description)
        (student, Permission.VIEW_OWN_PROGRESS, True, "Student can view own progress"),
        (student, Permission.VIEW_USERS, False, "Student cannot view users"),
        (student, Permission.DELETE_USERS, False, "Student cannot delete users"),
        
        (teacher, Permission.VIEW_OWN_PROGRESS, True, "Teacher can view own progress"),
        (teacher, Permission.VIEW_USERS, True, "Teacher can view users"),
        (teacher, Permission.VIEW_STUDENT_PROGRESS, True, "Teacher can view student progress"),
        (teacher, Permission.DELETE_USERS, False, "Teacher cannot delete users"),
        (teacher, Permission.MANAGE_SYSTEM, False, "Teacher cannot manage system"),
        
        (admin, Permission.VIEW_OWN_PROGRESS, True, "Admin can view own progress"),
        (admin, Permission.VIEW_USERS, True, "Admin can view users"),
        (admin, Permission.DELETE_USERS, True, "Admin can delete users"),
        (admin, Permission.MANAGE_SYSTEM, True, "Admin can manage system"),
        (admin, Permission.VIEW_ALL_PROGRESS, True, "Admin can view all progress"),
    ]
    
    for user, permission, expected, description in permission_tests:
        result = rbac_service.has_permission(user.role, permission)
        if result == expected:
            print(f"   ✓ {description}")
        else:
            print(f"   ✗ {description} - Expected: {expected}, Got: {result}")
            return False
    
    # Test 4: Test user data access control
    print("\n4. Testing user data access control...")
    
    access_tests = [
        # (current_user, target_user_id, expected_result, description)
        (student, student.id, True, "Student can access own data"),
        (student, teacher.id, False, "Student cannot access teacher data"),
        (student, admin.id, False, "Student cannot access admin data"),
        
        (teacher, student.id, True, "Teacher can access student data"),
        (teacher, teacher.id, True, "Teacher can access own data"),
        (teacher, admin.id, False, "Teacher cannot access admin data"),
        
        (admin, student.id, True, "Admin can access student data"),
        (admin, teacher.id, True, "Admin can access teacher data"),
        (admin, admin.id, True, "Admin can access own data"),
    ]
    
    for current_user, target_id, expected, description in access_tests:
        result = rbac_service.can_access_user_data(current_user, target_id)
        if result == expected:
            print(f"   ✓ {description}")
        else:
            print(f"   ✗ {description} - Expected: {expected}, Got: {result}")
            return False
    
    # Test 5: Test class management permissions
    print("\n5. Testing class management permissions...")
    
    class_tests = [
        (student, False, "Student cannot manage classes"),
        (teacher, True, "Teacher can manage classes"),
        (admin, True, "Admin can manage classes"),
    ]
    
    for user, expected, description in class_tests:
        result = rbac_service.can_manage_class(user)
        if result == expected:
            print(f"   ✓ {description}")
        else:
            print(f"   ✗ {description} - Expected: {expected}, Got: {result}")
            return False
    
    # Test 6: Test JWT token integration
    print("\n6. Testing JWT token integration...")
    
    # Generate tokens for each user
    student_token = auth_service.generate_token(student)
    teacher_token = auth_service.generate_token(teacher)
    admin_token = auth_service.generate_token(admin)
    
    # Verify tokens contain correct role information
    student_payload = auth_service.verify_token(student_token)
    teacher_payload = auth_service.verify_token(teacher_token)
    admin_payload = auth_service.verify_token(admin_token)
    
    if (student_payload['role'] == 'student' and 
        teacher_payload['role'] == 'teacher' and 
        admin_payload['role'] == 'admin'):
        print("   ✓ JWT tokens contain correct role information")
    else:
        print("   ✗ JWT token role information incorrect")
        return False
    
    # Test 7: Test permission categories
    print("\n7. Testing permission categories...")
    
    # Count permissions by category
    user_mgmt_perms = [p for p in Permission if 'user' in p.value.lower()]
    class_mgmt_perms = [p for p in Permission if 'class' in p.value.lower()]
    content_mgmt_perms = [p for p in Permission if 'content' in p.value.lower()]
    
    print(f"   ✓ User management permissions: {len(user_mgmt_perms)}")
    print(f"   ✓ Class management permissions: {len(class_mgmt_perms)}")
    print(f"   ✓ Content management permissions: {len(content_mgmt_perms)}")
    
    # Verify admin has all user management permissions
    admin_has_all_user_mgmt = all(rbac_service.has_permission('admin', perm) for perm in user_mgmt_perms)
    if admin_has_all_user_mgmt:
        print("   ✓ Admin has all user management permissions")
    else:
        print("   ✗ Admin missing some user management permissions")
        return False
    
    # Verify student has no user management permissions
    student_has_no_user_mgmt = not any(rbac_service.has_permission('student', perm) for perm in user_mgmt_perms)
    if student_has_no_user_mgmt:
        print("   ✓ Student has no user management permissions")
    else:
        print("   ✗ Student incorrectly has user management permissions")
        return False
    
    # Test 8: Test edge cases and error handling
    print("\n8. Testing edge cases and error handling...")
    
    # Test invalid role
    invalid_perms = rbac_service.get_user_permissions("invalid_role")
    if len(invalid_perms) == 0:
        print("   ✓ Invalid role returns empty permissions")
    else:
        print("   ✗ Invalid role handling failed")
        return False
    
    # Test invalid permission
    invalid_perm_check = rbac_service.has_permission("student", "invalid_permission")
    if not invalid_perm_check:
        print("   ✓ Invalid permission correctly rejected")
    else:
        print("   ✗ Invalid permission handling failed")
        return False
    
    # Test None values
    none_access = rbac_service.can_access_user_data(None, student.id)
    if not none_access:
        print("   ✓ None user correctly denied access")
    else:
        print("   ✗ None user handling failed")
        return False
    
    print("\n✅ Complete RBAC system test passed successfully!")
    
    # Final summary
    print(f"\n📊 RBAC System Summary:")
    print(f"   Total Roles: {len(Role)}")
    print(f"   Total Permissions: {len(Permission)}")
    print(f"   Student Permissions: {len(student_perms)}")
    print(f"   Teacher Permissions: {len(teacher_perms)}")
    print(f"   Admin Permissions: {len(admin_perms)}")
    print(f"   Permission Hierarchy: Student < Teacher < Admin ✓")
    
    return True

if __name__ == "__main__":
    success = test_complete_rbac()
    sys.exit(0 if success else 1)