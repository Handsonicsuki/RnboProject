#!/usr/bin/env python3
"""
test.py - Create test modules for development and testing

This script creates test modules by:
1. Creating two example modules with different configurations
2. Using createModule.py to generate the modules
3. Providing quick test data for development

Compatible with Windows, macOS, and Linux.
"""

import os
import sys
import subprocess
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory"""
    script_dir = Path(__file__).parent
    return script_dir.parent.parent


def create_test_module(project_root: Path, module_config: dict) -> bool:
    """Create a single test module using createModule.py"""
    create_script = project_root / "scripts" / "createModule.py"
    
    if not create_script.exists():
        print(f"Error: createModule.py not found at {create_script}")
        return False
    
    # Build command line arguments
    cmd = [
        sys.executable, str(create_script),
        module_config['id'],
        "--name", module_config['name'],
        "--description", module_config['description'],
        "--brand", module_config['brand'],
        "--author", module_config['author'],
        "--email", module_config['email'],
        "--website", module_config['website']
    ]
    
    print(f"Creating test module '{module_config['id']}'...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            print(f"Successfully created module '{module_config['id']}'")
            return True
        else:
            print(f"Failed to create module '{module_config['id']}':")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"Error creating module '{module_config['id']}': {e}")
        return False


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Create test modules for development and testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script creates two test modules:
  - TEST: A basic test module
  - VERB: A reverb effect module

These modules are useful for:
  - Testing the build system
  - Examining generated code structure
  - Development and debugging

Examples:
  # Create both test modules
  python test.py
  
  # Clean up afterwards with:
  python removeAll.py --force
        """
    )
    
    args = parser.parse_args()
    
    # Get project root
    project_root = get_project_root()
    
    # Define test module configurations
    test_modules = [
        {
            'id': 'TEST',
            'name': 'Test Module',
            'description': 'Basic test module for development',
            'brand': 'TestBrand',
            'author': 'Test Developer',
            'email': 'test@example.com',
            'website': 'https://test.example.com'
        },
        {
            'id': 'VERB',
            'name': 'Reverb Effect',
            'description': 'Digital reverb processor with multiple algorithms',
            'brand': 'AudioDev',
            'author': 'Audio Engineer',
            'email': 'audio@example.com',
            'website': 'https://audiodev.example.com'
        }
    ]
    
    print("Creating test modules for development...")
    print("=" * 50)
    
    success_count = 0
    total_count = len(test_modules)
    
    for module_config in test_modules:
        if create_test_module(project_root, module_config):
            success_count += 1
        print()  # Empty line for readability
    
    # Summary
    print("=" * 50)
    print(f"Test module creation complete: {success_count}/{total_count} modules created successfully")
    
    if success_count == total_count:
        print("\nTest modules created successfully!")
        print("\nNext steps:")
        print("1. Export RNBO code to:")
        print("   - modules/TEST/TEST-rnbo/")
        print("   - modules/VERB/VERB-rnbo/")
        print("\n2. Build the modules:")
        if os.name == 'nt':  # Windows
            print("   mkdir build")
            print("   cd build")
            print("   cmake ..")
            print("   cmake --build .")
        else:  # Unix-like (macOS, Linux)
            print("   mkdir -p build && cd build")
            print("   cmake ..")
            print("   cmake --build .")
        print("\n3. Clean up test modules when done:")
        print("   python scripts/test/removeAll.py --force")
    else:
        print("\nSome test modules could not be created. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()