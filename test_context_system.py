#!/usr/bin/env python3
"""
Test script for the enhanced context management system.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported successfully."""
    try:
        from tools.context_manager import ContextManagerTool
        print("[PASS] ContextManagerTool imported successfully")
        
        from agent import Agent
        print("[PASS] Agent imported successfully")
        
        from tools.chat import ChatTool
        print("[PASS] ChatTool imported successfully")
        
        return True
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False

def test_context_manager():
    """Test the ContextManagerTool functionality."""
    try:
        from tools.context_manager import ContextManagerTool
        
        cm = ContextManagerTool()
        
        # Test setting user profile
        result = cm.execute('set_profile', key='name', value='TestUser')
        print(f"[PASS] Set profile: {result}")
        
        # Test getting user profile
        profile = cm.execute('get_profile', key='name')
        print(f"[PASS] Got profile: {profile}")
        
        # Test adding topics
        result = cm.execute('add_topic', topic='Python Programming')
        print(f"[PASS] Added topic: {result}")
        
        # Test getting topics
        topics = cm.execute('get_topics')
        print(f"[PASS] Got topics: {topics}")
        
        # Test enhanced context
        enhanced = cm.execute('get_enhanced_context')
        print(f"[PASS] Enhanced context keys: {list(enhanced.keys())}")
        
        # Test system prompt generation
        prompt = cm.generate_enhanced_system_prompt()
        print(f"[PASS] Generated enhanced prompt (length: {len(prompt)} chars)")
        
        return True
    except Exception as e:
        print(f"[FAIL] Context manager test failed: {e}")
        return False

def test_agent_registration():
    """Test that the agent can register all tools including the new ContextManagerTool."""
    try:
        from agent import Agent
        
        agent = Agent()
        
        # Check if ContextManagerTool is registered
        if 'context_manager' in agent.tools:
            print("[PASS] ContextManagerTool registered in agent")
        else:
            print(f"[FAIL] ContextManagerTool not found in agent tools")
            print(f"Available tools: {list(agent.tools.keys())}")
            return False
        
        # Test enhanced context method
        enhanced_context = agent.get_enhanced_chat_context()
        print(f"[PASS] Agent enhanced context method works: {list(enhanced_context.keys())}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Agent registration test failed: {e}")
        return False

def test_chat_enhancements():
    """Test that ChatTool has the enhanced execute method."""
    try:
        from tools.chat import ChatTool
        
        chat_tool = ChatTool()
        
        # Check if the method signature includes the new parameter
        import inspect
        sig = inspect.signature(chat_tool.execute)
        params = list(sig.parameters.keys())
        
        if 'use_enhanced_context' in params:
            print("[PASS] ChatTool has enhanced context parameter")
        else:
            print(f"[FAIL] ChatTool missing enhanced context parameter. Params: {params}")
            return False
        
        # Check if the helper method exists
        if hasattr(chat_tool, '_extract_and_store_topics'):
            print("[PASS] ChatTool has topic extraction method")
        else:
            print("[FAIL] ChatTool missing topic extraction method")
            return False
        
        return True
    except Exception as e:
        print(f"[FAIL] Chat enhancement test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing Enhanced Context Management System")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Context Manager Test", test_context_manager),
        ("Agent Registration Test", test_agent_registration),
        ("Chat Enhancement Test", test_chat_enhancements)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"Failed: {test_name}")
    
    print(f"\n{'=' * 50}")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("[SUCCESS] All tests passed! Enhanced context system is working.")
    else:
        print("[ERROR] Some tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    main()