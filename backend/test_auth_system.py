#!/usr/bin/env python3
"""
Test script for enhanced authentication system
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:5001"

def test_auth_system():
    """Test the enhanced authentication system"""
    print("Testing Enhanced Authentication System...")
    
    # Test 1: Register a new user
    print("\n1. Testing user registration...")
    register_data = {
        "name": "test_student",
        "email": "test@example.com",
        "password": "testpass123",
        "role": "student"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        if response.status_code == 201:
            print("   ✓ User registration successful")
            register_result = response.json()
            student_token = register_result.get("token")
            print(f"   ✓ Token received: {student_token[:20]}...")
        else:
            print(f"   ✗ Registration failed: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ⚠ Server not running. Please start the Flask app first.")
        return False
    
    # Test 2: Login with password
    print("\n2. Testing login with password...")
    login_data = {
        "name": "test_student",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        print("   ✓ Login with password successful")
        login_result = response.json()
        token = login_result.get("token")
    else:
        print(f"   ✗ Login failed: {response.text}")
        return False
    
    # Test 3: Get current user info
    print("\n3. Testing get current user...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    if response.status_code == 200:
        print("   ✓ Get current user successful")
        user_info = response.json()
        print(f"   ✓ User: {user_info['user']['name']} ({user_info['user']['role']})")
    else:
        print(f"   ✗ Get current user failed: {response.text}")
        return False
    
    # Test 4: Update profile
    print("\n4. Testing profile update...")
    profile_data = {
        "email": "updated@example.com",
        "preferences": {"theme": "dark", "language": "id"}
    }
    
    response = requests.put(f"{BASE_URL}/api/auth/profile", json=profile_data, headers=headers)
    if response.status_code == 200:
        print("   ✓ Profile update successful")
        updated_user = response.json()
        print(f"   ✓ Updated email: {updated_user['user']['email']}")
        print(f"   ✓ Preferences: {updated_user['user']['preferences']}")
    else:
        print(f"   ✗ Profile update failed: {response.text}")
        return False
    
    # Test 5: Change password
    print("\n5. Testing password change...")
    password_data = {
        "current_password": "testpass123",
        "new_password": "newpass456"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/change-password", json=password_data, headers=headers)
    if response.status_code == 200:
        print("   ✓ Password change successful")
    else:
        print(f"   ✗ Password change failed: {response.text}")
        return False
    
    # Test 6: Login with new password
    print("\n6. Testing login with new password...")
    new_login_data = {
        "email": "updated@example.com",
        "password": "newpass456"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=new_login_data)
    if response.status_code == 200:
        print("   ✓ Login with new password successful")
    else:
        print(f"   ✗ Login with new password failed: {response.text}")
        return False
    
    # Test 7: Register teacher
    print("\n7. Testing teacher registration...")
    teacher_data = {
        "name": "test_teacher",
        "email": "teacher@example.com",
        "password": "teacherpass",
        "role": "teacher"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=teacher_data)
    if response.status_code == 201:
        print("   ✓ Teacher registration successful")
        teacher_result = response.json()
        teacher_token = teacher_result.get("token")
    else:
        print(f"   ✗ Teacher registration failed: {response.text}")
        return False
    
    # Test 8: Test role-based access (teacher accessing users list)
    print("\n8. Testing role-based access...")
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
    response = requests.get(f"{BASE_URL}/api/users", headers=teacher_headers)
    if response.status_code == 200:
        print("   ✓ Teacher can access users list")
        users = response.json()
        print(f"   ✓ Found {len(users)} users")
    else:
        print(f"   ✗ Teacher access failed: {response.text}")
        return False
    
    # Test 9: Test role-based access denial (student accessing users list)
    print("\n9. Testing role-based access denial...")
    student_headers = {"Authorization": f"Bearer {student_token}"}
    response = requests.get(f"{BASE_URL}/api/users", headers=student_headers)
    if response.status_code == 403:
        print("   ✓ Student correctly denied access to users list")
    else:
        print(f"   ✗ Student access control failed: {response.status_code}")
        return False
    
    # Test 10: Backward compatibility (login without password)
    print("\n10. Testing backward compatibility...")
    old_login_data = {
        "name": "legacy_user"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=old_login_data)
    if response.status_code == 200:
        print("   ✓ Backward compatibility login successful")
        legacy_result = response.json()
        print(f"   ✓ Legacy user created: {legacy_result['user']['name']}")
    else:
        print(f"   ✗ Backward compatibility failed: {response.text}")
        return False
    
    print("\n✅ Enhanced authentication system test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_auth_system()
    sys.exit(0 if success else 1)