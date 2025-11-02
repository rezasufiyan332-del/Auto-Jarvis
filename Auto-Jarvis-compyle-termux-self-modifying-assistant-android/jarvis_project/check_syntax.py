#!/usr/bin/env python3
import py_compile
import sys
import os

files_to_check = [
    'jarvis_v14_ultimate/jarvis.py',
    'jarvis_v14_ultimate/launcher.py',
]

errors_found = []
base_dir = '/workspace/jarvis_project'

for filepath in files_to_check:
    full_path = os.path.join(base_dir, filepath)
    if not os.path.exists(full_path):
        print(f"⚠️  File not found: {filepath}")
        continue
        
    try:
        py_compile.compile(full_path, doraise=True)
        print(f"✅ {filepath} - कोई syntax errors नहीं")
    except SyntaxError as e:
        error_msg = f"❌ {filepath} - Syntax Error at line {e.lineno}: {e.msg}"
        print(error_msg)
        if e.text:
            print(f"   Code: {e.text.strip()}")
        errors_found.append(error_msg)
    except Exception as e:
        error_msg = f"❌ {filepath} - Error: {e}"
        print(error_msg)
        errors_found.append(error_msg)

print("\n" + "="*60)
if errors_found:
    print(f"❌ Total Errors: {len(errors_found)}")
    sys.exit(1)
else:
    print("✅ सभी files में कोई syntax errors नहीं हैं!")
    sys.exit(0)
