#!/usr/bin/env python3
"""
Test script for class management API endpoints (without server)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models.user import User
from models.class_model import Class
from services.auth_service import auth_service
from services.rbac_service import rbac_service
from database import setup_database, seed_if_empty

def test_class_api_logic():
    """Test class API logic without running server"""
    print("Testing Class Management API Logic...")
    
    # Setup database and Flask app
    setup_database()
    seed_if_empty()
    
    app = Flask(__name__)
    
    # Create test users
    try:
        teacher = User.create_user("api_teacher", "teacher@api.com", "pass", "teacher")
        student = User.create_user("api_student", "student@api.com", "pass", "student")
        admin = User.create_user("api_admin", "admin@api.com", "pass", "admin")
        print("   ✓ Created test users for API testing")
    except Exception as e:
        print(f"   ✗ Failed to create test users: {e}")
        return False
    
    # Test 1: Test class creation logic
    print("\n1. Testing class creation logic...")
    
    # Valid class creation
    try:
        class_obj = Class.create_class(
            name="API Test Class",
            teacher_id=teacher.id,
            semester=1,
            description="Test class for API",
            max_students=5
        )
        print(f"   ✓ Class created: {class_obj.name} (Code: {class_obj.class_code})")
    except Exception as e:
        print(f"   ✗ Class creation failed: {e}")
        return False
    
    # Test 2: Test permission checks
    print("\n2. Testing permission checks...")
    
    # Teacher should be able to create classes
    teacher_can_create = rbac_service.has_permission(teacher.role, "create_classes")
    if teacher_can_create:
        print("   ✓ Teacher has create_classes permission")
    else:
        print("   ✗ Teacher missing create_classes permission")
        return False
    
    # Student should not be able to create classes
    student_cannot_create = not rbac_service.has_permission(student.role, "create_classes")
    if student_cannot_create:
        print("   ✓ Student correctly denied create_classes permission")
    else:
        print("   ✗ Student incorrectly has create_classes permission")
        return False
    
    # Test 3: Test student enrollment logic
    print("\n3. Testing student enrollment logic...")
    
    # Teacher should be able to manage class members
    teacher_can_manage = rbac_service.has_permission(teacher.role, "manage_class_members")
    if teacher_can_manage:
        print("   ✓ Teacher has manage_class_members permission")
    else:
        print("   ✗ Teacher missing manage_class_members permission")
        return False
    
    # Add student to class
    try:
        success = class_obj.add_student(student.id)
        if success:
            print("   ✓ Student added to class successfully")
            print(f"   ✓ Class now has {class_obj.get_student_count()} students")
        else:
            print("   ✗ Failed to add student to class")
            return False
    except Exception as e:
        print(f"   ✗ Student enrollment error: {e}")
        return False
    
    # Test 4: Test class code join logic
    print("\n4. Testing class code join logic...")
    
    # Create another student for testing
    try:
        student2 = User.create_user("api_student2", "student2@api.com", "pass", "student")
        
        # Student should be able to join by class code
        found_class = Class.find_by_code(class_obj.class_code)
        if found_class and found_class.id == class_obj.id:
            print("   ✓ Class found by code for joining")
            
            # Add student2 to class
            success = found_class.add_student(student2.id)
            if success:
                print("   ✓ Student2 joined class by code successfully")
            else:
                print("   ✗ Student2 failed to join class")
                return False
        else:
            print("   ✗ Class not found by code")
            return False
    except Exception as e:
        print(f"   ✗ Class join error: {e}")
        return False
    
    # Test 5: Test access control logic
    print("\n5. Testing access control logic...")
    
    # Teacher should be able to view their own classes
    teacher_classes = Class.find_by_teacher(teacher.id)
    if len(teacher_classes) == 1 and teacher_classes[0].id == class_obj.id:
        print("   ✓ Teacher can view their own classes")
    else:
        print("   ✗ Teacher class access failed")
        return False
    
    # Create another teacher and class
    try:
        teacher2 = User.create_user("api_teacher2", "teacher2@api.com", "pass", "teacher")
        class2 = Class.create_class("Teacher2 Class", teacher2.id, 2)
        
        # Teacher1 should not see Teacher2's classes
        teacher1_classes = Class.find_by_teacher(teacher.id)
        teacher2_classes = Class.find_by_teacher(teacher2.id)
        
        if (len(teacher1_classes) == 1 and teacher1_classes[0].id == class_obj.id and
            len(teacher2_classes) == 1 and teacher2_classes[0].id == class2.id):
            print("   ✓ Teachers can only see their own classes")
        else:
            print("   ✗ Teacher class isolation failed")
            return False
    except Exception as e:
        print(f"   ✗ Teacher isolation test error: {e}")
        return False
    
    # Test 6: Test class capacity logic
    print("\n6. Testing class capacity logic...")
    
    # Create a class with capacity 1
    try:
        small_class = Class.create_class("Small Class", teacher.id, 1, max_students=1)
        
        # Add first student (should succeed)
        student3 = User.create_user("api_student3", "student3@api.com", "pass", "student")
        success1 = small_class.add_student(student3.id)
        
        # Try to add second student (should fail)
        student4 = User.create_user("api_student4", "student4@api.com", "pass", "student")
        try:
            small_class.add_student(student4.id)
            print("   ✗ Class capacity limit not enforced")
            return False
        except ValueError:
            print("   ✓ Class capacity limit correctly enforced")
    except Exception as e:
        print(f"   ✗ Capacity test error: {e}")
        return False
    
    # Test 7: Test class update logic
    print("\n7. Testing class update logic...")
    
    # Update class information
    original_name = class_obj.name
    class_obj.name = "Updated API Test Class"
    class_obj.description = "Updated description"
    class_obj.save()
    
    # Verify update
    updated_class = Class.find_by_id(class_obj.id)
    if (updated_class.name == "Updated API Test Class" and 
        updated_class.description == "Updated description"):
        print("   ✓ Class update logic working correctly")
    else:
        print("   ✗ Class update logic failed")
        return False
    
    # Test 8: Test class statistics logic
    print("\n8. Testing class statistics logic...")
    
    stats = class_obj.get_class_progress()
    expected_stats = ['total_students', 'completed_challenges', 'total_points', 'average_progress']
    
    if all(key in stats for key in expected_stats):
        print("   ✓ Class statistics generated correctly")
        print(f"   ✓ Total students: {stats['total_students']}")
        print(f"   ✓ Completed challenges: {stats['completed_challenges']}")
    else:
        print("   ✗ Class statistics incomplete")
        return False
    
    # Test 9: Test class serialization for API
    print("\n9. Testing class serialization for API...")
    
    class_dict = class_obj.to_dict(include_students=True, include_progress=True)
    api_fields = ['id', 'name', 'teacher_id', 'semester', 'class_code', 'students', 'progress']
    
    if all(field in class_dict for field in api_fields):
        print("   ✓ Class serialization includes all API fields")
        print(f"   ✓ Students included: {len(class_dict['students'])}")
        print(f"   ✓ Progress included: {bool(class_dict['progress'])}")
    else:
        print("   ✗ Class serialization missing API fields")
        return False
    
    # Test 10: Test admin permissions
    print("\n10. Testing admin permissions...")
    
    # Admin should have all class management permissions
    admin_permissions = [
        "view_classes", "create_classes", "edit_classes", 
        "delete_classes", "manage_class_members"
    ]
    
    admin_has_all = all(rbac_service.has_permission(admin.role, perm) for perm in admin_permissions)
    if admin_has_all:
        print("   ✓ Admin has all class management permissions")
    else:
        print("   ✗ Admin missing some class management permissions")
        return False
    
    print("\n✅ Class management API logic test completed successfully!")
    
    # Final API summary
    print(f"\n📊 API Logic Summary:")
    print(f"   Classes created: {len(Class.get_all_classes(active_only=False))}")
    print(f"   Students enrolled: {sum(c.get_student_count() for c in Class.get_all_classes())}")
    print(f"   Teachers with classes: {len(set(c.teacher_id for c in Class.get_all_classes()))}")
    print(f"   Permission checks: All passed ✓")
    
    return True

if __name__ == "__main__":
    success = test_class_api_logic()
    sys.exit(0 if success else 1)