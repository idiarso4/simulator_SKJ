#!/usr/bin/env python3
"""
Test script for class management functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.user import User
from models.class_model import Class
from services.rbac_service import rbac_service
from database import setup_database, seed_if_empty

def test_class_management():
    """Test class management functionality"""
    print("Testing Class Management System...")
    
    # Setup database
    setup_database()
    seed_if_empty()
    
    # Test 1: Create test users
    print("\n1. Creating test users...")
    
    try:
        teacher1 = User.create_user("teacher1", "teacher1@test.com", "pass", "teacher")
        teacher2 = User.create_user("teacher2", "teacher2@test.com", "pass", "teacher")
        admin = User.create_user("admin", "admin@test.com", "pass", "admin")
        student1 = User.create_user("student1", "student1@test.com", "pass", "student")
        student2 = User.create_user("student2", "student2@test.com", "pass", "student")
        student3 = User.create_user("student3", "student3@test.com", "pass", "student")
        
        print(f"   ✓ Created users: {teacher1.name}, {teacher2.name}, {admin.name}, {student1.name}, {student2.name}, {student3.name}")
    except Exception as e:
        print(f"   ✗ User creation failed: {e}")
        return False
    
    # Test 2: Create classes
    print("\n2. Testing class creation...")
    
    try:
        class1 = Class.create_class(
            name="Network Security 101",
            teacher_id=teacher1.id,
            semester=1,
            description="Introduction to network security concepts",
            max_students=2
        )
        print(f"   ✓ Created class: {class1.name} (ID: {class1.id}, Code: {class1.class_code})")
        
        class2 = Class.create_class(
            name="Advanced Cybersecurity",
            teacher_id=teacher2.id,
            semester=2,
            description="Advanced cybersecurity techniques"
        )
        print(f"   ✓ Created class: {class2.name} (ID: {class2.id}, Code: {class2.class_code})")
        
    except Exception as e:
        print(f"   ✗ Class creation failed: {e}")
        return False
    
    # Test 3: Test class code uniqueness
    print("\n3. Testing class code uniqueness...")
    
    # Class codes should be unique
    if class1.class_code != class2.class_code:
        print(f"   ✓ Class codes are unique: {class1.class_code} != {class2.class_code}")
    else:
        print("   ✗ Class codes are not unique")
        return False
    
    # Test finding by code
    found_class = Class.find_by_code(class1.class_code)
    if found_class and found_class.id == class1.id:
        print("   ✓ Class found by code successfully")
    else:
        print("   ✗ Class lookup by code failed")
        return False
    
    # Test 4: Test class validation
    print("\n4. Testing class validation...")
    
    # Test invalid class creation
    try:
        Class.create_class("", teacher1.id, 1)  # Empty name
        print("   ✗ Empty name validation failed")
        return False
    except ValueError:
        print("   ✓ Empty name correctly rejected")
    
    try:
        Class.create_class("Test Class", 999, 1)  # Invalid teacher
        print("   ✗ Invalid teacher validation failed")
        return False
    except ValueError:
        print("   ✓ Invalid teacher correctly rejected")
    
    try:
        Class.create_class("Test Class", student1.id, 1)  # Student as teacher
        print("   ✗ Student as teacher validation failed")
        return False
    except ValueError:
        print("   ✓ Student as teacher correctly rejected")
    
    # Test 5: Test student enrollment
    print("\n5. Testing student enrollment...")
    
    # Add students to class1
    try:
        success1 = class1.add_student(student1.id)
        success2 = class1.add_student(student2.id)
        
        if success1 and success2:
            print(f"   ✓ Added students to {class1.name}")
            print(f"   ✓ Class now has {class1.get_student_count()} students")
        else:
            print("   ✗ Failed to add students")
            return False
    except Exception as e:
        print(f"   ✗ Student enrollment failed: {e}")
        return False
    
    # Test capacity limit
    try:
        class1.add_student(student3.id)  # Should fail due to max_students=2
        print("   ✗ Capacity limit not enforced")
        return False
    except ValueError:
        print("   ✓ Capacity limit correctly enforced")
    
    # Test 6: Test student retrieval
    print("\n6. Testing student retrieval...")
    
    students = class1.get_students()
    if len(students) == 2:
        print(f"   ✓ Retrieved {len(students)} students from class")
        student_names = [s.name for s in students]
        print(f"   ✓ Students: {', '.join(student_names)}")
    else:
        print(f"   ✗ Expected 2 students, got {len(students)}")
        return False
    
    # Test 7: Test class progress statistics
    print("\n7. Testing class progress statistics...")
    
    progress_stats = class1.get_class_progress()
    expected_keys = ['total_students', 'completed_challenges', 'total_points', 'average_progress']
    
    if all(key in progress_stats for key in expected_keys):
        print("   ✓ Progress statistics generated successfully")
        print(f"   ✓ Total students: {progress_stats['total_students']}")
        print(f"   ✓ Completed challenges: {progress_stats['completed_challenges']}")
        print(f"   ✓ Total points: {progress_stats['total_points']}")
    else:
        print("   ✗ Progress statistics incomplete")
        return False
    
    # Test 8: Test class updates
    print("\n8. Testing class updates...")
    
    original_name = class1.name
    class1.name = "Updated Network Security"
    class1.description = "Updated description"
    class1.save()
    
    # Reload from database
    updated_class = Class.find_by_id(class1.id)
    if (updated_class.name == "Updated Network Security" and 
        updated_class.description == "Updated description"):
        print("   ✓ Class update successful")
    else:
        print("   ✗ Class update failed")
        return False
    
    # Test 9: Test student removal
    print("\n9. Testing student removal...")
    
    success = class1.remove_student(student1.id)
    if success and class1.get_student_count() == 1:
        print("   ✓ Student removed successfully")
        print(f"   ✓ Class now has {class1.get_student_count()} students")
    else:
        print("   ✗ Student removal failed")
        return False
    
    # Test 10: Test teacher class retrieval
    print("\n10. Testing teacher class retrieval...")
    
    teacher1_classes = Class.find_by_teacher(teacher1.id)
    teacher2_classes = Class.find_by_teacher(teacher2.id)
    
    if (len(teacher1_classes) == 1 and teacher1_classes[0].id == class1.id and
        len(teacher2_classes) == 1 and teacher2_classes[0].id == class2.id):
        print("   ✓ Teacher class retrieval successful")
        print(f"   ✓ Teacher1 has {len(teacher1_classes)} classes")
        print(f"   ✓ Teacher2 has {len(teacher2_classes)} classes")
    else:
        print("   ✗ Teacher class retrieval failed")
        return False
    
    # Test 11: Test class serialization
    print("\n11. Testing class serialization...")
    
    class_dict = class1.to_dict(include_students=True, include_progress=True)
    expected_fields = ['id', 'name', 'teacher_id', 'semester', 'created_at', 
                      'is_active', 'description', 'max_students', 'class_code', 
                      'student_count', 'students', 'progress', 'teacher']
    
    if all(field in class_dict for field in expected_fields):
        print("   ✓ Class serialization successful")
        print(f"   ✓ Serialized fields: {len(class_dict)} fields")
        print(f"   ✓ Includes {len(class_dict['students'])} students")
    else:
        print("   ✗ Class serialization incomplete")
        missing = [f for f in expected_fields if f not in class_dict]
        print(f"   ✗ Missing fields: {missing}")
        return False
    
    # Test 12: Test class deactivation
    print("\n12. Testing class deactivation...")
    
    class2.deactivate()
    if not class2.is_active:
        print("   ✓ Class deactivated successfully")
    else:
        print("   ✗ Class deactivation failed")
        return False
    
    # Test active classes filter
    active_classes = Class.get_all_classes(active_only=True)
    all_classes = Class.get_all_classes(active_only=False)
    
    if len(all_classes) > len(active_classes):
        print("   ✓ Active classes filter working")
        print(f"   ✓ Total classes: {len(all_classes)}, Active: {len(active_classes)}")
    else:
        print("   ✗ Active classes filter not working")
        return False
    
    # Test 13: Test class deletion
    print("\n13. Testing class deletion...")
    
    # Create a test class for deletion
    test_class = Class.create_class("Test Delete Class", teacher1.id, 1)
    test_class_id = test_class.id
    
    # Delete the class
    success = test_class.delete()
    if success:
        # Verify it's deleted
        deleted_class = Class.find_by_id(test_class_id)
        if not deleted_class:
            print("   ✓ Class deletion successful")
        else:
            print("   ✗ Class not properly deleted")
            return False
    else:
        print("   ✗ Class deletion failed")
        return False
    
    # Test 14: Test RBAC integration
    print("\n14. Testing RBAC integration...")
    
    # Test teacher permissions
    teacher_can_create = rbac_service.has_permission(teacher1.role, "create_classes")
    teacher_can_manage = rbac_service.has_permission(teacher1.role, "manage_class_members")
    teacher_cannot_delete_users = not rbac_service.has_permission(teacher1.role, "delete_users")
    
    if teacher_can_create and teacher_can_manage and teacher_cannot_delete_users:
        print("   ✓ Teacher permissions correct for class management")
    else:
        print("   ✗ Teacher permissions incorrect")
        return False
    
    # Test student permissions
    student_cannot_create = not rbac_service.has_permission(student1.role, "create_classes")
    student_cannot_manage = not rbac_service.has_permission(student1.role, "manage_class_members")
    
    if student_cannot_create and student_cannot_manage:
        print("   ✓ Student permissions correct (no class management)")
    else:
        print("   ✗ Student permissions incorrect")
        return False
    
    print("\n✅ Class management system test completed successfully!")
    
    # Final summary
    print(f"\n📊 Class Management Summary:")
    print(f"   Total classes created: {len(Class.get_all_classes(active_only=False))}")
    print(f"   Active classes: {len(Class.get_all_classes(active_only=True))}")
    print(f"   Classes with students: {len([c for c in Class.get_all_classes() if c.get_student_count() > 0])}")
    print(f"   Total enrolled students: {sum(c.get_student_count() for c in Class.get_all_classes())}")
    
    return True

if __name__ == "__main__":
    success = test_class_management()
    sys.exit(0 if success else 1)