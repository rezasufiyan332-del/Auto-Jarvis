#!/usr/bin/env python3
"""
Test all imports from jarvis.py
"""

import sys
from pathlib import Path

# Add project to path
project_dir = Path(__file__).parent / 'jarvis_v14_ultimate'
sys.path.insert(0, str(project_dir))

errors = []
success_count = 0

# Test core imports
core_imports = [
    ('core.ai_engine', 'AIEngine'),
    ('core.enhanced_database_manager', 'DatabaseManager'),
    ('core.advanced_termux_controller', 'AdvancedTermuxController'),
    ('core.world_data_manager', 'WorldDataManager'),
    ('core.github_learning_engine', 'GitHubLearningEngine'),
    ('core.notification_system', 'NotificationSystem'),
    ('core.self_modifying_engine', 'SelfModifyingEngine'),
    ('core.project_auto_executor', 'ProjectAutoExecutor'),
    ('core.zero_intervention_processor', 'ZeroInterventionProcessor'),
    ('core.advanced_auto_fix', 'AdvancedAutoFix'),
    ('core.multi_modal_ai_engine', 'MultiModalAIEngine'),
    ('core.ultimate_termux_integration', 'UltimateTermuxIntegration'),
    ('core.error_proof_system', 'ErrorProofSystem'),
    ('core.ultimate_autonomous_controller', 'UltimateAutonomousController'),
    ('core.advanced_auto_execution_system', 'AdvancedAutoExecutionSystem'),
    ('core.advanced_pattern_recognition', 'AdvancedPatternRecognition'),
    ('core.predictive_assistance', 'PredictiveAssistance'),
    ('core.self_healing_architectures', 'SelfHealingArchitectures'),
    ('core.advanced_security_layers', 'AdvancedSecurityLayers'),
    ('core.performance_optimizer', 'PerformanceOptimizer'),
    ('core.intelligent_resource_manager', 'IntelligentResourceManager'),
    ('core.memory_manager', 'MemoryManager'),
    ('core.battery_optimizer', 'BatteryOptimizer'),
    ('core.background_processor', 'BackgroundProcessor'),
    ('core.cross_platform_integration', 'CrossPlatformIntegration'),
]

# Test termux_native imports
termux_imports = [
    ('termux_native.system_monitor', 'SystemMonitor'),
    ('termux_native.code_analyzer', 'AdvancedCodeAnalyzer'),
    ('termux_native.voice_controller', 'EnhancedVoiceController'),
    ('termux_native.security_manager', 'SecurityManager'),
]

all_imports = core_imports + termux_imports

print("Testing imports...\n")

for module_name, class_name in all_imports:
    try:
        module = __import__(module_name, fromlist=[class_name])
        cls = getattr(module, class_name)
        print(f"✅ {module_name}.{class_name}")
        success_count += 1
    except ImportError as e:
        error_msg = f"❌ {module_name}.{class_name}: ImportError - {e}"
        print(error_msg)
        errors.append(error_msg)
    except AttributeError as e:
        error_msg = f"❌ {module_name}.{class_name}: AttributeError - {e}"
        print(error_msg)
        errors.append(error_msg)
    except Exception as e:
        error_msg = f"❌ {module_name}.{class_name}: {type(e).__name__} - {e}"
        print(error_msg)
        errors.append(error_msg)

print("\n" + "="*60)
print(f"✅ Successful: {success_count}/{len(all_imports)}")
print(f"❌ Failed: {len(errors)}/{len(all_imports)}")

if errors:
    print("\nErrors:")
    for error in errors:
        print(f"  {error}")
    sys.exit(1)
else:
    print("\n🎉 All imports working perfectly!")
    sys.exit(0)
