"""
Class model for managing student groups and teacher assignments
"""

import json
from datetime import datetime
from database import get_conn, row_to_dict

class Class:
    def __init__(self, id=None, name=None, teacher_id=None, semester=None, 
                 created_at=None, is_active=True, description=None, 
                 max_students=None, class_code=None):
        self.id = id
        self.name = name
        self.teacher_id = teacher_id
        self.semester = semester
        self.created_at = created_at
        self.is_active = is_active
        self.description = description
        self.max_students = max_students
        self.class_code = class_code
    
    @classmethod
    def find_by_id(cls, class_id):
        """Find class by ID"""
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM classes WHERE id = ?", (class_id,))
            row = cursor.fetchone()
            if row:
                return cls.from_db_row(row)
        return None
    
    @classmethod
    def find_by_teacher(cls, teacher_id):
        """Find all classes for a specific teacher"""
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM classes 
                WHERE teacher_id = ? 
                ORDER BY created_at DESC
            """, (teacher_id,))
            classes = []
            for row in cursor.fetchall():
                classes.append(cls.from_db_row(row))
            return classes
    
    @classmethod
    def find_by_code(cls, class_code):
        """Find class by class code"""
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM classes WHERE class_code = ?", (class_code,))
            row = cursor.fetchone()
            if row:
                return cls.from_db_row(row)
        return None
    
    @classmethod
    def get_all_classes(cls, active_only=True):
        """Get all classes, optionally filtered by active status"""
        with get_conn() as conn:
            cursor = conn.cursor()
            if active_only:
                cursor.execute("SELECT * FROM classes WHERE is_active = 1 ORDER BY created_at DESC")
            else:
                cursor.execute("SELECT * FROM classes ORDER BY created_at DESC")
            
            classes = []
            for row in cursor.fetchall():
                classes.append(cls.from_db_row(row))
            return classes
    
    @classmethod
    def from_db_row(cls, row):
        """Create Class instance from database row"""
        data = row_to_dict(row)
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            teacher_id=data.get('teacher_id'),
            semester=data.get('semester'),
            created_at=data.get('created_at'),
            is_active=bool(data.get('is_active', True)),
            description=data.get('description'),
            max_students=data.get('max_students'),
            class_code=data.get('class_code')
        )
    
    def save(self):
        """Save class to database"""
        with get_conn() as conn:
            cursor = conn.cursor()
            
            if self.id:
                # Update existing class
                cursor.execute("""
                    UPDATE classes SET 
                        name = ?, teacher_id = ?, semester = ?, 
                        is_active = ?, description = ?, max_students = ?, 
                        class_code = ?
                    WHERE id = ?
                """, (
                    self.name, self.teacher_id, self.semester,
                    self.is_active, self.description, self.max_students,
                    self.class_code, self.id
                ))
            else:
                # Create new class
                if not self.created_at:
                    self.created_at = datetime.utcnow().isoformat()
                
                # Generate class code if not provided
                if not self.class_code:
                    self.class_code = self._generate_class_code()
                
                cursor.execute("""
                    INSERT INTO classes (name, teacher_id, semester, created_at, 
                                       is_active, description, max_students, class_code)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.name, self.teacher_id, self.semester, self.created_at,
                    self.is_active, self.description, self.max_students, self.class_code
                ))
                self.id = cursor.lastrowid
            
            conn.commit()
        return self
    
    def delete(self):
        """Delete class from database"""
        if not self.id:
            return False
        
        with get_conn() as conn:
            cursor = conn.cursor()
            
            # First, remove students from this class
            cursor.execute("UPDATE users SET class_id = NULL WHERE class_id = ?", (self.id,))
            
            # Then delete the class
            cursor.execute("DELETE FROM classes WHERE id = ?", (self.id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def deactivate(self):
        """Deactivate class instead of deleting"""
        self.is_active = False
        return self.save()
    
    def get_students(self):
        """Get all students in this class"""
        if not self.id:
            return []
        
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM users 
                WHERE class_id = ? AND role = 'student'
                ORDER BY name
            """, (self.id,))
            
            from models.user import User
            students = []
            for row in cursor.fetchall():
                students.append(User.from_db_row(row))
            return students
    
    def get_student_count(self):
        """Get number of students in this class"""
        if not self.id:
            return 0
        
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as count FROM users 
                WHERE class_id = ? AND role = 'student'
            """, (self.id,))
            return cursor.fetchone()['count']
    
    def add_student(self, student_id):
        """Add a student to this class"""
        if not self.id:
            return False
        
        # Check if class is at capacity
        if self.max_students and self.get_student_count() >= self.max_students:
            raise ValueError("Class is at maximum capacity")
        
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET class_id = ? 
                WHERE id = ? AND role = 'student'
            """, (self.id, student_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def remove_student(self, student_id):
        """Remove a student from this class"""
        if not self.id:
            return False
        
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET class_id = NULL 
                WHERE id = ? AND class_id = ?
            """, (student_id, self.id))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_teacher(self):
        """Get the teacher for this class"""
        if not self.teacher_id:
            return None
        
        from models.user import User
        return User.find_by_id(self.teacher_id)
    
    def get_class_progress(self):
        """Get progress statistics for this class"""
        if not self.id:
            return {}
        
        with get_conn() as conn:
            cursor = conn.cursor()
            
            # Get total students
            cursor.execute("""
                SELECT COUNT(*) as count FROM users 
                WHERE class_id = ? AND role = 'student'
            """, (self.id,))
            total_students = cursor.fetchone()['count']
            
            # Get total completed challenges
            cursor.execute("""
                SELECT COUNT(*) as count FROM progress p
                JOIN users u ON p.user_id = u.id
                WHERE u.class_id = ? AND p.status = 'completed'
            """, (self.id,))
            completed_challenges = cursor.fetchone()['count']
            
            # Get total points earned
            cursor.execute("""
                SELECT COALESCE(SUM(p.points), 0) as total_points FROM progress p
                JOIN users u ON p.user_id = u.id
                WHERE u.class_id = ?
            """, (self.id,))
            total_points = cursor.fetchone()['total_points']
            
            # Get average progress per student
            avg_progress = completed_challenges / total_students if total_students > 0 else 0
            
            return {
                'total_students': total_students,
                'completed_challenges': completed_challenges,
                'total_points': total_points,
                'average_progress': round(avg_progress, 2)
            }
    
    def to_dict(self, include_students=False, include_progress=False):
        """Convert class to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'teacher_id': self.teacher_id,
            'semester': self.semester,
            'created_at': self.created_at,
            'is_active': self.is_active,
            'description': self.description,
            'max_students': self.max_students,
            'class_code': self.class_code,
            'student_count': self.get_student_count() if self.id else 0
        }
        
        if include_students:
            data['students'] = [student.to_dict() for student in self.get_students()]
        
        if include_progress:
            data['progress'] = self.get_class_progress()
        
        # Include teacher info
        teacher = self.get_teacher()
        if teacher:
            data['teacher'] = {
                'id': teacher.id,
                'name': teacher.name,
                'email': teacher.email
            }
        
        return data
    
    def _generate_class_code(self):
        """Generate a unique class code"""
        import random
        import string
        
        while True:
            # Generate 6-character code (letters and numbers)
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            
            # Check if code already exists
            existing = self.find_by_code(code)
            if not existing:
                return code
    
    @classmethod
    def create_class(cls, name, teacher_id, semester, description=None, max_students=None):
        """Create a new class with validation"""
        if not name or not name.strip():
            raise ValueError("Class name is required")
        
        if not teacher_id:
            raise ValueError("Teacher ID is required")
        
        if not semester or semester < 1:
            raise ValueError("Valid semester is required")
        
        # Verify teacher exists and has teacher role
        from models.user import User
        teacher = User.find_by_id(teacher_id)
        if not teacher:
            raise ValueError("Teacher not found")
        
        if teacher.role not in ['teacher', 'admin']:
            raise ValueError("Only teachers and admins can create classes")
        
        # Create class
        class_obj = cls(
            name=name.strip(),
            teacher_id=teacher_id,
            semester=semester,
            description=description.strip() if description else None,
            max_students=max_students
        )
        
        return class_obj.save()