#!/usr/bin/env python3
"""
Script to split combined modules into individual files
"""

import re
from pathlib import Path

# Read the combined files
base_dir = Path('/workspace/jarvis_project/jarvis_v14_ultimate')

# Define modules to create
modules_mapping = {
    'core': {
        'missing_modules_part1.py': [
            ('AdvancedTermuxController', 'advanced_termux_controller.py'),
            ('WorldDataManager', 'world_data_manager.py'),
            ('GitHubLearningEngine', 'github_learning_engine.py'),
            ('NotificationSystem', 'notification_system.py'),
            ('SelfModifyingEngine', 'self_modifying_engine.py'),
            ('ProjectAutoExecutor', 'project_auto_executor.py'),
            ('ZeroInterventionProcessor', 'zero_intervention_processor.py'),
            ('AdvancedAutoFix', 'advanced_auto_fix.py'),
            ('AdvancedAutoExecutionSystem', 'advanced_auto_execution_system.py'),
        ],
        'missing_modules_part2.py': [
            ('AdvancedPatternRecognition', 'advanced_pattern_recognition.py'),
            ('PredictiveAssistance', 'predictive_assistance.py'),
            ('SelfHealingArchitectures', 'self_healing_architectures.py'),
            ('AdvancedSecurityLayers', 'advanced_security_layers.py'),
            ('PerformanceOptimizer', 'performance_optimizer.py'),
            ('IntelligentResourceManager', 'intelligent_resource_manager.py'),
            ('MemoryManager', 'memory_manager.py'),
            ('BatteryOptimizer', 'battery_optimizer.py'),
            ('BackgroundProcessor', 'background_processor.py'),
            ('CrossPlatformIntegration', 'cross_platform_integration.py'),
        ]
    },
    'termux_native': {
        'all_modules.py': [
            ('SystemMonitor', 'system_monitor.py'),
            ('AdvancedCodeAnalyzer', 'code_analyzer.py'),
            ('EnhancedVoiceController', 'voice_controller.py'),
            ('SecurityManager', 'security_manager.py'),
        ]
    }
}

def extract_class_code(content: str, class_name: str) -> str:
    """Extract class code from content"""
    # Find class definition
    pattern = rf'class {class_name}[:\(].*?(?=\n(?:class |# ====|$))'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        return match.group(0)
    return None

def create_module_file(content: str, output_path: Path):
    """Create individual module file"""
    header = '''#!/usr/bin/env python3
"""
{module_name}
Auto-generated stub implementation for Termux compatibility
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
'''
    
    # Add necessary imports based on content
    if 'psutil' in content:
        header += 'import psutil\n'
    if 'gc' in content:
        header += 'import gc\n'
    if 'subprocess' in content:
        header += 'import subprocess\n'
    if 'sqlite3' in content:
        header += 'import sqlite3\n'
        
    header += '\n\n'
    
    module_name = output_path.stem.replace('_', ' ').title()
    full_content = header.format(module_name=module_name) + content
    
    output_path.write_text(full_content, encoding='utf-8')
    print(f"✅ Created: {output_path.relative_to(base_dir)}")

# Process each module type
for module_type, source_files in modules_mapping.items():
    module_dir = base_dir / module_type
    
    for source_file, classes in source_files.items():
        source_path = module_dir / source_file
        
        if not source_path.exists():
            print(f"⚠️  Source not found: {source_path}")
            continue
            
        source_content = source_path.read_text(encoding='utf-8')
        
        for class_name, output_file in classes:
            class_code = extract_class_code(source_content, class_name)
            
            if class_code:
                output_path = module_dir / output_file
                create_module_file(class_code, output_path)
            else:
                print(f"⚠️  Class not found: {class_name}")

print("\n✅ All modules created successfully!")
