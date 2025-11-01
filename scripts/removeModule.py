#!/usr/bin/env python3
"""
removeModule.py - Remove an RNBO module from Percussa SSP/XMX project

This script removes a module by:
1. Confirming the user wants to delete the module (destructive operation)
2. Removing the module directory from modules/
3. Removing the add_subdirectory line from modules/CMakeLists.txt

Compatible with Windows, macOS, and Linux.
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from typing import List


def list_available_modules(modules_dir: Path) -> List[str]:
    """List all available modules in the modules directory"""
    modules = []
    for item in modules_dir.iterdir():
        if item.is_dir() and item.name not in ['common', 'inc', '.git']:
            modules.append(item.name)
    return sorted(modules)


def confirm_removal(module_id: str, module_dir: Path, force: bool = False) -> bool:
    """Confirm with user that they want to remove the module"""
    if force:
        return True
    
    print(f"\nWARNING: This will permanently delete module '{module_id}'")
    print(f"Directory to be removed: {module_dir}")
    print("CMakeLists.txt entry will also be removed")
    print("\nThis action cannot be undone!")
    
    while True:
        response = input(f"\nAre you sure you want to remove module '{module_id}'? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Please enter 'yes' or 'no'")


def remove_module_directory(module_dir: Path, module_id: str) -> bool:
    """Remove the module directory"""
    try:
        if module_dir.exists():
            print(f"Removing module directory: {module_dir}")
            shutil.rmtree(module_dir)
            print(f"Successfully removed directory for module '{module_id}'")
            return True
        else:
            print(f"Warning: Module directory {module_dir} does not exist")
            return False
    except Exception as e:
        print(f"Error removing directory {module_dir}: {e}")
        return False


def remove_from_cmake(cmake_file: Path, module_id: str) -> bool:
    """Remove the add_subdirectory line from CMakeLists.txt"""
    try:
        if not cmake_file.exists():
            print(f"Warning: CMakeLists.txt not found: {cmake_file}")
            return False
        
        # Read current content
        with open(cmake_file, 'r') as f:
            lines = f.readlines()
        
        # Find and remove the line
        target_line = f"add_subdirectory({module_id})\n"
        target_line_alt = f"add_subdirectory({module_id})"  # without newline
        
        original_count = len(lines)
        lines = [line for line in lines if line.strip() != target_line.strip()]
        
        if len(lines) < original_count:
            # Write back the modified content
            with open(cmake_file, 'w') as f:
                f.writelines(lines)
            print(f"Removed '{module_id}' from CMakeLists.txt")
            return True
        else:
            print(f"Warning: Module '{module_id}' was not found in CMakeLists.txt")
            return False
            
    except Exception as e:
        print(f"Error updating CMakeLists.txt: {e}")
        return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Remove an RNBO module from Percussa SSP/XMX project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode - list modules and choose
  python removeModule.py
  
  # Remove specific module with confirmation
  python removeModule.py TEST
  
  # Remove module without confirmation (dangerous!)
  python removeModule.py TEST --force
  
WARNING: This operation is destructive and cannot be undone!
        """
    )
    
    parser.add_argument('module_id', nargs='?', 
                       help='Module ID to remove')
    parser.add_argument('--force', action='store_true',
                       help='Remove without confirmation (dangerous!)')
    parser.add_argument('--list', action='store_true',
                       help='List available modules and exit')
    
    args = parser.parse_args()
    
    # Get project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    modules_dir = project_root / "modules"
    cmake_file = modules_dir / "CMakeLists.txt"
    
    # Validate directories exist
    if not modules_dir.exists():
        print(f"Error: Modules directory {modules_dir} not found!")
        sys.exit(1)
    
    # List available modules
    available_modules = list_available_modules(modules_dir)
    
    if args.list:
        print("Available modules:")
        if available_modules:
            for module in available_modules:
                print(f"  - {module}")
        else:
            print("  (no modules found)")
        sys.exit(0)
    
    # Determine which module to remove
    module_id = args.module_id
    
    if not module_id:
        # Interactive mode
        if not available_modules:
            print("No modules found to remove.")
            sys.exit(0)
        
        print("Available modules:")
        for i, module in enumerate(available_modules, 1):
            print(f"  {i}. {module}")
        
        while True:
            try:
                choice = input(f"\nSelect module to remove (1-{len(available_modules)}) or 'q' to quit: ").strip()
                if choice.lower() == 'q':
                    print("Cancelled.")
                    sys.exit(0)
                
                index = int(choice) - 1
                if 0 <= index < len(available_modules):
                    module_id = available_modules[index]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(available_modules)}")
            except ValueError:
                print("Please enter a valid number or 'q' to quit")
    
    # Validate module exists
    module_dir = modules_dir / module_id
    if not module_dir.exists():
        print(f"Error: Module '{module_id}' not found in {modules_dir}")
        if available_modules:
            print(f"Available modules: {', '.join(available_modules)}")
        sys.exit(1)
    
    # Confirm removal
    if not confirm_removal(module_id, module_dir, args.force):
        print("Removal cancelled.")
        sys.exit(0)
    
    # Perform removal
    print(f"\nRemoving module '{module_id}'...")
    
    success = True
    
    # Remove from CMakeLists.txt first (safer to fail here)
    if not remove_from_cmake(cmake_file, module_id):
        success = False
    
    # Remove directory
    if not remove_module_directory(module_dir, module_id):
        success = False
    
    # Summary
    if success:
        print(f"\nModule '{module_id}' has been successfully removed!")
        print("\nYou may want to clean your build directory:")
        if os.name == 'nt':  # Windows
            print("   rmdir /s build*")
        else:  # Unix-like (macOS, Linux)
            print("   rm -rf build*/")
    else:
        print(f"\nModule '{module_id}' was partially removed. Please check manually.")
        sys.exit(1)


if __name__ == "__main__":
    main()