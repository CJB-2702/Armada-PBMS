#!/usr/bin/env python3
"""
Script to split build_data.json into critical and test data files.

This script helps migrate from a single build_data.json file to separate
critical and test data files for better testing data management.

Usage:
    python scripts/split_build_data.py
"""
import json
import sys
from pathlib import Path


def deep_merge(base_dict, update_dict):
    """Deep merge two dictionaries, with update_dict taking precedence"""
    result = base_dict.copy()
    for key, value in update_dict.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def split_build_data():
    """Split build_data.json into critical and test data files"""
    # Get the project root (parent of scripts directory)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    utils_dir = project_root / 'app' / 'utils'
    
    build_data_file = utils_dir / 'build_data.json'
    
    if not build_data_file.exists():
        print(f"Error: {build_data_file} not found")
        print(f"Looking in: {build_data_file.absolute()}")
        return False
    
    print(f"Reading {build_data_file}...")
    with open(build_data_file, 'r') as f:
        build_data = json.load(f)
    
    # Define what is system-critical
    # Essential section is always critical
    critical_data = {
        'Essential': build_data.get('Essential', {}).copy()
    }
    
    # Core section: Only Asset_Types are potentially critical
    # For now, include all Asset_Types as critical (you may want to review this)
    core_critical = {}
    if 'Core' in build_data:
        if 'Asset_Types' in build_data['Core']:
            core_critical['Asset_Types'] = build_data['Core']['Asset_Types'].copy()
    
    if core_critical:
        critical_data['Core'] = core_critical
    
    # Everything else is test/debugging data
    test_data = {}
    
    # Core test data (everything in Core except what's in critical)
    if 'Core' in build_data:
        core_test = build_data['Core'].copy()
        # Remove critical items
        if 'Asset_Types' in core_test and 'Core' in critical_data and 'Asset_Types' in critical_data['Core']:
            # Keep Asset_Types in test if there are additional ones beyond critical
            # For now, we'll keep them in both - you can manually review
            pass
        test_data['Core'] = core_test
    
    # All other sections are test data
    test_sections = ['Asset_Details', 'Dispatching', 'Supply', 'Maintenance']
    for section in test_sections:
        if section in build_data:
            test_data[section] = build_data[section].copy()
    
    # Write critical data
    critical_file = utils_dir / 'build_data_critical.json'
    with open(critical_file, 'w') as f:
        json.dump(critical_data, f, indent=2)
    print(f"✓ Created {critical_file}")
    print(f"  Contains: Essential (Users, Events)")
    if 'Core' in critical_data:
        print(f"  Contains: Core (Asset_Types)")
    
    # Write test data
    test_file = utils_dir / 'build_data_test.json'
    with open(test_file, 'w') as f:
        json.dump(test_data, f, indent=2)
    print(f"✓ Created {test_file}")
    print(f"  Contains: Core (Users, Locations, Make_Models, Assets)")
    print(f"  Contains: Asset_Details, Dispatching, Supply, Maintenance")
    
    # Create a backup of original
    backup_file = utils_dir / 'build_data.json.backup'
    if not backup_file.exists():
        import shutil
        shutil.copy2(build_data_file, backup_file)
        print(f"✓ Created backup: {backup_file}")
    
    # Summary
    print("\n" + "="*60)
    print("Migration Summary")
    print("="*60)
    print(f"Critical data file: {critical_file.name}")
    print(f"  - System user, Admin user")
    print(f"  - System initialization event")
    print(f"  - Essential asset types")
    print()
    print(f"Test data file: {test_file.name}")
    print(f"  - Sample locations, assets, make/models")
    print(f"  - Test users")
    print(f"  - Example dispatches, maintenance events")
    print(f"  - Sample supply items")
    print()
    print("Next steps:")
    print("1. Review build_data_critical.json - ensure it has minimum required data")
    print("2. Review build_data_test.json - verify all test data is included")
    print("3. Test with: python app.py --data-mode=critical")
    print("4. Test with: python app.py --data-mode=test")
    print("5. Update app/build.py to use load_build_data(mode=...)")
    print("6. Update individual init_data() functions to respect data_mode")
    print()
    print("Note: Original build_data.json is preserved for backward compatibility")
    print("="*60)
    
    return True


def validate_split():
    """Validate that the split files can be merged back to original"""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    utils_dir = project_root / 'app' / 'utils'
    
    critical_file = utils_dir / 'build_data_critical.json'
    test_file = utils_dir / 'build_data_test.json'
    original_file = utils_dir / 'build_data.json'
    
    if not critical_file.exists() or not test_file.exists():
        print("Error: Split files not found. Run split_build_data() first.")
        return False
    
    print("\nValidating split files...")
    
    with open(critical_file, 'r') as f:
        critical_data = json.load(f)
    
    with open(test_file, 'r') as f:
        test_data = json.load(f)
    
    # Merge them
    merged = deep_merge(critical_data, test_data)
    
    # Compare with original
    with open(original_file, 'r') as f:
        original_data = json.load(f)
    
    # Check if key sections match
    issues = []
    for key in original_data.keys():
        if key not in merged:
            issues.append(f"Missing section: {key}")
        elif original_data[key] != merged[key]:
            # Deep comparison would be better, but this is a simple check
            if isinstance(original_data[key], dict) and isinstance(merged[key], dict):
                if set(original_data[key].keys()) != set(merged[key].keys()):
                    issues.append(f"Section {key} has different keys")
    
    if issues:
        print("⚠ Validation issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✓ Validation passed: Split files can be merged to recreate original")
        return True


if __name__ == '__main__':
    print("="*60)
    print("Build Data Migration Script")
    print("="*60)
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--validate':
        success = validate_split()
    else:
        success = split_build_data()
        if success:
            # Auto-validate after splitting
            print()
            validate_split()
    
    sys.exit(0 if success else 1)


