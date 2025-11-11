#!/usr/bin/env python3
"""
createModule.py - Create a new RNBO module for Percussa SSP/XMX

This script creates a new module by:
1. Collecting module information from the user
2. Copying the template files
3. Performing placeholder substitution
4. Updating the modules CMakeLists.txt

Compatible with Windows, macOS, and Linux.
"""

import os
import sys
import shutil
import re
import argparse
from pathlib import Path
from typing import Dict, Optional


def validate_module_id(module_id: str) -> bool:
    """Validate that module_id is suitable for filename and C++ class name"""
    if not module_id:
        return False
    
    # Check length (should be 4 characters as mentioned in docs)
    if len(module_id) != 4:
        print(f"Error: Module ID must be exactly 4 characters (got {len(module_id)})")
        return False
    
    # Check it's alphanumeric and starts with letter (C++ class name requirement)
    if not module_id.isalnum():
        print("Error: Module ID must be alphanumeric")
        return False
    
    if not module_id[0].isalpha():
        print("Error: Module ID must start with a letter")
        return False
    
    # Check it's uppercase (convention from existing code)
    if module_id != module_id.upper():
        print("Error: Module ID should be uppercase")
        return False
    
    return True


def collect_module_info(args: Optional[argparse.Namespace] = None) -> Dict[str, str]:
    """Collect module information from user or command line args"""
    
    if args and args.module_id:
        # Non-interactive mode
        if not validate_module_id(args.module_id):
            sys.exit(1)
        
        return {
            '__MOD__': args.module_id,
            '__NAME__': args.name or args.module_id,
            '__DESCRIPTION__': args.description or args.name or args.module_id,
            '__BRAND__': args.brand or "YourBrand",
            '__AUTHOR__': args.author or "Unknown",
            '__EMAIL__': args.email or "unknown@example.com",
            '__URL__': args.website or "https://example.com"
        }
    
    # Interactive mode
    print("Creating new RNBO module for Percussa SSP/XMX")
    print("=" * 50)
    
    # Module ID
    while True:
        module_id = input("Module ID (4 uppercase letters/numbers, starts with letter): ").strip()
        if validate_module_id(module_id):
            break
    
    # Other information
    name = input(f"Module Name [{module_id}]: ").strip() or module_id
    description = input(f"Description [{name}]: ").strip() or name
    brand = input("Brand/Company [YourBrand]: ").strip() or "YourBrand"
    author = input("Author Name: ").strip() or "Unknown"
    email = input("Email: ").strip() or "unknown@example.com"
    website = input("Website: ").strip() or "https://example.com"
    
    return {
        '__MOD__': module_id,
        '__NAME__': name,
        '__DESCRIPTION__': description,
        '__BRAND__': brand,
        '__AUTHOR__': author,
        '__EMAIL__': email,
        '__URL__': website
    }


def substitute_in_file(file_path: Path, substitutions: Dict[str, str]) -> None:
    """Perform placeholder substitution in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Perform substitutions
        for placeholder, value in substitutions.items():
            content = content.replace(placeholder, value)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    except UnicodeDecodeError:
        # Skip binary files
        print(f"Skipping binary file: {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")


def copy_and_substitute(template_dir: Path, target_dir: Path, substitutions: Dict[str, str]) -> None:
    """Copy template directory and perform substitutions"""
    if target_dir.exists():
        print(f"Error: Target directory {target_dir} already exists!")
        sys.exit(1)
    
    # Copy template
    print(f"Copying template from {template_dir} to {target_dir}")
    shutil.copytree(template_dir, target_dir)
    
    # Create RNBO export directory structure
    module_id = substitutions['__MOD__']
    rnbo_dir = target_dir / f"{module_id}-rnbo"
    rnbo_dir.mkdir(exist_ok=True)
    print(f"Created RNBO export directory: {rnbo_dir}")
    
    # Perform substitutions in all files
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            file_path = Path(root) / file
            substitute_in_file(file_path, substitutions)
    
    print(f"Template copied and processed successfully")


def update_modules_cmake(modules_dir: Path, module_id: str) -> None:
    """Add the new module to modules/CMakeLists.txt"""
    cmake_file = modules_dir / "CMakeLists.txt"
    
    if not cmake_file.exists():
        print(f"Error: {cmake_file} not found!")
        sys.exit(1)
    
    # Check if module is already added
    with open(cmake_file, 'r') as f:
        content = f.read()
    
    add_line = f"add_subdirectory({module_id})"
    if add_line in content:
        print(f"Module {module_id} already exists in CMakeLists.txt")
        return
    
    # Add the subdirectory line
    with open(cmake_file, 'a') as f:
        f.write(f"{add_line}\n")
    
    print(f"Added {module_id} to modules/CMakeLists.txt")


def print_next_steps(module_id: str) -> None:
    """Print instructions for the user"""
    print("\n" + "=" * 60)
    print("Module created successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print(f"1. Export your RNBO code to:")
    print(f"   modules{os.sep}{module_id}{os.sep}{module_id}-rnbo{os.sep}")
    print("\n2. Build the module:")
    print("   cmake --fresh -B build.ssp -DCMAKE_BUILD_TYPE=Release -DCMAKE_TOOLCHAIN_FILE=./xcSSP.cmake && cmake --build build.ssp ")
    print("   cmake --fresh -B build.xmx -DCMAKE_BUILD_TYPE=Release -DCMAKE_TOOLCHAIN_FILE=./xcXMX.cmake && cmake --build build.xmx ")
    print("   cmake --fresh -B build && cmake --build build ")
    print("\nFor more details, see docs/BUILDING.md")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Create a new RNBO module for Percussa SSP/XMX",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python createModule.py
  
  # Non-interactive mode
  python createModule.py TEST --name "Test Module" --author "Your Name"
  
  # Minimal non-interactive
  python createModule.py VERB --description "Reverb Effect"
        """
    )
    
    parser.add_argument('module_id', nargs='?', 
                       help='4-character module ID (uppercase, starts with letter)')
    parser.add_argument('--name', help='Module display name')
    parser.add_argument('--description', help='Module description')
    parser.add_argument('--brand', help='Brand/Company name')
    parser.add_argument('--author', help='Author name')
    parser.add_argument('--email', help='Author email')
    parser.add_argument('--website', help='Author website')
    
    args = parser.parse_args()
    
    # Get project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    template_dir = project_root / "template" / "module"
    modules_dir = project_root / "modules"
    
    # Validate directories exist
    if not template_dir.exists():
        print(f"Error: Template directory {template_dir} not found!")
        sys.exit(1)
    
    if not modules_dir.exists():
        print(f"Error: Modules directory {modules_dir} not found!")
        sys.exit(1)
    
    # Collect information
    substitutions = collect_module_info(args)
    module_id = substitutions['__MOD__']
    
    # Create target directory
    target_dir = modules_dir / module_id
    
    # Copy and process template
    copy_and_substitute(template_dir, target_dir, substitutions)
    
    # Update CMakeLists.txt
    update_modules_cmake(modules_dir, module_id)
    
    # Print next steps
    print_next_steps(module_id)


if __name__ == "__main__":
    main()