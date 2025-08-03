"""
Prerequisite Validation Service for challenges
"""

from models.challenge import Challenge
from database import get_conn

class PrerequisiteService:
    """Service for managing and validating challenge prerequisites"""
    
    def __init__(self):
        pass
    
    def validate_prerequisites(self, challenge_id, user_id):
        """Validate if user has completed prerequisites for a challenge"""
        challenge = Challenge.find_by_id(challenge_id)
        if not challenge:
            return False, ["Challenge not found"]
        
        if not challenge.prerequisites:
            return True, []
        
        # Get user's completed challenges
        completed_challenges = self.get_user_completed_challenges(user_id)
        
        # Check prerequisites
        missing_prerequisites = []
        for prereq_id in challenge.prerequisites:
            if prereq_id not in completed_challenges:
                prereq_challenge = Challenge.find_by_id(prereq_id)
                if prereq_challenge:
                    missing_prerequisites.append({
                        'id': prereq_id,
                        'title': prereq_challenge.title,
                        'module_id': prereq_challenge.module_id
                    })
                else:
                    missing_prerequisites.append({
                        'id': prereq_id,
                        'title': f"Unknown Challenge ({prereq_id})",
                        'module_id': 'unknown'
                    })
        
        return len(missing_prerequisites) == 0, missing_prerequisites
    
    def get_user_completed_challenges(self, user_id):
        """Get list of challenge IDs completed by user"""
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT challenge_id FROM progress 
                WHERE user_id = ? AND status = 'completed'
            """, (user_id,))
            
            return [row[0] for row in cursor.fetchall()]
    
    def get_available_challenges(self, user_id, module_id=None):
        """Get challenges available to user (prerequisites met)"""
        # Get all challenges
        if module_id:
            all_challenges = Challenge.find_by_module(module_id)
        else:
            all_challenges = Challenge.get_all_challenges()
        
        # Get user's completed challenges
        completed_challenges = self.get_user_completed_challenges(user_id)
        
        available_challenges = []
        locked_challenges = []
        
        for challenge in all_challenges:
            can_access, missing_prereqs = self.validate_prerequisites(challenge.id, user_id)
            
            if can_access:
                available_challenges.append({
                    'challenge': challenge,
                    'status': 'completed' if challenge.id in completed_challenges else 'available'
                })
            else:
                locked_challenges.append({
                    'challenge': challenge,
                    'status': 'locked',
                    'missing_prerequisites': missing_prereqs
                })
        
        return available_challenges, locked_challenges
    
    def get_prerequisite_chain(self, challenge_id, visited=None):
        """Get the complete prerequisite chain for a challenge"""
        if visited is None:
            visited = set()
        
        if challenge_id in visited:
            return []  # Circular dependency detected
        
        visited.add(challenge_id)
        
        challenge = Challenge.find_by_id(challenge_id)
        if not challenge or not challenge.prerequisites:
            return []
        
        chain = []
        for prereq_id in challenge.prerequisites:
            prereq_challenge = Challenge.find_by_id(prereq_id)
            if prereq_challenge:
                # Add the prerequisite
                chain.append({
                    'id': prereq_id,
                    'title': prereq_challenge.title,
                    'module_id': prereq_challenge.module_id,
                    'level': 1
                })
                
                # Recursively get prerequisites of prerequisites
                sub_chain = self.get_prerequisite_chain(prereq_id, visited.copy())
                for item in sub_chain:
                    item['level'] += 1
                    chain.append(item)
        
        return chain
    
    def validate_prerequisite_chain(self, challenge_id):
        """Validate that prerequisite chain doesn't have circular dependencies"""
        try:
            chain = self.get_prerequisite_chain(challenge_id)
            return True, chain
        except RecursionError:
            return False, "Circular dependency detected in prerequisite chain"
    
    def suggest_learning_path(self, user_id, target_challenge_id):
        """Suggest optimal learning path to reach target challenge"""
        target_challenge = Challenge.find_by_id(target_challenge_id)
        if not target_challenge:
            return []
        
        # Check if user can already access the challenge
        can_access, missing_prereqs = self.validate_prerequisites(target_challenge_id, user_id)
        if can_access:
            return []  # No path needed, already accessible
        
        # Get completed challenges
        completed = set(self.get_user_completed_challenges(user_id))
        
        # Build learning path
        learning_path = []
        to_complete = set()
        
        # Add direct prerequisites
        for prereq in missing_prereqs:
            to_complete.add(prereq['id'])
        
        # Add prerequisites of prerequisites
        for prereq_id in list(to_complete):
            prereq_chain = self.get_prerequisite_chain(prereq_id)
            for item in prereq_chain:
                if item['id'] not in completed:
                    to_complete.add(item['id'])
        
        # Sort by dependency order (challenges with no prerequisites first)
        sorted_challenges = self._topological_sort(list(to_complete))
        
        for challenge_id in sorted_challenges:
            challenge = Challenge.find_by_id(challenge_id)
            if challenge:
                learning_path.append({
                    'id': challenge_id,
                    'title': challenge.title,
                    'module_id': challenge.module_id,
                    'difficulty': challenge.difficulty,
                    'estimated_duration': challenge.estimated_duration,
                    'points': challenge.points
                })
        
        return learning_path
    
    def _topological_sort(self, challenge_ids):
        """Sort challenges in dependency order using topological sort"""
        # Build adjacency list
        graph = {cid: [] for cid in challenge_ids}
        in_degree = {cid: 0 for cid in challenge_ids}
        
        for challenge_id in challenge_ids:
            challenge = Challenge.find_by_id(challenge_id)
            if challenge and challenge.prerequisites:
                for prereq_id in challenge.prerequisites:
                    if prereq_id in graph:
                        graph[prereq_id].append(challenge_id)
                        in_degree[challenge_id] += 1
        
        # Kahn's algorithm
        queue = [cid for cid in challenge_ids if in_degree[cid] == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result
    
    def get_challenge_dependencies(self, challenge_id):
        """Get challenges that depend on this challenge"""
        dependencies = []
        all_challenges = Challenge.get_all_challenges()
        
        for challenge in all_challenges:
            if challenge.prerequisites and challenge_id in challenge.prerequisites:
                dependencies.append({
                    'id': challenge.id,
                    'title': challenge.title,
                    'module_id': challenge.module_id
                })
        
        return dependencies
    
    def validate_prerequisite_update(self, challenge_id, new_prerequisites):
        """Validate that updating prerequisites won't create circular dependencies"""
        # Temporarily update prerequisites
        challenge = Challenge.find_by_id(challenge_id)
        if not challenge:
            return False, "Challenge not found"
        
        original_prerequisites = challenge.prerequisites.copy()
        challenge.prerequisites = new_prerequisites
        
        # Check for circular dependencies
        is_valid, error = self.validate_prerequisite_chain(challenge_id)
        
        # Restore original prerequisites
        challenge.prerequisites = original_prerequisites
        
        return is_valid, error if not is_valid else None
    
    def get_prerequisite_statistics(self):
        """Get statistics about prerequisites across all challenges"""
        all_challenges = Challenge.get_all_challenges()
        
        stats = {
            'total_challenges': len(all_challenges),
            'challenges_with_prerequisites': 0,
            'average_prerequisites': 0,
            'max_prerequisites': 0,
            'prerequisite_distribution': {},
            'circular_dependencies': []
        }
        
        total_prerequisites = 0
        
        for challenge in all_challenges:
            prereq_count = len(challenge.prerequisites) if challenge.prerequisites else 0
            
            if prereq_count > 0:
                stats['challenges_with_prerequisites'] += 1
                total_prerequisites += prereq_count
                stats['max_prerequisites'] = max(stats['max_prerequisites'], prereq_count)
                
                # Distribution
                if prereq_count not in stats['prerequisite_distribution']:
                    stats['prerequisite_distribution'][prereq_count] = 0
                stats['prerequisite_distribution'][prereq_count] += 1
            
            # Check for circular dependencies
            is_valid, _ = self.validate_prerequisite_chain(challenge.id)
            if not is_valid:
                stats['circular_dependencies'].append(challenge.id)
        
        if stats['challenges_with_prerequisites'] > 0:
            stats['average_prerequisites'] = round(total_prerequisites / stats['challenges_with_prerequisites'], 2)
        
        return stats

# Global service instance
prerequisite_service = PrerequisiteService()