#!/usr/bin/env python3
import py_compile
import sys

file_path = '/workspace/jarvis_project/jarvis_v14_ultimate/core/ultimate_termux_integration.py'

try:
    py_compile.compile(file_path, doraise=True)
    print(f"✅ No syntax errors in {file_path}")
    sys.exit(0)
except SyntaxError as e:
    print(f"❌ Syntax Error:")
    print(f"   File: {e.filename}")
    print(f"   Line: {e.lineno}")
    print(f"   Message: {e.msg}")
    if e.text:
        print(f"   Code: {e.text.strip()}")
    if e.offset:
        print(f"   " + " " * (e.offset - 1) + "^")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
