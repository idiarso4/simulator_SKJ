from flask import Flask, request, jsonify
from flask_cors import CORS
from database import get_conn, setup_database, seed_if_empty, row_to_dict
from models.user import User
from models.class_model import Class
from services.auth_service import auth_service, token_required, role_required, optional_auth
from services.rbac_service import rbac_service, require_permission, require_any_permission, require_role, require_own_resource_or_permission, Permission
from datetime import datetime, timedelta
import os
import base64
import hmac
import hashlib
import json

app = Flask(__name__)
CORS(app)

# Simple secret for signing tokens (for MVP; replace with strong secret in prod)
SECRET = os.environ.get("SKJ_SECRET", "dev-secret-change-me")

def setup():
    """Setup database with migrations and seed data"""
    setup_database()
    seed_if_empty()


# --- Minimal JWT-like token for MVP (username only, HMAC-SHA256 signed) ---

def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def sign_token(payload: dict, exp_minutes: int = 120) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = dict(payload)
    payload["exp"] = (datetime.utcnow() + timedelta(minutes=exp_minutes)).isoformat()
    header_b64 = b64url(json.dumps(header, separators=(",", ":")).encode())
    payload_b64 = b64url(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{header_b64}.{payload_b64}".encode()
    sig = hmac.new(SECRET.encode(), signing_input, hashlib.sha256).digest()
    token = f"{header_b64}.{payload_b64}.{b64url(sig)}"
    return token


def verify_token(token: str):
    try:
        header_b64, payload_b64, sig_b64 = token.split(".")
        signing_input = f"{header_b64}.{payload_b64}".encode()
        expected = hmac.new(SECRET.encode(), signing_input, hashlib.sha256).digest()
        if not hmac.compare_digest(expected, base64.urlsafe_b64decode(sig_b64 + "==")):
            return None
        payload = json.loads(base64.urlsafe_b64decode(payload_b64 + "==").decode())
        if "exp" in payload and datetime.fromisoformat(payload["exp"]) < datetime.utcnow():
            return None
        return payload
    except Exception:
        return None


def get_auth_user():
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1].strip()
        payload = verify_token(token)
        if payload and "user_id" in payload:
            return payload
    return None


# Enhanced Authentication Endpoints
@app.post("/api/auth/register")
def auth_register():
    """Register a new user"""
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip() or None
    password = data.get("password")
    role = data.get("role", "student")
    
    if not name:
        return jsonify({"error": "Name is required"}), 400
    
    # Validate role
    if role not in ["student", "teacher", "admin"]:
        return jsonify({"error": "Invalid role"}), 400
    
    try:
        user = auth_service.register_user(name, email, password, role)
        token = auth_service.generate_token(user)
        
        return jsonify({
            "message": "User registered successfully",
            "token": token,
            "user": user.to_dict()
        }), 201
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Registration failed"}), 500

@app.post("/api/auth/login")
def auth_login():
    """Login with name/email and password, or just name for backward compatibility"""
    data = request.get_json(force=True)
    identifier = (data.get("name") or data.get("email") or "").strip()
    password = data.get("password")
    
    if not identifier:
        return jsonify({"error": "Name or email is required"}), 400
    
    # Enhanced authentication with password
    if password:
        user = auth_service.authenticate_user(identifier, password)
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401
    else:
        # Backward compatibility: login with just name (create if doesn't exist)
        user = User.find_by_name(identifier)
        if not user:
            try:
                user = User.create_user(name=identifier, role="student")
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
    
    # Generate token and return
    token = auth_service.generate_token(user)
    user.update_last_active()
    
    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": user.to_dict()
    })

@app.get("/api/auth/me")
@token_required
def get_current_user(current_user):
    """Get current user information"""
    return jsonify({
        "user": current_user.to_dict()
    })

@app.post("/api/auth/logout")
@token_required
def auth_logout(current_user):
    """Logout (client should discard token)"""
    return jsonify({"message": "Logged out successfully"})

@app.put("/api/auth/profile")
@token_required
def update_profile(current_user):
    """Update user profile"""
    data = request.get_json(force=True)
    
    # Update allowed fields
    if "email" in data:
        email = data["email"].strip() if data["email"] else None
        if email and email != current_user.email:
            # Check if email is already taken
            existing_user = User.find_by_email(email)
            if existing_user and existing_user.id != current_user.id:
                return jsonify({"error": "Email already in use"}), 400
            current_user.email = email
    
    if "profile_picture" in data:
        current_user.profile_picture = data["profile_picture"]
    
    if "preferences" in data and isinstance(data["preferences"], dict):
        current_user.preferences.update(data["preferences"])
    
    try:
        current_user.save()
        return jsonify({
            "message": "Profile updated successfully",
            "user": current_user.to_dict()
        })
    except Exception as e:
        return jsonify({"error": "Failed to update profile"}), 500

@app.post("/api/auth/change-password")
@token_required
def change_password(current_user):
    """Change user password"""
    data = request.get_json(force=True)
    current_password = data.get("current_password")
    new_password = data.get("new_password")
    
    if not new_password:
        return jsonify({"error": "New password is required"}), 400
    
    # If user has a password, verify current password
    if current_user.password_hash:
        if not current_password:
            return jsonify({"error": "Current password is required"}), 400
        if not current_user.check_password(current_password):
            return jsonify({"error": "Current password is incorrect"}), 401
    
    # Set new password
    current_user.password_hash = User.hash_password(new_password)
    current_user.save()
    
    return jsonify({"message": "Password changed successfully"})


# Role-specific Dashboard Endpoints
@app.get("/api/dashboard/student")
@require_permission(Permission.VIEW_OWN_PROGRESS)
def student_dashboard(current_user):
    """Student dashboard with personal progress and available challenges"""
    with get_conn() as conn:
        cursor = conn.cursor()
        
        # Get user's progress
        cursor.execute("""
            SELECT p.*, c.title, c.points as max_points, m.title as module_title
            FROM progress p
            JOIN challenges c ON p.challenge_id = c.id
            JOIN modules m ON c.module_id = m.id
            WHERE p.user_id = ?
            ORDER BY p.updated_at DESC
        """, (current_user.id,))
        progress = [row_to_dict(row) for row in cursor.fetchall()]
        
        # Get available challenges
        cursor.execute("""
            SELECT c.*, m.title as module_title
            FROM challenges c
            JOIN modules m ON c.module_id = m.id
            ORDER BY m.semester, c.id
        """)
        challenges = [row_to_dict(row) for row in cursor.fetchall()]
        
        # Get user's achievements
        cursor.execute("""
            SELECT a.*, ua.earned_at, ua.progress
            FROM achievements a
            JOIN user_achievements ua ON a.id = ua.achievement_id
            WHERE ua.user_id = ?
            ORDER BY ua.earned_at DESC
        """, (current_user.id,))
        achievements = [row_to_dict(row) for row in cursor.fetchall()]
        
        # Calculate statistics
        total_points = sum(p['points'] for p in progress)
        completed_challenges = len([p for p in progress if p['status'] == 'completed'])
        
        return jsonify({
            "user": current_user.to_dict(),
            "statistics": {
                "total_points": total_points,
                "completed_challenges": completed_challenges,
                "total_achievements": len(achievements)
            },
            "recent_progress": progress[:5],
            "available_challenges": challenges,
            "achievements": achievements,
            "permissions": rbac_service.get_user_permissions(current_user.role)
        })

@app.get("/api/dashboard/teacher")
@require_permission(Permission.VIEW_STUDENT_PROGRESS)
def teacher_dashboard(current_user):
    """Teacher dashboard with class management and student progress"""
    with get_conn() as conn:
        cursor = conn.cursor()
        
        # Get teacher's classes
        cursor.execute("""
            SELECT c.*, COUNT(u.id) as student_count
            FROM classes c
            LEFT JOIN users u ON c.id = u.class_id
            WHERE c.teacher_id = ?
            GROUP BY c.id
            ORDER BY c.created_at DESC
        """, (current_user.id,))
        classes = [row_to_dict(row) for row in cursor.fetchall()]
        
        # Get students in teacher's classes
        cursor.execute("""
            SELECT u.*, c.name as class_name
            FROM users u
            JOIN classes c ON u.class_id = c.id
            WHERE c.teacher_id = ? AND u.role = 'student'
            ORDER BY c.name, u.name
        """, (current_user.id,))
        students = [row_to_dict(row) for row in cursor.fetchall()]
        
        # Get recent student activity
        cursor.execute("""
            SELECT p.*, u.name as student_name, ch.title as challenge_title, c.name as class_name
            FROM progress p
            JOIN users u ON p.user_id = u.id
            JOIN challenges ch ON p.challenge_id = ch.id
            JOIN classes c ON u.class_id = c.id
            WHERE c.teacher_id = ?
            ORDER BY p.updated_at DESC
            LIMIT 10
        """, (current_user.id,))
        recent_activity = [row_to_dict(row) for row in cursor.fetchall()]
        
        # Calculate statistics
        total_students = len(students)
        total_classes = len(classes)
        
        return jsonify({
            "user": current_user.to_dict(),
            "statistics": {
                "total_classes": total_classes,
                "total_students": total_students,
                "active_challenges": 0  # TODO: implement active challenges count
            },
            "classes": classes,
            "students": students[:10],  # Limit for performance
            "recent_activity": recent_activity,
            "permissions": rbac_service.get_user_permissions(current_user.role)
        })

@app.get("/api/dashboard/admin")
@require_permission(Permission.VIEW_ALL_PROGRESS)
def admin_dashboard(current_user):
    """Admin dashboard with system-wide statistics and management"""
    with get_conn() as conn:
        cursor = conn.cursor()
        
        # Get system statistics
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'student'")
        student_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'teacher'")
        teacher_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM classes")
        class_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM challenges")
        challenge_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM progress WHERE status = 'completed'")
        completed_challenges = cursor.fetchone()['count']
        
        # Get recent users
        cursor.execute("""
            SELECT * FROM users 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        recent_users = [row_to_dict(row) for row in cursor.fetchall()]
        
        # Get system activity
        cursor.execute("""
            SELECT p.*, u.name as user_name, c.title as challenge_title
            FROM progress p
            JOIN users u ON p.user_id = u.id
            JOIN challenges c ON p.challenge_id = c.id
            ORDER BY p.updated_at DESC
            LIMIT 15
        """)
        recent_activity = [row_to_dict(row) for row in cursor.fetchall()]
        
        return jsonify({
            "user": current_user.to_dict(),
            "statistics": {
                "total_students": student_count,
                "total_teachers": teacher_count,
                "total_classes": class_count,
                "total_challenges": challenge_count,
                "completed_challenges": completed_challenges
            },
            "recent_users": recent_users,
            "recent_activity": recent_activity,
            "permissions": rbac_service.get_user_permissions(current_user.role)
        })

# Enhanced User Management Endpoints
@app.get("/api/users")
@require_permission(Permission.VIEW_USERS)
def list_users(current_user):
    """List all users (teachers and admins only)"""
    role_filter = request.args.get('role')
    users = User.get_all_users(role=role_filter)
    return jsonify([user.to_dict() for user in users])

@app.get("/api/users/<int:user_id>")
@require_own_resource_or_permission('user_id', Permission.VIEW_USERS)
def get_user(current_user, user_id):
    """Get specific user (own profile or admin/teacher access)"""
    user = User.find_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({"user": user.to_dict()})

@app.put("/api/users/<int:user_id>")
@require_own_resource_or_permission('user_id', Permission.EDIT_USERS)
def update_user(current_user, user_id):
    """Update user information"""
    user = User.find_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json(force=True)
    
    # Only admins can change roles
    if "role" in data and current_user.role != "admin":
        return jsonify({"error": "Only admins can change user roles"}), 403
    
    # Update allowed fields
    if "role" in data and data["role"] in ["student", "teacher", "admin"]:
        user.role = data["role"]
    
    if "class_id" in data:
        user.class_id = data["class_id"]
    
    if "email" in data:
        email = data["email"].strip() if data["email"] else None
        if email and email != user.email:
            existing_user = User.find_by_email(email)
            if existing_user and existing_user.id != user.id:
                return jsonify({"error": "Email already in use"}), 400
            user.email = email
    
    try:
        user.save()
        return jsonify({
            "message": "User updated successfully",
            "user": user.to_dict()
        })
    except Exception as e:
        return jsonify({"error": "Failed to update user"}), 500

@app.delete("/api/users/<int:user_id>")
@require_permission(Permission.DELETE_USERS)
def delete_user(current_user, user_id):
    """Delete user (admin only)"""
    if current_user.id == user_id:
        return jsonify({"error": "Cannot delete your own account"}), 400
    
    user = User.find_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if user.delete():
        return jsonify({"message": "User deleted successfully"})
    else:
        return jsonify({"error": "Failed to delete user"}), 500

# Permissions endpoint
@app.get("/api/auth/permissions")
@token_required
def get_user_permissions(current_user):
    """Get current user's permissions"""
    permissions = rbac_service.get_user_permissions(current_user.role)
    return jsonify({
        "role": current_user.role,
        "permissions": permissions
    })

# Class Management Endpoints
@app.get("/api/classes")
@require_permission(Permission.VIEW_CLASSES)
def list_classes(current_user):
    """List classes (filtered by teacher for teachers)"""
    if current_user.role == "teacher":
        # Teachers only see their own classes
        classes = Class.find_by_teacher(current_user.id)
    else:
        # Admins see all classes
        classes = Class.get_all_classes()
    
    include_students = request.args.get('include_students', 'false').lower() == 'true'
    include_progress = request.args.get('include_progress', 'false').lower() == 'true'
    
    return jsonify([
        class_obj.to_dict(include_students=include_students, include_progress=include_progress) 
        for class_obj in classes
    ])

@app.post("/api/classes")
@require_permission(Permission.CREATE_CLASSES)
def create_class(current_user):
    """Create a new class"""
    data = request.get_json(force=True)
    
    name = data.get('name', '').strip()
    semester = data.get('semester')
    description = data.get('description', '').strip() or None
    max_students = data.get('max_students')
    
    if not name:
        return jsonify({"error": "Class name is required"}), 400
    
    if not semester or not isinstance(semester, int) or semester < 1:
        return jsonify({"error": "Valid semester number is required"}), 400
    
    # Teachers can only create classes for themselves
    teacher_id = current_user.id if current_user.role == "teacher" else data.get('teacher_id', current_user.id)
    
    # Validate max_students if provided
    if max_students is not None:
        if not isinstance(max_students, int) or max_students < 1:
            return jsonify({"error": "Max students must be a positive number"}), 400
    
    try:
        class_obj = Class.create_class(
            name=name,
            teacher_id=teacher_id,
            semester=semester,
            description=description,
            max_students=max_students
        )
        
        return jsonify({
            "message": "Class created successfully",
            "class": class_obj.to_dict()
        }), 201
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to create class"}), 500

@app.get("/api/classes/<int:class_id>")
@require_permission(Permission.VIEW_CLASSES)
def get_class(current_user, class_id):
    """Get specific class details"""
    class_obj = Class.find_by_id(class_id)
    if not class_obj:
        return jsonify({"error": "Class not found"}), 404
    
    # Teachers can only view their own classes
    if current_user.role == "teacher" and class_obj.teacher_id != current_user.id:
        return jsonify({"error": "Access denied"}), 403
    
    include_students = request.args.get('include_students', 'true').lower() == 'true'
    include_progress = request.args.get('include_progress', 'true').lower() == 'true'
    
    return jsonify({
        "class": class_obj.to_dict(include_students=include_students, include_progress=include_progress)
    })

@app.put("/api/classes/<int:class_id>")
@require_permission(Permission.EDIT_CLASSES)
def update_class(current_user, class_id):
    """Update class information"""
    class_obj = Class.find_by_id(class_id)
    if not class_obj:
        return jsonify({"error": "Class not found"}), 404
    
    # Teachers can only edit their own classes
    if current_user.role == "teacher" and class_obj.teacher_id != current_user.id:
        return jsonify({"error": "Access denied"}), 403
    
    data = request.get_json(force=True)
    
    # Update allowed fields
    if "name" in data:
        name = data["name"].strip()
        if not name:
            return jsonify({"error": "Class name cannot be empty"}), 400
        class_obj.name = name
    
    if "description" in data:
        class_obj.description = data["description"].strip() or None
    
    if "semester" in data:
        semester = data["semester"]
        if not isinstance(semester, int) or semester < 1:
            return jsonify({"error": "Valid semester number is required"}), 400
        class_obj.semester = semester
    
    if "max_students" in data:
        max_students = data["max_students"]
        if max_students is not None:
            if not isinstance(max_students, int) or max_students < 1:
                return jsonify({"error": "Max students must be a positive number"}), 400
            # Check if reducing capacity would exceed current student count
            current_count = class_obj.get_student_count()
            if max_students < current_count:
                return jsonify({
                    "error": f"Cannot reduce capacity below current student count ({current_count})"
                }), 400
        class_obj.max_students = max_students
    
    if "is_active" in data:
        class_obj.is_active = bool(data["is_active"])
    
    # Only admins can change teacher assignment
    if "teacher_id" in data and current_user.role == "admin":
        teacher_id = data["teacher_id"]
        teacher = User.find_by_id(teacher_id)
        if not teacher or teacher.role not in ['teacher', 'admin']:
            return jsonify({"error": "Invalid teacher"}), 400
        class_obj.teacher_id = teacher_id
    
    try:
        class_obj.save()
        return jsonify({
            "message": "Class updated successfully",
            "class": class_obj.to_dict()
        })
    except Exception as e:
        return jsonify({"error": "Failed to update class"}), 500

@app.delete("/api/classes/<int:class_id>")
@require_permission(Permission.DELETE_CLASSES)
def delete_class(current_user, class_id):
    """Delete a class"""
    class_obj = Class.find_by_id(class_id)
    if not class_obj:
        return jsonify({"error": "Class not found"}), 404
    
    # Teachers can only delete their own classes
    if current_user.role == "teacher" and class_obj.teacher_id != current_user.id:
        return jsonify({"error": "Access denied"}), 403
    
    # Check if class has students
    student_count = class_obj.get_student_count()
    if student_count > 0:
        # Offer to deactivate instead of delete
        force_delete = request.args.get('force', 'false').lower() == 'true'
        if not force_delete:
            return jsonify({
                "error": f"Class has {student_count} students. Use ?force=true to delete anyway or deactivate instead.",
                "student_count": student_count,
                "suggestion": "Consider deactivating the class instead"
            }), 400
    
    try:
        if class_obj.delete():
            return jsonify({"message": "Class deleted successfully"})
        else:
            return jsonify({"error": "Failed to delete class"}), 500
    except Exception as e:
        return jsonify({"error": "Failed to delete class"}), 500

@app.post("/api/classes/<int:class_id>/deactivate")
@require_permission(Permission.EDIT_CLASSES)
def deactivate_class(current_user, class_id):
    """Deactivate a class instead of deleting"""
    class_obj = Class.find_by_id(class_id)
    if not class_obj:
        return jsonify({"error": "Class not found"}), 404
    
    # Teachers can only deactivate their own classes
    if current_user.role == "teacher" and class_obj.teacher_id != current_user.id:
        return jsonify({"error": "Access denied"}), 403
    
    try:
        class_obj.deactivate()
        return jsonify({
            "message": "Class deactivated successfully",
            "class": class_obj.to_dict()
        })
    except Exception as e:
        return jsonify({"error": "Failed to deactivate class"}), 500

# Student Enrollment Endpoints
@app.post("/api/classes/<int:class_id>/students")
@require_permission(Permission.MANAGE_CLASS_MEMBERS)
def add_student_to_class(current_user, class_id):
    """Add a student to a class"""
    class_obj = Class.find_by_id(class_id)
    if not class_obj:
        return jsonify({"error": "Class not found"}), 404
    
    # Teachers can only manage their own classes
    if current_user.role == "teacher" and class_obj.teacher_id != current_user.id:
        return jsonify({"error": "Access denied"}), 403
    
    data = request.get_json(force=True)
    student_id = data.get('student_id')
    
    if not student_id:
        return jsonify({"error": "Student ID is required"}), 400
    
    # Verify student exists and is a student
    student = User.find_by_id(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    if student.role != 'student':
        return jsonify({"error": "User is not a student"}), 400
    
    # Check if student is already in a class
    if student.class_id:
        existing_class = Class.find_by_id(student.class_id)
        if existing_class:
            return jsonify({
                "error": f"Student is already enrolled in class '{existing_class.name}'"
            }), 400
    
    try:
        if class_obj.add_student(student_id):
            return jsonify({
                "message": f"Student {student.name} added to class successfully",
                "class": class_obj.to_dict(include_students=True)
            })
        else:
            return jsonify({"error": "Failed to add student to class"}), 500
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to add student to class"}), 500

@app.delete("/api/classes/<int:class_id>/students/<int:student_id>")
@require_permission(Permission.MANAGE_CLASS_MEMBERS)
def remove_student_from_class(current_user, class_id, student_id):
    """Remove a student from a class"""
    class_obj = Class.find_by_id(class_id)
    if not class_obj:
        return jsonify({"error": "Class not found"}), 404
    
    # Teachers can only manage their own classes
    if current_user.role == "teacher" and class_obj.teacher_id != current_user.id:
        return jsonify({"error": "Access denied"}), 403
    
    student = User.find_by_id(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    try:
        if class_obj.remove_student(student_id):
            return jsonify({
                "message": f"Student {student.name} removed from class successfully"
            })
        else:
            return jsonify({"error": "Student was not in this class"}), 400
    except Exception as e:
        return jsonify({"error": "Failed to remove student from class"}), 500

@app.post("/api/classes/join")
@token_required
def join_class_by_code(current_user):
    """Join a class using class code (for students)"""
    if current_user.role != 'student':
        return jsonify({"error": "Only students can join classes"}), 403
    
    data = request.get_json(force=True)
    class_code = data.get('class_code', '').strip().upper()
    
    if not class_code:
        return jsonify({"error": "Class code is required"}), 400
    
    # Check if student is already in a class
    if current_user.class_id:
        existing_class = Class.find_by_id(current_user.class_id)
        if existing_class:
            return jsonify({
                "error": f"You are already enrolled in class '{existing_class.name}'"
            }), 400
    
    # Find class by code
    class_obj = Class.find_by_code(class_code)
    if not class_obj:
        return jsonify({"error": "Invalid class code"}), 404
    
    if not class_obj.is_active:
        return jsonify({"error": "This class is no longer active"}), 400
    
    try:
        if class_obj.add_student(current_user.id):
            return jsonify({
                "message": f"Successfully joined class '{class_obj.name}'",
                "class": class_obj.to_dict()
            })
        else:
            return jsonify({"error": "Failed to join class"}), 500
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to join class"}), 500

@app.post("/api/classes/<int:class_id>/leave")
@token_required
def leave_class(current_user, class_id):
    """Leave a class (for students)"""
    if current_user.role != 'student':
        return jsonify({"error": "Only students can leave classes"}), 403
    
    if current_user.class_id != class_id:
        return jsonify({"error": "You are not enrolled in this class"}), 400
    
    class_obj = Class.find_by_id(class_id)
    if not class_obj:
        return jsonify({"error": "Class not found"}), 404
    
    try:
        if class_obj.remove_student(current_user.id):
            return jsonify({
                "message": f"Successfully left class '{class_obj.name}'"
            })
        else:
            return jsonify({"error": "Failed to leave class"}), 500
    except Exception as e:
        return jsonify({"error": "Failed to leave class"}), 500

@app.get("/api/classes/<int:class_id>/students")
@require_permission(Permission.VIEW_CLASSES)
def get_class_students(current_user, class_id):
    """Get all students in a class"""
    class_obj = Class.find_by_id(class_id)
    if not class_obj:
        return jsonify({"error": "Class not found"}), 404
    
    # Teachers can only view their own classes
    if current_user.role == "teacher" and class_obj.teacher_id != current_user.id:
        return jsonify({"error": "Access denied"}), 403
    
    students = class_obj.get_students()
    return jsonify({
        "class_id": class_id,
        "class_name": class_obj.name,
        "students": [student.to_dict() for student in students],
        "total_students": len(students)
    })


# Modules and challenges
@app.get("/api/modules")
def get_modules():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM modules ORDER BY semester, id")
        mods = [row_to_dict(r) for r in cur.fetchall()]
        for m in mods:
            cur.execute("SELECT * FROM challenges WHERE module_id=? ORDER BY id", (m["id"],))
            m["challenges"] = [row_to_dict(r) for r in cur.fetchall()]
        return jsonify(mods)


# Progress (protected endpoints but lenient for MVP if no token)
@app.get("/api/progress/<int:user_id>")
def get_progress(user_id: int):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM progress WHERE user_id=?", (user_id,))
        rows = [row_to_dict(r) for r in cur.fetchall()]
        total_points = sum(r["points"] for r in rows)
        completed = [r["challenge_id"] for r in rows if r["status"] == "completed"]
        return jsonify({"user_id": user_id, "points": total_points, "completed": completed, "entries": rows})


@app.post("/api/progress")
def upsert_progress():
    # For MVP, allow without JWT but prefer with Authorization: Bearer <token>
    payload = get_auth_user()
    data = request.get_json(force=True)
    user_id = data.get("user_id") or (payload and payload.get("user_id"))
    challenge_id = data.get("challenge_id")
    status = data.get("status", "started")
    points = int(data.get("points", 0))
    if not user_id or not challenge_id:
        return jsonify({"error": "user_id and challenge_id required"}), 400
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM progress WHERE user_id=? AND challenge_id=?", (user_id, challenge_id))
        row = cur.fetchone()
        ts = datetime.utcnow().isoformat()
        if row:
            cur.execute("UPDATE progress SET status=?, points=?, updated_at=? WHERE id=?", (status, points, ts, row["id"]))
        else:
            cur.execute("INSERT INTO progress(user_id, challenge_id, status, points, updated_at) VALUES(?,?,?,?,?)",
                        (user_id, challenge_id, status, points, ts))
        # optional: write detailed action
        cur.execute("INSERT INTO detailed_progress(user_id, challenge_id, action, payload, created_at) VALUES(?,?,?,?,?)",
                    (user_id, challenge_id, "upsert_progress", json.dumps(data), ts))
        conn.commit()
        return jsonify({"ok": True})


@app.get("/api/leaderboard")
def api_leaderboard():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
        SELECT u.name, COALESCE(SUM(p.points),0) AS points
        FROM users u
        LEFT JOIN progress p ON p.user_id=u.id
        GROUP BY u.id
        ORDER BY points DESC, u.name ASC
        """)
        rows = [{"name": r["name"], "points": r["points"]} for r in cur.fetchall()]
        return jsonify(rows)


if __name__ == "__main__":
    # Flask 3.1 menghapus before_first_request; panggil setup() langsung saat start
    setup()
    app.run(host="127.0.0.1", port=5001, debug=True)
