"""
Enhanced User model with authentication capabilities
"""

import bcrypt
import json
from datetime import datetime
from database import get_conn, row_to_dict

class User:
    def __init__(self, id=None, name=None, email=None, password_hash=None, 
                 role='student', class_id=None, profile_picture=None, 
                 preferences=None, created_at=None, last_active=None):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.class_id = class_id
        self.profile_picture = profile_picture
        self.preferences = preferences or {}
        self.created_at = created_at
        self.last_active = last_active
    
    @staticmethod
    def hash_password(password):
        """Hash a password using bcrypt"""
        if not password:
            return None
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches the stored hash"""
        if not password or not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    @classmethod
    def find_by_id(cls, user_id):
        """Find user by ID"""
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return cls.from_db_row(row)
        return None
    
    @classmethod
    def find_by_name(cls, name):
        """Find user by name"""
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
            row = cursor.fetchone()
            if row:
                return cls.from_db_row(row)
        return None
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email"""
        if not email:
            return None
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            if row:
                return cls.from_db_row(row)
        return None
    
    @classmethod
    def from_db_row(cls, row):
        """Create User instance from database row"""
        data = row_to_dict(row)
        preferences = {}
        if data.get('preferences'):
            try:
                preferences = json.loads(data['preferences'])
            except:
                preferences = {}
        
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            email=data.get('email'),
            password_hash=data.get('password_hash'),
            role=data.get('role', 'student'),
            class_id=data.get('class_id'),
            profile_picture=data.get('profile_picture'),
            preferences=preferences,
            created_at=data.get('created_at'),
            last_active=data.get('last_active')
        )
    
    def save(self):
        """Save user to database"""
        with get_conn() as conn:
            cursor = conn.cursor()
            preferences_json = json.dumps(self.preferences) if self.preferences else None
            
            # Check for email uniqueness if email is being set
            if self.email:
                existing_user = self.find_by_email(self.email)
                if existing_user and existing_user.id != self.id:
                    raise ValueError("User with this email already exists")
            
            if self.id:
                # Update existing user
                cursor.execute("""
                    UPDATE users SET 
                        name = ?, email = ?, password_hash = ?, role = ?, 
                        class_id = ?, profile_picture = ?, preferences = ?, 
                        last_active = ?
                    WHERE id = ?
                """, (
                    self.name, self.email, self.password_hash, self.role,
                    self.class_id, self.profile_picture, preferences_json,
                    self.last_active, self.id
                ))
            else:
                # Create new user
                if not self.created_at:
                    self.created_at = datetime.utcnow().isoformat()
                
                cursor.execute("""
                    INSERT INTO users (name, email, password_hash, role, class_id, 
                                     profile_picture, preferences, created_at, last_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.name, self.email, self.password_hash, self.role,
                    self.class_id, self.profile_picture, preferences_json,
                    self.created_at, self.last_active
                ))
                self.id = cursor.lastrowid
            
            conn.commit()
        return self
    
    def update_last_active(self):
        """Update last active timestamp"""
        self.last_active = datetime.utcnow().isoformat()
        if self.id:
            with get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET last_active = ? WHERE id = ?",
                    (self.last_active, self.id)
                )
                conn.commit()
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'class_id': self.class_id,
            'profile_picture': self.profile_picture,
            'preferences': self.preferences,
            'created_at': self.created_at,
            'last_active': self.last_active
        }
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
        
        return data
    
    @classmethod
    def get_all_users(cls, role=None):
        """Get all users, optionally filtered by role"""
        with get_conn() as conn:
            cursor = conn.cursor()
            if role:
                cursor.execute("SELECT * FROM users WHERE role = ? ORDER BY created_at DESC", (role,))
            else:
                cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
            
            users = []
            for row in cursor.fetchall():
                users.append(cls.from_db_row(row))
            return users
    
    @classmethod
    def create_user(cls, name, email=None, password=None, role='student', class_id=None):
        """Create a new user with validation"""
        # Validate required fields
        if not name or not name.strip():
            raise ValueError("Name is required")
        
        name = name.strip()
        
        # Check if user already exists
        if cls.find_by_name(name):
            raise ValueError("User with this name already exists")
        
        if email:
            email = email.strip()
            existing_email_user = cls.find_by_email(email)
            if existing_email_user:
                raise ValueError("User with this email already exists")
        
        # Create user
        user = cls(
            name=name,
            email=email.strip() if email else None,
            role=role,
            class_id=class_id
        )
        
        # Set password if provided
        if password:
            user.password_hash = cls.hash_password(password)
        
        return user.save()
    
    def delete(self):
        """Delete user from database"""
        if not self.id:
            return False
        
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (self.id,))
            conn.commit()
            return cursor.rowcount > 0