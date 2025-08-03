#!/usr/bin/env python3
"""
Test script for enhanced Challenge model and services
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.challenge import Challenge, DifficultyLevel, SimulationType
from services.challenge_config_service import challenge_config_service
from services.prerequisite_service import prerequisite_service
from database import setup_database, seed_if_empty

def test_enhanced_challenges():
    """Test enhanced Challenge model and related services"""
    print("Testing Enhanced Challenge System...")
    
    # Setup database
    setup_database()
    seed_if_empty()
    
    # Test 1: Test Challenge model creation with advanced properties
    print("\n1. Testing enhanced Challenge model creation...")
    
    try:
        # Create a visual challenge
        visual_challenge = Challenge.create_challenge(
            id="test_visual_1",
            module_id="m1",
            title="Network Diagram Challenge",
            description="Create a network topology diagram",
            tasks=["Draw network", "Add devices", "Configure connections"],
            difficulty=DifficultyLevel.BEGINNER.value,
            simulation_type=SimulationType.VISUAL.value,
            simulation_config={
                "canvas_size": {"width": 1000, "height": 700},
                "tools": ["router", "switch", "cable"]
            },
            points=100,
            time_limit=1800,  # 30 minutes
            tags=["networking", "topology", "visual"],
            estimated_duration=25
        )
        print(f"   ✓ Created visual challenge: {visual_challenge.title}")
        
        # Create a terminal challenge
        terminal_challenge = Challenge.create_challenge(
            id="test_terminal_1",
            module_id="m2",
            title="Command Line Security",
            description="Use command line tools for security analysis",
            tasks=["Run nmap scan", "Analyze results", "Generate report"],
            difficulty=DifficultyLevel.INTERMEDIATE.value,
            simulation_type=SimulationType.TERMINAL.value,
            simulation_config={
                "available_commands": ["nmap", "netstat", "ps", "grep"],
                "working_directory": "/home/student"
            },
            points=150,
            prerequisites=["test_visual_1"],
            tags=["terminal", "nmap", "security"],
            estimated_duration=45
        )
        print(f"   ✓ Created terminal challenge: {terminal_challenge.title}")
        
    except Exception as e:
        print(f"   ✗ Challenge creation failed: {e}")
        return False
    
    # Test 2: Test difficulty and simulation type validation
    print("\n2. Testing validation...")
    
    # Test invalid difficulty
    try:
        Challenge.create_challenge(
            id="invalid_diff",
            module_id="m1",
            title="Invalid Challenge",
            difficulty="invalid_difficulty"
        )
        print("   ✗ Invalid difficulty validation failed")
        return False
    except ValueError:
        print("   ✓ Invalid difficulty correctly rejected")
    
    # Test invalid simulation type
    try:
        Challenge.create_challenge(
            id="invalid_sim",
            module_id="m1", 
            title="Invalid Challenge",
            simulation_type="invalid_type"
        )
        print("   ✗ Invalid simulation type validation failed")
        return False
    except ValueError:
        print("   ✓ Invalid simulation type correctly rejected")
    
    # Test duplicate ID
    try:
        Challenge.create_challenge(
            id="test_visual_1",  # Already exists
            module_id="m1",
            title="Duplicate Challenge"
        )
        print("   ✗ Duplicate ID validation failed")
        return False
    except ValueError:
        print("   ✓ Duplicate ID correctly rejected")
    
    # Test 3: Test challenge retrieval methods
    print("\n3. Testing challenge retrieval...")
    
    # Find by ID
    found_challenge = Challenge.find_by_id("test_visual_1")
    if found_challenge and found_challenge.title == "Network Diagram Challenge":
        print("   ✓ Challenge found by ID")
    else:
        print("   ✗ Challenge lookup by ID failed")
        return False
    
    # Find by module
    module_challenges = Challenge.find_by_module("m1")
    if len(module_challenges) >= 1:
        print(f"   ✓ Found {len(module_challenges)} challenges in module m1")
    else:
        print("   ✗ Module challenge lookup failed")
        return False
    
    # Find by difficulty
    beginner_challenges = Challenge.find_by_difficulty(DifficultyLevel.BEGINNER.value)
    if len(beginner_challenges) >= 1:
        print(f"   ✓ Found {len(beginner_challenges)} beginner challenges")
    else:
        print("   ✗ Difficulty challenge lookup failed")
        return False
    
    # Find by simulation type
    visual_challenges = Challenge.find_by_simulation_type(SimulationType.VISUAL.value)
    if len(visual_challenges) >= 1:
        print(f"   ✓ Found {len(visual_challenges)} visual challenges")
    else:
        print("   ✗ Simulation type challenge lookup failed")
        return False
    
    # Test 4: Test challenge configuration service
    print("\n4. Testing challenge configuration service...")
    
    # Get config template
    visual_template = challenge_config_service.get_config_template(SimulationType.VISUAL.value)
    if "canvas_size" in visual_template and "interactive_elements" in visual_template:
        print("   ✓ Visual simulation config template retrieved")
    else:
        print("   ✗ Visual simulation config template incomplete")
        return False
    
    # Test config validation
    valid_config = {"canvas_size": {"width": 800, "height": 600}}
    is_valid, errors = challenge_config_service.validate_config(SimulationType.VISUAL.value, valid_config)
    if is_valid:
        print("   ✓ Valid configuration accepted")
    else:
        print(f"   ✗ Valid configuration rejected: {errors}")
        return False
    
    # Test config merging
    merged_config = challenge_config_service.merge_config(
        SimulationType.TERMINAL.value,
        {"custom_prompt": "student@security:~$ "}
    )
    if "available_commands" in merged_config and "custom_prompt" in merged_config:
        print("   ✓ Configuration merging works correctly")
    else:
        print("   ✗ Configuration merging failed")
        return False
    
    # Test 5: Test prerequisite service
    print("\n5. Testing prerequisite service...")
    
    # Create a user for testing (mock user ID)
    test_user_id = 1
    
    # Test prerequisite validation (terminal challenge requires visual challenge)
    can_access, missing = prerequisite_service.validate_prerequisites("test_terminal_1", test_user_id)
    if not can_access and len(missing) == 1:
        print("   ✓ Prerequisite validation correctly blocks access")
        print(f"   ✓ Missing prerequisite: {missing[0]['title']}")
    else:
        print("   ✗ Prerequisite validation failed")
        return False
    
    # Test available challenges
    available, locked = prerequisite_service.get_available_challenges(test_user_id, "m1")
    if len(available) > 0 and len(locked) >= 0:
        print(f"   ✓ Found {len(available)} available and {len(locked)} locked challenges")
    else:
        print("   ✗ Available challenges lookup failed")
        return False
    
    # Test learning path suggestion
    learning_path = prerequisite_service.suggest_learning_path(test_user_id, "test_terminal_1")
    if len(learning_path) >= 1:
        print(f"   ✓ Learning path suggested with {len(learning_path)} steps")
        print(f"   ✓ First step: {learning_path[0]['title']}")
    else:
        print("   ✗ Learning path suggestion failed")
        return False
    
    # Test 6: Test challenge properties and methods
    print("\n6. Testing challenge properties and methods...")
    
    # Test difficulty info
    difficulty_info = visual_challenge.get_difficulty_info()
    if "name" in difficulty_info and "multiplier" in difficulty_info:
        print(f"   ✓ Difficulty info: {difficulty_info['name']} (x{difficulty_info['multiplier']})")
    else:
        print("   ✗ Difficulty info incomplete")
        return False
    
    # Test simulation info
    simulation_info = visual_challenge.get_simulation_info()
    if "name" in simulation_info and "icon" in simulation_info:
        print(f"   ✓ Simulation info: {simulation_info['name']} {simulation_info['icon']}")
    else:
        print("   ✗ Simulation info incomplete")
        return False
    
    # Test hints
    visual_challenge.add_hint("Start by placing a router in the center", "text")
    visual_challenge.add_hint("Connect devices using appropriate cables", "text")
    
    if len(visual_challenge.hints) == 2:
        print("   ✓ Hints added successfully")
        
        first_hint = visual_challenge.get_hint(0)
        if first_hint and "router" in first_hint["content"]:
            print("   ✓ Hint retrieval works correctly")
        else:
            print("   ✗ Hint retrieval failed")
            return False
    else:
        print("   ✗ Hint addition failed")
        return False
    
    # Test points calculation
    base_points = visual_challenge.calculate_points(completion_time=1200, hints_used=1)
    if base_points > 0:
        print(f"   ✓ Points calculation: {base_points} points")
    else:
        print("   ✗ Points calculation failed")
        return False
    
    # Test 7: Test challenge serialization
    print("\n7. Testing challenge serialization...")
    
    # Basic serialization
    challenge_dict = visual_challenge.to_dict()
    expected_fields = ['id', 'title', 'difficulty', 'simulation_type', 'points', 'tasks']
    
    if all(field in challenge_dict for field in expected_fields):
        print("   ✓ Basic challenge serialization successful")
    else:
        print("   ✗ Basic challenge serialization incomplete")
        return False
    
    # Serialization with hints and solution
    full_dict = visual_challenge.to_dict(include_hints=True, include_solution=True)
    if "hints" in full_dict and "solution" in full_dict:
        print("   ✓ Full challenge serialization successful")
    else:
        print("   ✗ Full challenge serialization incomplete")
        return False
    
    # Test 8: Test challenge updates
    print("\n8. Testing challenge updates...")
    
    # Update challenge properties
    original_title = visual_challenge.title
    visual_challenge.title = "Updated Network Diagram Challenge"
    visual_challenge.description = "Updated description with more details"
    visual_challenge.points = 120
    visual_challenge.save()
    
    # Reload from database
    updated_challenge = Challenge.find_by_id("test_visual_1")
    if (updated_challenge.title == "Updated Network Diagram Challenge" and
        updated_challenge.points == 120):
        print("   ✓ Challenge update successful")
    else:
        print("   ✗ Challenge update failed")
        return False
    
    # Test 9: Test simulation type configurations
    print("\n9. Testing simulation type configurations...")
    
    simulation_types = [
        SimulationType.VISUAL.value,
        SimulationType.NETWORK.value,
        SimulationType.TERMINAL.value,
        SimulationType.LAB.value,
        SimulationType.QUIZ.value,
        SimulationType.SCENARIO.value
    ]
    
    for sim_type in simulation_types:
        config = challenge_config_service.get_config_template(sim_type)
        requirements = challenge_config_service.get_simulation_requirements(sim_type)
        
        if config and requirements:
            print(f"   ✓ {sim_type}: Config and requirements available")
        else:
            print(f"   ✗ {sim_type}: Missing config or requirements")
            return False
    
    # Test 10: Test prerequisite statistics
    print("\n10. Testing prerequisite statistics...")
    
    stats = prerequisite_service.get_prerequisite_statistics()
    expected_stats = ['total_challenges', 'challenges_with_prerequisites', 'average_prerequisites']
    
    if all(key in stats for key in expected_stats):
        print("   ✓ Prerequisite statistics generated")
        print(f"   ✓ Total challenges: {stats['total_challenges']}")
        print(f"   ✓ With prerequisites: {stats['challenges_with_prerequisites']}")
        print(f"   ✓ Average prerequisites: {stats['average_prerequisites']}")
    else:
        print("   ✗ Prerequisite statistics incomplete")
        return False
    
    print("\n✅ Enhanced Challenge system test completed successfully!")
    
    # Final summary
    print(f"\n📊 Enhanced Challenge System Summary:")
    print(f"   Difficulty levels: {len(DifficultyLevel)} types")
    print(f"   Simulation types: {len(SimulationType)} types")
    print(f"   Challenges created: 2")
    print(f"   Configuration templates: {len(simulation_types)}")
    print(f"   Prerequisite validation: ✓")
    print(f"   Learning path generation: ✓")
    
    return True

if __name__ == "__main__":
    success = test_enhanced_challenges()
    sys.exit(0 if success else 1)