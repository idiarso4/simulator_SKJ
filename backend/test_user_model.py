#!/usr/bin/env python3
"""
Test script for User model and authentication service (without server)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.user import User
from services.auth_service import auth_service
from database import setup_database, seed_if_empty

def test_user_model():
    """Test the User model functionality"""
    print("Testing Enhanced User Model and Authentication...")
    
    # Setup database
    setup_database()
    seed_if_empty()
    
    # Test 1: Create user with password
    print("\n1. Testing user creation with password...")
    try:
        user = User.create_user(
            name="test_user_1",
            email="test1@example.com",
            password="testpass123",
            role="student"
        )
        print(f"   ✓ User created: {user.name} (ID: {user.id})")
        print(f"   ✓ Email: {user.email}")
        print(f"   ✓ Role: {user.role}")
        print(f"   ✓ Password hash: {user.password_hash[:20]}...")
    except Exception as e:
        print(f"   ✗ User creation failed: {e}")
        return False
    
    # Test 2: Password verification
    print("\n2. Testing password verification...")
    if user.check_password("testpass123"):
        print("   ✓ Correct password verified")
    else:
        print("   ✗ Password verification failed")
        return False
    
    if not user.check_password("wrongpass"):
        print("   ✓ Wrong password correctly rejected")
    else:
        print("   ✗ Wrong password incorrectly accepted")
        return False
    
    # Test 3: Find user by name and email
    print("\n3. Testing user lookup...")
    found_by_name = User.find_by_name("test_user_1")
    if found_by_name and found_by_name.id == user.id:
        print("   ✓ User found by name")
    else:
        print("   ✗ User lookup by name failed")
        return False
    
    found_by_email = User.find_by_email("test1@example.com")
    if found_by_email and found_by_email.id == user.id:
        print("   ✓ User found by email")
    else:
        print("   ✗ User lookup by email failed")
        return False
    
    # Test 4: JWT token generation and verification
    print("\n4. Testing JWT token functionality...")
    token = auth_service.generate_token(user)
    print(f"   ✓ Token generated: {token[:30]}...")
    
    payload = auth_service.verify_token(token)
    if payload and payload.get('user_id') == user.id:
        print("   ✓ Token verified successfully")
        print(f"   ✓ Payload: user_id={payload.get('user_id')}, role={payload.get('role')}")
    else:
        print("   ✗ Token verification failed")
        return False
    
    # Test 5: User authentication
    print("\n5. Testing user authentication...")
    auth_user = auth_service.authenticate_user("test_user_1", "testpass123")
    if auth_user and auth_user.id == user.id:
        print("   ✓ Authentication by name successful")
    else:
        print("   ✗ Authentication by name failed")
        return False
    
    auth_user_email = auth_service.authenticate_user("test1@example.com", "testpass123")
    if auth_user_email and auth_user_email.id == user.id:
        print("   ✓ Authentication by email successful")
    else:
        print("   ✗ Authentication by email failed")
        return False
    
    # Test 6: Profile update
    print("\n6. Testing profile update...")
    user.email = "updated@example.com"
    user.preferences = {"theme": "dark", "language": "id"}
    user.profile_picture = "avatar.jpg"
    user.save()
    
    updated_user = User.find_by_id(user.id)
    if (updated_user.email == "updated@example.com" and 
        updated_user.preferences.get("theme") == "dark"):
        print("   ✓ Profile update successful")
        print(f"   ✓ Updated email: {updated_user.email}")
        print(f"   ✓ Preferences: {updated_user.preferences}")
    else:
        print("   ✗ Profile update failed")
        return False
    
    # Test 7: Create teacher user
    print("\n7. Testing teacher user creation...")
    try:
        teacher = User.create_user(
            name="test_teacher",
            email="teacher@example.com",
            password="teacherpass",
            role="teacher"
        )
        print(f"   ✓ Teacher created: {teacher.name} (Role: {teacher.role})")
    except Exception as e:
        print(f"   ✗ Teacher creation failed: {e}")
        return False
    
    # Test 8: Get all users
    print("\n8. Testing get all users...")
    all_users = User.get_all_users()
    print(f"   ✓ Found {len(all_users)} users")
    for u in all_users:
        print(f"   - {u.name} ({u.role})")
    
    # Test 9: User to dict conversion
    print("\n9. Testing user serialization...")
    user_dict = user.to_dict()
    expected_fields = ['id', 'name', 'email', 'role', 'preferences', 'created_at']
    if all(field in user_dict for field in expected_fields):
        print("   ✓ User serialization successful")
        print(f"   ✓ Fields: {list(user_dict.keys())}")
    else:
        print("   ✗ User serialization failed")
        return False
    
    # Test 10: Duplicate user validation
    print("\n10. Testing duplicate user validation...")
    try:
        User.create_user(name="test_user_1", email="duplicate@example.com")
        print("   ✗ Duplicate name validation failed")
        return False
    except ValueError:
        print("   ✓ Duplicate name correctly rejected")
    
    try:
        User.create_user(name="unique_name", email="updated@example.com")
        print("   ✗ Duplicate email validation failed")
        return False
    except ValueError:
        print("   ✓ Duplicate email correctly rejected")
    
    print("\n✅ Enhanced User model and authentication test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_user_model()
    sys.exit(0 if success else 1)