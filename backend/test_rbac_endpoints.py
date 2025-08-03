#!/usr/bin/env python3
"""
Test script for RBAC-protected API endpoints
"""

import requests
import json
import sys
import time
import subprocess
import threading

BASE_URL = "http://127.0.0.1:5001"

def start_server():
    """Start the Flask server in background"""
    try:
        subprocess.Popen(
            ["python", "app.py"],
            cwd=".",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(3)  # Give server time to start
        return True
    except Exception as e:
        print(f"Failed to start server: {e}")
        return False

def test_rbac_endpoints():
    """Test RBAC-protected endpoints"""
    print("Testing RBAC-Protected API Endpoints...")
    
    # Clean database and start server
    import os
    if os.path.exists('skj.db'):
        os.remove('skj.db')
    
    print("Starting server...")
    if not start_server():
        print("Failed to start server")
        return False
    
    try:
        # Test server is running
        response = requests.get(f"{BASE_URL}/api/modules", timeout=5)
        print("   ✓ Server is running")
    except requests.exceptions.RequestException:
        print("   ✗ Server not accessible")
        return False
    
    # Test 1: Create users with different roles
    print("\n1. Creating test users...")
    
    users = {}
    tokens = {}
    
    # Create student
    student_data = {
        "name": "test_student",
        "email": "student@test.com",
        "password": "password123",
        "role": "student"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=student_data)
    if response.status_code == 201:
        result = response.json()
        users['student'] = result['user']
        tokens['student'] = result['token']
        print("   ✓ Student user created")
    else:
        print(f"   ✗ Student creation failed: {response.text}")
        return False
    
    # Create teacher
    teacher_data = {
        "name": "test_teacher",
        "email": "teacher@test.com",
        "password": "password123",
        "role": "teacher"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=teacher_data)
    if response.status_code == 201:
        result = response.json()
        users['teacher'] = result['user']
        tokens['teacher'] = result['token']
        print("   ✓ Teacher user created")
    else:
        print(f"   ✗ Teacher creation failed: {response.text}")
        return False
    
    # Create admin
    admin_data = {
        "name": "test_admin",
        "email": "admin@test.com",
        "password": "password123",
        "role": "admin"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=admin_data)
    if response.status_code == 201:
        result = response.json()
        users['admin'] = result['user']
        tokens['admin'] = result['token']
        print("   ✓ Admin user created")
    else:
        print(f"   ✗ Admin creation failed: {response.text}")
        return False
    
    # Test 2: Test permissions endpoint
    print("\n2. Testing permissions endpoint...")
    
    for role in ['student', 'teacher', 'admin']:
        headers = {"Authorization": f"Bearer {tokens[role]}"}
        response = requests.get(f"{BASE_URL}/api/auth/permissions", headers=headers)
        
        if response.status_code == 200:
            perms = response.json()
            print(f"   ✓ {role.capitalize()} permissions: {len(perms['permissions'])} permissions")
        else:
            print(f"   ✗ {role.capitalize()} permissions failed: {response.text}")
            return False
    
    # Test 3: Test dashboard access
    print("\n3. Testing role-specific dashboards...")
    
    # Student dashboard
    headers = {"Authorization": f"Bearer {tokens['student']}"}
    response = requests.get(f"{BASE_URL}/api/dashboard/student", headers=headers)
    if response.status_code == 200:
        print("   ✓ Student can access student dashboard")
    else:
        print(f"   ✗ Student dashboard access failed: {response.text}")
        return False
    
    # Teacher dashboard (student should be denied)
    response = requests.get(f"{BASE_URL}/api/dashboard/teacher", headers=headers)
    if response.status_code == 403:
        print("   ✓ Student correctly denied teacher dashboard")
    else:
        print(f"   ✗ Student access control failed: {response.status_code}")
        return False
    
    # Teacher dashboard (teacher should access)
    headers = {"Authorization": f"Bearer {tokens['teacher']}"}
    response = requests.get(f"{BASE_URL}/api/dashboard/teacher", headers=headers)
    if response.status_code == 200:
        print("   ✓ Teacher can access teacher dashboard")
    else:
        print(f"   ✗ Teacher dashboard access failed: {response.text}")
        return False
    
    # Admin dashboard (admin should access)
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    response = requests.get(f"{BASE_URL}/api/dashboard/admin", headers=headers)
    if response.status_code == 200:
        print("   ✓ Admin can access admin dashboard")
    else:
        print(f"   ✗ Admin dashboard access failed: {response.text}")
        return False
    
    # Test 4: Test user management endpoints
    print("\n4. Testing user management endpoints...")
    
    # Student trying to list users (should be denied)
    headers = {"Authorization": f"Bearer {tokens['student']}"}
    response = requests.get(f"{BASE_URL}/api/users", headers=headers)
    if response.status_code == 403:
        print("   ✓ Student correctly denied users list")
    else:
        print(f"   ✗ Student access control failed: {response.status_code}")
        return False
    
    # Teacher listing users (should be allowed)
    headers = {"Authorization": f"Bearer {tokens['teacher']}"}
    response = requests.get(f"{BASE_URL}/api/users", headers=headers)
    if response.status_code == 200:
        users_list = response.json()
        print(f"   ✓ Teacher can list users ({len(users_list)} users)")
    else:
        print(f"   ✗ Teacher users list failed: {response.text}")
        return False
    
    # Admin listing users (should be allowed)
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    response = requests.get(f"{BASE_URL}/api/users", headers=headers)
    if response.status_code == 200:
        print("   ✓ Admin can list users")
    else:
        print(f"   ✗ Admin users list failed: {response.text}")
        return False
    
    # Test 5: Test own resource access
    print("\n5. Testing own resource access...")
    
    student_id = users['student']['id']
    teacher_id = users['teacher']['id']
    
    # Student accessing own profile
    headers = {"Authorization": f"Bearer {tokens['student']}"}
    response = requests.get(f"{BASE_URL}/api/users/{student_id}", headers=headers)
    if response.status_code == 200:
        print("   ✓ Student can access own profile")
    else:
        print(f"   ✗ Student own profile access failed: {response.text}")
        return False
    
    # Student accessing teacher's profile (should be denied)
    response = requests.get(f"{BASE_URL}/api/users/{teacher_id}", headers=headers)
    if response.status_code == 403:
        print("   ✓ Student correctly denied access to teacher profile")
    else:
        print(f"   ✗ Student access control failed: {response.status_code}")
        return False
    
    # Teacher accessing student profile (should be allowed)
    headers = {"Authorization": f"Bearer {tokens['teacher']}"}
    response = requests.get(f"{BASE_URL}/api/users/{student_id}", headers=headers)
    if response.status_code == 200:
        print("   ✓ Teacher can access student profile")
    else:
        print(f"   ✗ Teacher student profile access failed: {response.text}")
        return False
    
    # Test 6: Test user modification permissions
    print("\n6. Testing user modification permissions...")
    
    # Student trying to delete user (should be denied)
    headers = {"Authorization": f"Bearer {tokens['student']}"}
    response = requests.delete(f"{BASE_URL}/api/users/{teacher_id}", headers=headers)
    if response.status_code == 403:
        print("   ✓ Student correctly denied user deletion")
    else:
        print(f"   ✗ Student deletion access control failed: {response.status_code}")
        return False
    
    # Teacher trying to delete user (should be denied)
    headers = {"Authorization": f"Bearer {tokens['teacher']}"}
    response = requests.delete(f"{BASE_URL}/api/users/{student_id}", headers=headers)
    if response.status_code == 403:
        print("   ✓ Teacher correctly denied user deletion")
    else:
        print(f"   ✗ Teacher deletion access control failed: {response.status_code}")
        return False
    
    # Admin can delete user (but we won't actually delete)
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    # Just test that admin has access (we'll get 200 or different error, not 403)
    response = requests.delete(f"{BASE_URL}/api/users/999", headers=headers)  # Non-existent user
    if response.status_code != 403:
        print("   ✓ Admin has user deletion permissions")
    else:
        print(f"   ✗ Admin deletion permissions failed: {response.status_code}")
        return False
    
    # Test 7: Test unauthenticated access
    print("\n7. Testing unauthenticated access...")
    
    # No token provided
    response = requests.get(f"{BASE_URL}/api/users")
    if response.status_code == 401:
        print("   ✓ Unauthenticated request correctly denied")
    else:
        print(f"   ✗ Unauthenticated access control failed: {response.status_code}")
        return False
    
    # Invalid token
    headers = {"Authorization": "Bearer invalid_token"}
    response = requests.get(f"{BASE_URL}/api/users", headers=headers)
    if response.status_code == 401:
        print("   ✓ Invalid token correctly denied")
    else:
        print(f"   ✗ Invalid token access control failed: {response.status_code}")
        return False
    
    print("\n✅ RBAC endpoints test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_rbac_endpoints()
    sys.exit(0 if success else 1)