"""
Challenge Configuration Service for different simulation types
"""

from models.challenge import SimulationType, DifficultyLevel

class ChallengeConfigService:
    """Service for managing challenge configurations"""
    
    def __init__(self):
        self.default_configs = self._get_default_configs()
    
    def _get_default_configs(self):
        """Get default configurations for each simulation type"""
        return {
            SimulationType.VISUAL.value: {
                "canvas_size": {"width": 800, "height": 600},
                "interactive_elements": True,
                "drag_drop": True,
                "animations": True,
                "zoom_enabled": True,
                "grid_enabled": True,
                "tools": ["select", "draw", "text", "shapes"],
                "color_scheme": "default"
            },
            
            SimulationType.NETWORK.value: {
                "topology_type": "custom",
                "max_devices": 20,
                "device_types": ["router", "switch", "firewall", "server", "workstation"],
                "connection_types": ["ethernet", "serial", "wireless"],
                "packet_simulation": True,
                "real_time_monitoring": True,
                "protocol_support": ["tcp", "udp", "icmp", "http", "https"],
                "vlan_support": True,
                "routing_protocols": ["static", "rip", "ospf"]
            },
            
            SimulationType.TERMINAL.value: {
                "shell_type": "bash",
                "filesystem": "simulated",
                "available_commands": [
                    "ls", "cd", "pwd", "cat", "grep", "find", "ps", "netstat",
                    "ping", "nmap", "ssh", "scp", "wget", "curl", "iptables"
                ],
                "command_history": True,
                "tab_completion": True,
                "color_output": True,
                "max_session_time": 3600,
                "working_directory": "/home/student",
                "restricted_paths": ["/etc/shadow", "/root"]
            },
            
            SimulationType.LAB.value: {
                "environment_type": "docker",
                "base_image": "ubuntu:20.04",
                "cpu_limit": "1",
                "memory_limit": "512m",
                "network_isolation": True,
                "internet_access": False,
                "persistent_storage": False,
                "session_timeout": 7200,
                "auto_cleanup": True,
                "pre_installed_tools": [
                    "nmap", "wireshark", "metasploit", "burpsuite", "john"
                ]
            },
            
            SimulationType.QUIZ.value: {
                "question_types": ["multiple_choice", "true_false", "fill_blank", "drag_drop"],
                "randomize_questions": True,
                "randomize_answers": True,
                "show_progress": True,
                "allow_review": True,
                "immediate_feedback": False,
                "passing_score": 70,
                "max_attempts": 3,
                "time_per_question": 60
            },
            
            SimulationType.SCENARIO.value: {
                "story_mode": True,
                "branching_paths": True,
                "character_interactions": True,
                "inventory_system": False,
                "decision_points": True,
                "multimedia_support": True,
                "progress_checkpoints": True,
                "multiple_endings": False,
                "difficulty_scaling": True
            }
        }
    
    def get_config_template(self, simulation_type):
        """Get configuration template for a simulation type"""
        return self.default_configs.get(simulation_type, {})
    
    def validate_config(self, simulation_type, config):
        """Validate configuration for a simulation type"""
        template = self.get_config_template(simulation_type)
        if not template:
            return False, f"Unknown simulation type: {simulation_type}"
        
        errors = []
        
        # Check for required fields based on simulation type
        if simulation_type == SimulationType.NETWORK.value:
            if config.get("max_devices", 0) > 50:
                errors.append("max_devices cannot exceed 50")
            
            if "device_types" in config and not isinstance(config["device_types"], list):
                errors.append("device_types must be a list")
        
        elif simulation_type == SimulationType.TERMINAL.value:
            if "available_commands" in config and not isinstance(config["available_commands"], list):
                errors.append("available_commands must be a list")
            
            if config.get("max_session_time", 0) > 7200:
                errors.append("max_session_time cannot exceed 2 hours")
        
        elif simulation_type == SimulationType.LAB.value:
            memory_limit = config.get("memory_limit", "512m")
            if isinstance(memory_limit, str) and memory_limit.endswith("m"):
                try:
                    memory_mb = int(memory_limit[:-1])
                    if memory_mb > 2048:
                        errors.append("memory_limit cannot exceed 2048m")
                except ValueError:
                    errors.append("Invalid memory_limit format")
        
        elif simulation_type == SimulationType.QUIZ.value:
            passing_score = config.get("passing_score", 70)
            if not isinstance(passing_score, (int, float)) or passing_score < 0 or passing_score > 100:
                errors.append("passing_score must be between 0 and 100")
        
        return len(errors) == 0, errors
    
    def merge_config(self, simulation_type, custom_config):
        """Merge custom config with default template"""
        template = self.get_config_template(simulation_type)
        merged_config = template.copy()
        
        if custom_config:
            merged_config.update(custom_config)
        
        return merged_config
    
    def get_difficulty_adjustments(self, difficulty):
        """Get configuration adjustments based on difficulty level"""
        adjustments = {
            DifficultyLevel.BEGINNER.value: {
                "hints_available": True,
                "time_multiplier": 1.5,
                "simplified_interface": True,
                "guided_mode": True
            },
            DifficultyLevel.INTERMEDIATE.value: {
                "hints_available": True,
                "time_multiplier": 1.2,
                "simplified_interface": False,
                "guided_mode": False
            },
            DifficultyLevel.ADVANCED.value: {
                "hints_available": False,
                "time_multiplier": 1.0,
                "simplified_interface": False,
                "guided_mode": False
            },
            DifficultyLevel.EXPERT.value: {
                "hints_available": False,
                "time_multiplier": 0.8,
                "simplified_interface": False,
                "guided_mode": False,
                "additional_constraints": True
            }
        }
        
        return adjustments.get(difficulty, adjustments[DifficultyLevel.BEGINNER.value])
    
    def generate_config_for_challenge(self, simulation_type, difficulty, custom_config=None):
        """Generate complete configuration for a challenge"""
        # Start with default template
        config = self.get_config_template(simulation_type)
        
        # Apply difficulty adjustments
        difficulty_adjustments = self.get_difficulty_adjustments(difficulty)
        config.update(difficulty_adjustments)
        
        # Apply custom configuration
        if custom_config:
            config.update(custom_config)
        
        # Validate the final configuration
        is_valid, errors = self.validate_config(simulation_type, config)
        if not is_valid:
            raise ValueError(f"Invalid configuration: {', '.join(errors)}")
        
        return config
    
    def get_simulation_requirements(self, simulation_type):
        """Get technical requirements for a simulation type"""
        requirements = {
            SimulationType.VISUAL.value: {
                "browser_features": ["canvas", "svg", "css3"],
                "javascript_required": True,
                "minimum_screen_width": 800,
                "mobile_compatible": True
            },
            SimulationType.NETWORK.value: {
                "browser_features": ["canvas", "webgl", "websockets"],
                "javascript_required": True,
                "minimum_screen_width": 1024,
                "mobile_compatible": False,
                "performance_intensive": True
            },
            SimulationType.TERMINAL.value: {
                "browser_features": ["websockets", "local_storage"],
                "javascript_required": True,
                "minimum_screen_width": 600,
                "mobile_compatible": True,
                "keyboard_required": True
            },
            SimulationType.LAB.value: {
                "browser_features": ["websockets", "webrtc"],
                "javascript_required": True,
                "minimum_screen_width": 1024,
                "mobile_compatible": False,
                "server_resources": "high",
                "security_isolation": True
            },
            SimulationType.QUIZ.value: {
                "browser_features": ["local_storage"],
                "javascript_required": True,
                "minimum_screen_width": 400,
                "mobile_compatible": True,
                "offline_capable": True
            },
            SimulationType.SCENARIO.value: {
                "browser_features": ["audio", "video", "local_storage"],
                "javascript_required": True,
                "minimum_screen_width": 600,
                "mobile_compatible": True,
                "multimedia_support": True
            }
        }
        
        return requirements.get(simulation_type, {})

# Global service instance
challenge_config_service = ChallengeConfigService()