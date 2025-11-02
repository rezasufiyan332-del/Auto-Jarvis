#!/usr/bin/env python3
"""
Try to import without ultimate_termux_integration
"""

import sys
from pathlib import Path

# Add project to path
project_dir = Path('/workspace/jarvis_project/jarvis_v14_ultimate')
sys.path.insert(0, str(project_dir))

# Temporarily rename the problematic file
import os
orig_path = project_dir / 'core' / 'ultimate_termux_integration.py'
temp_path = project_dir / 'core' / 'ultimate_termux_integration.py.bak'

if orig_path.exists():
    os.rename(str(orig_path), str(temp_path))
    print("✅ Renamed ultimate_termux_integration.py to .bak")

# Now try imports
try:
    from core.ai_engine import AIEngine
    print("✅ AIEngine imported successfully without ultimate_termux_integration")
    from core.enhanced_database_manager import DatabaseManager
    print("✅ DatabaseManager imported successfully")
except Exception as e:
    print(f"❌ Import still failing: {e}")

# Restore file
if temp_path.exists():
    os.rename(str(temp_path), str(orig_path))
    print("\n✅ Restored ultimate_termux_integration.py")
