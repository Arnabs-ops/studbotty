#!/usr/bin/env python3
"""
Simple test script to verify VizTool functionality
"""

from tools.viz import VizTool
import json
import os

def test_viz_tool():
    # Create sample flashcards
    sample_flashcards = [
        {
            "id": 1,
            "front": "What is photosynthesis?",
            "back": "The process by which plants convert light energy into chemical energy",
            "tags": ["biology", "plants"]
        },
        {
            "id": 2,
            "front": "Capital of France?",
            "back": "Paris",
            "tags": ["geography", "europe"]
        },
        {
            "id": 3,
            "front": "2 + 2 = ?",
            "back": "4",
            "tags": ["math", "basic"]
        }
    ]
    
    # Test the VizTool
    try:
        viz_tool = VizTool()
        
        # Test flashcard visualization
        result = viz_tool.visualize_flashcards(sample_flashcards)
        
        if result:
            print("VizTool test passed successfully!")
            print(f"Generated visualization with {len(sample_flashcards)} flashcards")
            
            # Check if HTML file was created
            if os.path.exists("flashcards_visualization.html"):
                print("HTML visualization file created successfully!")
                return True
            else:
                print("HTML file was not created")
                return False
        else:
            print("VizTool test failed - no result returned")
            return False
            
    except Exception as e:
        print(f"VizTool test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_viz_tool()
    if success:
        print("\n🎉 All tests passed! VizTool is working correctly.")
    else:
        print("\nTests failed! There are issues with the VizTool.")