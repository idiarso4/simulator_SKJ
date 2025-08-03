"""
Enhanced Challenge model with advanced simulation properties
"""

import json
from datetime import datetime
from enum import Enum
from database import get_conn, row_to_dict

class DifficultyLevel(Enum):
    """Challenge difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class SimulationType(Enum):
    """Types of challenge simulations"""
    VISUAL = "visual"          # Interactive visual diagrams
    NETWORK = "network"        # Network topology simulation
    TERMINAL = "terminal"      # Command-line simulation
    LAB = "lab"               # Virtual lab environment
    QUIZ = "quiz"             # Interactive quiz/assessment
    SCENARIO = "scenario"     # Story-based scenario

class Challenge:
    def __init__(self, id=None, module_id=None, title=None, description=None,
                 tasks_json=None, difficulty=DifficultyLevel.BEGINNER.value,
                 simulation_type=SimulationType.VISUAL.value, simulation_config=None,
                 hints=None, solution=None, points=50, time_limit=None,
                 prerequisites=None, created_at=None, updated_at=None,
                 is_active=True, tags=None, estimated_duration=None):
        self.id = id
        self.module_id = module_id
        self.title = title
        self.description = description
        self.tasks_json = tasks_json
        self.difficulty = difficulty
        self.simulation_type = simulation_type
        self.simulation_config = simulation_config or {}
        self.hints = hints or []
        self.solution = solution or {}
        self.points = points
        self.time_limit = time_limit
        self.prerequisites = prerequisites or []
        self.created_at = created_at
        self.updated_at = updated_at
        self.is_active = is_active
        self.tags = tags or []
        self.estimated_duration = estimated_duration
    
    @classmethod
    def find_by_id(cls, challenge_id):
        """Find challenge by ID"""
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM challenges WHERE id = ?", (challenge_id,))
            row = cursor.fetchone()
            if row:
                return cls.from_db_row(row)
        return None
    
    @classmethod
    def find_by_module(cls, module_id, active_only=True):
        """Find all challenges for a specific module"""
        with get_conn() as conn:
            cursor = conn.cursor()
            if active_only:
                cursor.execute("""
                    SELECT * FROM challenges 
                    WHERE module_id = ? AND is_active = 1
                    ORDER BY id
                """, (module_id,))
            else:
                cursor.execute("""
                    SELECT * FROM challenges 
                    WHERE module_id = ?
                    ORDER BY id
                """, (module_id,))
            
            challenges = []
            for row in cursor.fetchall():
                challenges.append(cls.from_db_row(row))
            return challenges
    
    @classmethod
    def find_by_difficulty(cls, difficulty):
        """Find challenges by difficulty level"""
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM challenges 
                WHERE difficulty = ? AND is_active = 1
                ORDER BY module_id, id
            """, (difficulty,))
            
            challenges = []
            for row in cursor.fetchall():
                challenges.append(cls.from_db_row(row))
            return challenges
    
    @classmethod
    def find_by_simulation_type(cls, simulation_type):
        """Find challenges by simulation type"""
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM challenges 
                WHERE simulation_type = ? AND is_active = 1
                ORDER BY module_id, id
            """, (simulation_type,))
            
            challenges = []
            for row in cursor.fetchall():
                challenges.append(cls.from_db_row(row))
            return challenges
    
    @classmethod
    def get_all_challenges(cls, active_only=True):
        """Get all challenges"""
        with get_conn() as conn:
            cursor = conn.cursor()
            if active_only:
                cursor.execute("SELECT * FROM challenges WHERE is_active = 1 ORDER BY module_id, id")
            else:
                cursor.execute("SELECT * FROM challenges ORDER BY module_id, id")
            
            challenges = []
            for row in cursor.fetchall():
                challenges.append(cls.from_db_row(row))
            return challenges
    
    @classmethod
    def from_db_row(cls, row):
        """Create Challenge instance from database row"""
        data = row_to_dict(row)
        
        # Parse JSON fields
        simulation_config = {}
        if data.get('simulation_config'):
            try:
                simulation_config = json.loads(data['simulation_config'])
            except:
                simulation_config = {}
        
        hints = []
        if data.get('hints'):
            try:
                hints = json.loads(data['hints'])
            except:
                hints = []
        
        solution = {}
        if data.get('solution'):
            try:
                solution = json.loads(data['solution'])
            except:
                solution = {}
        
        prerequisites = []
        if data.get('prerequisites'):
            try:
                prerequisites = json.loads(data['prerequisites'])
            except:
                prerequisites = []
        
        tags = []
        if data.get('tags'):
            try:
                tags = json.loads(data['tags'])
            except:
                tags = []
        
        return cls(
            id=data.get('id'),
            module_id=data.get('module_id'),
            title=data.get('title'),
            description=data.get('description'),
            tasks_json=data.get('tasks_json'),
            difficulty=data.get('difficulty', DifficultyLevel.BEGINNER.value),
            simulation_type=data.get('simulation_type', SimulationType.VISUAL.value),
            simulation_config=simulation_config,
            hints=hints,
            solution=solution,
            points=data.get('points', 50),
            time_limit=data.get('time_limit'),
            prerequisites=prerequisites,
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            is_active=bool(data.get('is_active', True)),
            tags=tags,
            estimated_duration=data.get('estimated_duration')
        )
    
    def save(self):
        """Save challenge to database"""
        conn = get_conn()
        try:
            cursor = conn.cursor()
            
            # Serialize JSON fields
            simulation_config_json = json.dumps(self.simulation_config) if self.simulation_config else None
            hints_json = json.dumps(self.hints) if self.hints else None
            solution_json = json.dumps(self.solution) if self.solution else None
            prerequisites_json = json.dumps(self.prerequisites) if self.prerequisites else None
            tags_json = json.dumps(self.tags) if self.tags else None
            
            # Check if challenge exists
            cursor.execute("SELECT id FROM challenges WHERE id = ?", (self.id,))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing challenge
                self.updated_at = datetime.utcnow().isoformat()
                cursor.execute("""
                    UPDATE challenges SET 
                        module_id = ?, title = ?, description = ?, tasks_json = ?,
                        difficulty = ?, simulation_type = ?, simulation_config = ?,
                        hints = ?, solution = ?, points = ?, time_limit = ?,
                        prerequisites = ?, updated_at = ?, is_active = ?,
                        tags = ?, estimated_duration = ?
                    WHERE id = ?
                """, (
                    self.module_id, self.title, self.description, self.tasks_json,
                    self.difficulty, self.simulation_type, simulation_config_json,
                    hints_json, solution_json, self.points, self.time_limit,
                    prerequisites_json, self.updated_at, self.is_active,
                    tags_json, self.estimated_duration, self.id
                ))
            else:
                # Create new challenge
                if not self.created_at:
                    self.created_at = datetime.utcnow().isoformat()
                self.updated_at = self.created_at
                
                cursor.execute("""
                    INSERT INTO challenges (id, module_id, title, description, tasks_json,
                                          difficulty, simulation_type, simulation_config,
                                          hints, solution, points, time_limit,
                                          prerequisites, created_at, updated_at, is_active,
                                          tags, estimated_duration)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.id, self.module_id, self.title, self.description, self.tasks_json,
                    self.difficulty, self.simulation_type, simulation_config_json,
                    hints_json, solution_json, self.points, self.time_limit,
                    prerequisites_json, self.created_at, self.updated_at, self.is_active,
                    tags_json, self.estimated_duration
                ))
            
            conn.commit()
        finally:
            conn.close()
            
        return self
    
    def delete(self):
        """Delete challenge from database"""
        if not self.id:
            return False
        
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM challenges WHERE id = ?", (self.id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def deactivate(self):
        """Deactivate challenge instead of deleting"""
        self.is_active = False
        return self.save()
    
    def get_tasks(self):
        """Get parsed tasks list"""
        if not self.tasks_json:
            return []
        
        try:
            return json.loads(self.tasks_json)
        except:
            return []
    
    def set_tasks(self, tasks):
        """Set tasks from list"""
        self.tasks_json = json.dumps(tasks) if tasks else None
    
    def add_hint(self, hint_text, hint_type="text"):
        """Add a hint to the challenge"""
        hint = {
            "type": hint_type,
            "content": hint_text,
            "order": len(self.hints) + 1
        }
        self.hints.append(hint)
    
    def get_hint(self, hint_index):
        """Get a specific hint by index"""
        if 0 <= hint_index < len(self.hints):
            return self.hints[hint_index]
        return None
    
    def check_prerequisites(self, user_completed_challenges):
        """Check if user has completed prerequisite challenges"""
        if not self.prerequisites:
            return True, []
        
        missing_prerequisites = []
        for prereq_id in self.prerequisites:
            if prereq_id not in user_completed_challenges:
                missing_prerequisites.append(prereq_id)
        
        return len(missing_prerequisites) == 0, missing_prerequisites
    
    def get_difficulty_info(self):
        """Get difficulty information"""
        difficulty_info = {
            DifficultyLevel.BEGINNER.value: {
                "name": "Beginner",
                "description": "Basic concepts and simple tasks",
                "color": "#4CAF50",
                "multiplier": 1.0
            },
            DifficultyLevel.INTERMEDIATE.value: {
                "name": "Intermediate", 
                "description": "Moderate complexity requiring some experience",
                "color": "#FF9800",
                "multiplier": 1.5
            },
            DifficultyLevel.ADVANCED.value: {
                "name": "Advanced",
                "description": "Complex scenarios requiring solid understanding",
                "color": "#F44336",
                "multiplier": 2.0
            },
            DifficultyLevel.EXPERT.value: {
                "name": "Expert",
                "description": "Highly complex challenges for experts",
                "color": "#9C27B0",
                "multiplier": 3.0
            }
        }
        return difficulty_info.get(self.difficulty, difficulty_info[DifficultyLevel.BEGINNER.value])
    
    def get_simulation_info(self):
        """Get simulation type information"""
        simulation_info = {
            SimulationType.VISUAL.value: {
                "name": "Visual Simulation",
                "description": "Interactive diagrams and visual elements",
                "icon": "🎨",
                "requires_interaction": True
            },
            SimulationType.NETWORK.value: {
                "name": "Network Simulation",
                "description": "Network topology and packet flow simulation",
                "icon": "🌐",
                "requires_interaction": True
            },
            SimulationType.TERMINAL.value: {
                "name": "Terminal Simulation",
                "description": "Command-line interface simulation",
                "icon": "💻",
                "requires_interaction": True
            },
            SimulationType.LAB.value: {
                "name": "Virtual Lab",
                "description": "Isolated virtual environment",
                "icon": "🧪",
                "requires_interaction": True
            },
            SimulationType.QUIZ.value: {
                "name": "Interactive Quiz",
                "description": "Question and answer assessment",
                "icon": "❓",
                "requires_interaction": True
            },
            SimulationType.SCENARIO.value: {
                "name": "Scenario-based",
                "description": "Story-driven learning experience",
                "icon": "📖",
                "requires_interaction": False
            }
        }
        return simulation_info.get(self.simulation_type, simulation_info[SimulationType.VISUAL.value])
    
    def calculate_points(self, completion_time=None, hints_used=0):
        """Calculate points based on difficulty, time, and hints used"""
        base_points = self.points
        difficulty_multiplier = self.get_difficulty_info()["multiplier"]
        
        # Apply difficulty multiplier
        total_points = int(base_points * difficulty_multiplier)
        
        # Time bonus (if completed within time limit)
        if self.time_limit and completion_time and completion_time <= self.time_limit:
            time_bonus = max(0, int((self.time_limit - completion_time) / self.time_limit * base_points * 0.2))
            total_points += time_bonus
        
        # Hint penalty
        hint_penalty = hints_used * int(base_points * 0.1)
        total_points = max(int(base_points * 0.3), total_points - hint_penalty)
        
        return total_points
    
    def to_dict(self, include_solution=False, include_hints=False, user_progress=None):
        """Convert challenge to dictionary"""
        difficulty_info = self.get_difficulty_info()
        simulation_info = self.get_simulation_info()
        
        data = {
            'id': self.id,
            'module_id': self.module_id,
            'title': self.title,
            'description': self.description,
            'tasks': self.get_tasks(),
            'difficulty': self.difficulty,
            'difficulty_info': difficulty_info,
            'simulation_type': self.simulation_type,
            'simulation_info': simulation_info,
            'simulation_config': self.simulation_config,
            'points': self.points,
            'time_limit': self.time_limit,
            'prerequisites': self.prerequisites,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': self.is_active,
            'tags': self.tags,
            'estimated_duration': self.estimated_duration
        }
        
        # Include hints if requested (for teachers/admins or progressive hints for students)
        if include_hints:
            data['hints'] = self.hints
        else:
            data['hint_count'] = len(self.hints)
        
        # Include solution only for teachers/admins
        if include_solution:
            data['solution'] = self.solution
        
        # Include user-specific progress if provided
        if user_progress:
            data['user_progress'] = user_progress
        
        return data
    
    @classmethod
    def create_challenge(cls, id, module_id, title, description=None, tasks=None,
                        difficulty=DifficultyLevel.BEGINNER.value,
                        simulation_type=SimulationType.VISUAL.value,
                        simulation_config=None, points=50, time_limit=None,
                        prerequisites=None, tags=None, estimated_duration=None):
        """Create a new challenge with validation"""
        if not id or not id.strip():
            raise ValueError("Challenge ID is required")
        
        if not module_id or not module_id.strip():
            raise ValueError("Module ID is required")
        
        if not title or not title.strip():
            raise ValueError("Challenge title is required")
        
        # Validate difficulty
        if difficulty not in [d.value for d in DifficultyLevel]:
            raise ValueError(f"Invalid difficulty level: {difficulty}")
        
        # Validate simulation type
        if simulation_type not in [s.value for s in SimulationType]:
            raise ValueError(f"Invalid simulation type: {simulation_type}")
        
        # Validate points
        if points < 0:
            raise ValueError("Points must be non-negative")
        
        # Validate time limit
        if time_limit is not None and time_limit <= 0:
            raise ValueError("Time limit must be positive")
        
        # Check if challenge ID already exists
        existing = cls.find_by_id(id)
        if existing:
            raise ValueError(f"Challenge with ID '{id}' already exists")
        
        # Create challenge
        challenge = cls(
            id=id.strip(),
            module_id=module_id.strip(),
            title=title.strip(),
            description=description.strip() if description else None,
            difficulty=difficulty,
            simulation_type=simulation_type,
            simulation_config=simulation_config or {},
            points=points,
            time_limit=time_limit,
            prerequisites=prerequisites or [],
            tags=tags or [],
            estimated_duration=estimated_duration
        )
        
        # Set tasks
        if tasks:
            challenge.set_tasks(tasks)
        else:
            challenge.tasks_json = "[]"  # Default empty tasks
        
        return challenge.save()