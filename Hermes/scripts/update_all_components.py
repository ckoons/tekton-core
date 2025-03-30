#!/usr/bin/env python3
"""
Update All Components - Converts all Tekton components to use Hermes centralized services.

This script updates Tekton components to use the Unified Registration Protocol
and Centralized Logging System from Hermes.
"""

import os
import sys
import argparse
from pathlib import Path
import subprocess
import importlib.util
import shutil

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hermes.utils.logging_helper import setup_logging


def import_module_from_file(path):
    """Import a module from a file path."""
    module_name = os.path.basename(path).replace(".py", "")
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def update_engram(tekton_root, logger):
    """Update Engram to use centralized services."""
    logger.info("Updating Engram...")
    
    # Check if Engram exists
    engram_path = Path(tekton_root) / "Engram"
    if not engram_path.exists():
        logger.warn(f"Engram not found at {engram_path}")
        return False
    
    # Run update_engram_logging.py
    try:
        update_script = Path(__file__).parent / "update_engram_logging.py"
        if update_script.exists():
            # Run as a subprocess
            result = subprocess.run(
                [sys.executable, str(update_script), "--engram-path", str(engram_path)],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logger.info("Successfully updated Engram logging")
                logger.debug(result.stdout)
                return True
            else:
                logger.error(f"Failed to update Engram logging: {result.stderr}")
                return False
        else:
            # Import and run directly
            logger.info("Update script not found, updating manually...")
            
            # Memory module path
            memory_py_path = engram_path / "engram" / "core" / "memory.py"
            
            if not memory_py_path.exists():
                logger.error(f"Memory module not found: {memory_py_path}")
                return False
            
            # Read the memory.py file
            with open(memory_py_path, "r") as f:
                content = f.read()
            
            # Check if already updated
            if "from hermes.utils.logging_helper import setup_logging" in content:
                logger.info("Memory module already updated to use Centralized Logging")
                return True
            
            # Replace standard logging initialization with centralized logging
            old_logging_imports = """import logging
import os
import time"""
            
            new_logging_imports = """import os
import time
# Import Centralized Logging System
try:
    from hermes.utils.logging_helper import setup_logging
    USE_CENTRALIZED_LOGGING = True
except ImportError:
    # Fall back to standard logging if Hermes is not available
    import logging
    USE_CENTRALIZED_LOGGING = False"""
            
            content = content.replace(old_logging_imports, new_logging_imports)
            
            # Replace logging initialization
            old_logging_init = """# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("engram.memory")"""
            
            new_logging_init = """# Configure logging
if USE_CENTRALIZED_LOGGING:
    # Use Centralized Logging System
    logger = setup_logging("engram.memory")
else:
    # Fall back to standard logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger("engram.memory")"""
            
            content = content.replace(old_logging_init, new_logging_init)
            
            # Write the updated file
            with open(memory_py_path, "w") as f:
                f.write(content)
            
            logger.info(f"Successfully updated Engram memory module to use Centralized Logging")
            
            # Create a README file to explain the changes
            readme_path = engram_path / "LOGGING_UPDATE.md"
            
            with open(readme_path, "w") as f:
                f.write("""# Centralized Logging Update

Engram has been updated to use the Centralized Logging System (CLS) from Hermes. This provides the following benefits:

1. **Structured Logging**: All logs follow a standardized schema
2. **Schema Versioning**: Log schema evolution is tracked for backward compatibility
3. **Effective Timestamps**: Distinguish between when an event occurred vs. when it was logged
4. **Log Levels**: Standardized log levels (FATAL, ERROR, WARN, INFO, NORMAL, DEBUG, TRACE)
5. **Contextual Information**: Rich context for all log entries
6. **Correlation**: Track related log entries across components
7. **Storage**: Logs are stored centrally for easier debugging and analysis

## Compatibility

The update is backward compatible - if Hermes is not available, Engram will fall back to using standard Python logging.

## How to Use

No changes are needed to use the basic logging functionality. For advanced features:

```python
# Access Hermes logging features if available
if USE_CENTRALIZED_LOGGING:
    # Log with context
    logger.info("User action", context={"user_id": "user123"})
    
    # Create correlated logger
    op_logger = logger.with_correlation("operation-123")
    op_logger.info("Operation started")
    op_logger.info("Operation completed")
```

## Next Steps

More Engram modules will be updated to use the Centralized Logging System in future updates.
""")
            
            logger.normal("Created LOGGING_UPDATE.md with information about the changes")
            
            return True
    except Exception as e:
        logger.error(f"Error updating Engram: {e}")
        return False


def update_ergon(tekton_root, logger):
    """Update Ergon to use centralized services."""
    logger.info("Updating Ergon...")
    
    # Check if Ergon exists
    ergon_path = Path(tekton_root) / "Ergon"
    if not ergon_path.exists():
        logger.warn(f"Ergon not found at {ergon_path}")
        return False
    
    # Update main.py
    main_py_path = ergon_path / "ergon" / "cli" / "main.py"
    
    if not main_py_path.exists():
        logger.warn(f"Main module not found: {main_py_path}")
        # Try finding another suitable file
        app_py_path = ergon_path / "ergon" / "api" / "app.py"
        if app_py_path.exists():
            main_py_path = app_py_path
            logger.info(f"Using alternative file: {main_py_path}")
        else:
            logger.error("No suitable files found to update")
            return False
    
    # Read the file
    with open(main_py_path, "r") as f:
        content = f.read()
    
    # Check if already updated
    if "from hermes.utils.logging_helper import setup_logging" in content:
        logger.info("Ergon already updated to use Centralized Logging")
        return True
    
    # Find logging imports
    if "import logging" in content:
        # Replace standard logging with centralized logging
        if "import logging\n" in content:
            content = content.replace(
                "import logging\n",
                "# Import Centralized Logging System\n"
                "try:\n"
                "    from hermes.utils.logging_helper import setup_logging\n"
                "    USE_CENTRALIZED_LOGGING = True\n"
                "except ImportError:\n"
                "    # Fall back to standard logging if Hermes is not available\n"
                "    import logging\n"
                "    USE_CENTRALIZED_LOGGING = False\n"
            )
        else:
            # More complex case, add after imports
            import_section_end = 0
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    import_section_end = i
            
            if import_section_end > 0:
                lines.insert(import_section_end + 1, "")
                lines.insert(import_section_end + 2, "# Import Centralized Logging System")
                lines.insert(import_section_end + 3, "try:")
                lines.insert(import_section_end + 4, "    from hermes.utils.logging_helper import setup_logging")
                lines.insert(import_section_end + 5, "    USE_CENTRALIZED_LOGGING = True")
                lines.insert(import_section_end + 6, "except ImportError:")
                lines.insert(import_section_end + 7, "    # Fall back to standard logging if Hermes is not available")
                lines.insert(import_section_end + 8, "    import logging")
                lines.insert(import_section_end + 9, "    USE_CENTRALIZED_LOGGING = False")
                content = "\n".join(lines)
    
        # Find logger initialization
        logger_init_patterns = [
            "logger = logging.getLogger",
            "logging.basicConfig"
        ]
        
        for pattern in logger_init_patterns:
            if pattern in content:
                # Simple case: direct logger assignment
                if pattern == "logger = logging.getLogger" and "logger = logging.getLogger" in content:
                    module_name = content.split("logger = logging.getLogger(")[1].split(")")[0].strip('"\'')
                    
                    content = content.replace(
                        f'logger = logging.getLogger({module_name})',
                        f'if USE_CENTRALIZED_LOGGING:\n'
                        f'    # Use Centralized Logging System\n'
                        f'    logger = setup_logging({module_name})\n'
                        f'else:\n'
                        f'    # Fall back to standard logging\n'
                        f'    logger = logging.getLogger({module_name})'
                    )
                    break
                
                # Check for basicConfig
                elif pattern == "logging.basicConfig" and "logging.basicConfig" in content:
                    logger_line = content.split("logging.basicConfig")[1].split("\n")[0]
                    if "getLogger" in content.split("logging.basicConfig")[1].split("\n\n")[0]:
                        # basicConfig followed by getLogger
                        config_and_logger = "logging.basicConfig" + content.split("logging.basicConfig")[1].split("\n\n")[0]
                        
                        # Extract logger name
                        if "logger = logging.getLogger(" in config_and_logger:
                            module_name = config_and_logger.split("logger = logging.getLogger(")[1].split(")")[0].strip('"\'')
                        else:
                            module_name = '"ergon"'
                        
                        content = content.replace(
                            config_and_logger,
                            f'if USE_CENTRALIZED_LOGGING:\n'
                            f'    # Use Centralized Logging System\n'
                            f'    logger = setup_logging({module_name})\n'
                            f'else:\n'
                            f'    # Fall back to standard logging\n'
                            f'    {config_and_logger}'
                        )
                        break
    
    # Write the updated file
    with open(main_py_path, "w") as f:
        f.write(content)
    
    logger.info(f"Successfully updated Ergon to use Centralized Logging")
    
    # Create a README file to explain the changes
    readme_path = ergon_path / "LOGGING_UPDATE.md"
    
    with open(readme_path, "w") as f:
        f.write("""# Centralized Logging Update

Ergon has been updated to use the Centralized Logging System (CLS) from Hermes. This provides the following benefits:

1. **Structured Logging**: All logs follow a standardized schema
2. **Schema Versioning**: Log schema evolution is tracked for backward compatibility
3. **Effective Timestamps**: Distinguish between when an event occurred vs. when it was logged
4. **Log Levels**: Standardized log levels (FATAL, ERROR, WARN, INFO, NORMAL, DEBUG, TRACE)
5. **Contextual Information**: Rich context for all log entries
6. **Correlation**: Track related log entries across components
7. **Storage**: Logs are stored centrally for easier debugging and analysis

## Compatibility

The update is backward compatible - if Hermes is not available, Ergon will fall back to using standard Python logging.

## How to Use

No changes are needed to use the basic logging functionality. For advanced features:

```python
# Access Hermes logging features if available
if USE_CENTRALIZED_LOGGING:
    # Log with context
    logger.info("User action", context={"user_id": "user123"})
    
    # Create correlated logger
    op_logger = logger.with_correlation("operation-123")
    op_logger.info("Operation started")
    op_logger.info("Operation completed")
```

## Next Steps

More Ergon modules will be updated to use the Centralized Logging System in future updates.
""")
    
    logger.normal("Created LOGGING_UPDATE.md for Ergon with information about the changes")
    
    return True


def update_athena(tekton_root, logger):
    """Update Athena to use centralized services."""
    logger.info("Updating Athena...")
    
    # Check if Athena exists
    athena_path = Path(tekton_root) / "Athena"
    if not athena_path.exists():
        logger.warn(f"Athena not found at {athena_path}")
        return False
    
    # Find a suitable file to update
    suitable_files = [
        athena_path / "athena" / "core" / "engine.py",
        athena_path / "athena" / "core" / "entity.py",
        athena_path / "athena" / "core" / "relationship.py"
    ]
    
    updated_any = False
    
    for file_path in suitable_files:
        if file_path.exists():
            # Read the file
            with open(file_path, "r") as f:
                content = f.read()
            
            # Check if already updated
            if "from hermes.utils.logging_helper import setup_logging" in content:
                logger.info(f"{file_path.name} already updated to use Centralized Logging")
                updated_any = True
                continue
            
            # Find logging imports
            if "import logging" in content:
                # Replace standard logging with centralized logging
                if "import logging\n" in content:
                    content = content.replace(
                        "import logging\n",
                        "# Import Centralized Logging System\n"
                        "try:\n"
                        "    from hermes.utils.logging_helper import setup_logging\n"
                        "    USE_CENTRALIZED_LOGGING = True\n"
                        "except ImportError:\n"
                        "    # Fall back to standard logging if Hermes is not available\n"
                        "    import logging\n"
                        "    USE_CENTRALIZED_LOGGING = False\n"
                    )
                else:
                    # More complex case, add after imports
                    import_section_end = 0
                    lines = content.split("\n")
                    for i, line in enumerate(lines):
                        if line.startswith("import ") or line.startswith("from "):
                            import_section_end = i
                    
                    if import_section_end > 0:
                        lines.insert(import_section_end + 1, "")
                        lines.insert(import_section_end + 2, "# Import Centralized Logging System")
                        lines.insert(import_section_end + 3, "try:")
                        lines.insert(import_section_end + 4, "    from hermes.utils.logging_helper import setup_logging")
                        lines.insert(import_section_end + 5, "    USE_CENTRALIZED_LOGGING = True")
                        lines.insert(import_section_end + 6, "except ImportError:")
                        lines.insert(import_section_end + 7, "    # Fall back to standard logging if Hermes is not available")
                        lines.insert(import_section_end + 8, "    import logging")
                        lines.insert(import_section_end + 9, "    USE_CENTRALIZED_LOGGING = False")
                        content = "\n".join(lines)
            
                # Find logger initialization
                logger_init_patterns = [
                    "logger = logging.getLogger",
                    "logging.basicConfig"
                ]
                
                for pattern in logger_init_patterns:
                    if pattern in content:
                        # Simple case: direct logger assignment
                        if pattern == "logger = logging.getLogger" and "logger = logging.getLogger" in content:
                            # Extract module name
                            if 'logger = logging.getLogger("' in content:
                                module_name = content.split('logger = logging.getLogger("')[1].split('"')[0]
                                module_name = f'"{module_name}"'
                            elif "logger = logging.getLogger('" in content:
                                module_name = content.split("logger = logging.getLogger('")[1].split("'")[0]
                                module_name = f"'{module_name}'"
                            elif "logger = logging.getLogger(__name__" in content:
                                module_name = "__name__"
                            else:
                                module_name = '"athena"'
                            
                            content = content.replace(
                                f'logger = logging.getLogger({module_name})',
                                f'if USE_CENTRALIZED_LOGGING:\n'
                                f'    # Use Centralized Logging System\n'
                                f'    logger = setup_logging({module_name})\n'
                                f'else:\n'
                                f'    # Fall back to standard logging\n'
                                f'    logger = logging.getLogger({module_name})'
                            )
                            break
                        
                        # Check for basicConfig
                        elif pattern == "logging.basicConfig" and "logging.basicConfig" in content:
                            logger_line = content.split("logging.basicConfig")[1].split("\n")[0]
                            if "getLogger" in content.split("logging.basicConfig")[1].split("\n\n")[0]:
                                # basicConfig followed by getLogger
                                config_and_logger = "logging.basicConfig" + content.split("logging.basicConfig")[1].split("\n\n")[0]
                                
                                # Extract logger name
                                if "logger = logging.getLogger(" in config_and_logger:
                                    if 'logger = logging.getLogger("' in config_and_logger:
                                        module_name = config_and_logger.split('logger = logging.getLogger("')[1].split('"')[0]
                                        module_name = f'"{module_name}"'
                                    elif "logger = logging.getLogger('" in config_and_logger:
                                        module_name = config_and_logger.split("logger = logging.getLogger('")[1].split("'")[0]
                                        module_name = f"'{module_name}'"
                                    else:
                                        module_name = '"athena"'
                                else:
                                    module_name = '"athena"'
                                
                                content = content.replace(
                                    config_and_logger,
                                    f'if USE_CENTRALIZED_LOGGING:\n'
                                    f'    # Use Centralized Logging System\n'
                                    f'    logger = setup_logging({module_name})\n'
                                    f'else:\n'
                                    f'    # Fall back to standard logging\n'
                                    f'    {config_and_logger}'
                                )
                                break
            
            # Write the updated file
            with open(file_path, "w") as f:
                f.write(content)
            
            logger.info(f"Successfully updated {file_path.name} to use Centralized Logging")
            updated_any = True
    
    if updated_any:
        # Create a README file to explain the changes
        readme_path = athena_path / "LOGGING_UPDATE.md"
        
        with open(readme_path, "w") as f:
            f.write("""# Centralized Logging Update

Athena has been updated to use the Centralized Logging System (CLS) from Hermes. This provides the following benefits:

1. **Structured Logging**: All logs follow a standardized schema
2. **Schema Versioning**: Log schema evolution is tracked for backward compatibility
3. **Effective Timestamps**: Distinguish between when an event occurred vs. when it was logged
4. **Log Levels**: Standardized log levels (FATAL, ERROR, WARN, INFO, NORMAL, DEBUG, TRACE)
5. **Contextual Information**: Rich context for all log entries
6. **Correlation**: Track related log entries across components
7. **Storage**: Logs are stored centrally for easier debugging and analysis

## Compatibility

The update is backward compatible - if Hermes is not available, Athena will fall back to using standard Python logging.

## How to Use

No changes are needed to use the basic logging functionality. For advanced features:

```python
# Access Hermes logging features if available
if USE_CENTRALIZED_LOGGING:
    # Log with context
    logger.info("User action", context={"user_id": "user123"})
    
    # Create correlated logger
    op_logger = logger.with_correlation("operation-123")
    op_logger.info("Operation started")
    op_logger.info("Operation completed")
```

## Next Steps

More Athena modules will be updated to use the Centralized Logging System in future updates.
""")
        
        logger.normal("Created LOGGING_UPDATE.md for Athena with information about the changes")
    
    return updated_any


def update_harmonia(tekton_root, logger):
    """Update Harmonia to use centralized services."""
    logger.info("Updating Harmonia...")
    
    # Check if Harmonia exists
    harmonia_path = Path(tekton_root) / "Harmonia"
    if not harmonia_path.exists():
        logger.warn(f"Harmonia not found at {harmonia_path}")
        return False
    
    # Find suitable files to update
    suitable_files = [
        harmonia_path / "harmonia" / "core" / "engine.py",
        harmonia_path / "harmonia" / "core" / "workflow.py",
        harmonia_path / "harmonia" / "core" / "state.py"
    ]
    
    updated_any = False
    
    for file_path in suitable_files:
        if file_path.exists():
            # Read the file
            with open(file_path, "r") as f:
                content = f.read()
            
            # Check if already updated
            if "from hermes.utils.logging_helper import setup_logging" in content:
                logger.info(f"{file_path.name} already updated to use Centralized Logging")
                updated_any = True
                continue
            
            # Find logging imports
            if "import logging" in content:
                # Replace standard logging with centralized logging
                if "import logging\n" in content:
                    content = content.replace(
                        "import logging\n",
                        "# Import Centralized Logging System\n"
                        "try:\n"
                        "    from hermes.utils.logging_helper import setup_logging\n"
                        "    USE_CENTRALIZED_LOGGING = True\n"
                        "except ImportError:\n"
                        "    # Fall back to standard logging if Hermes is not available\n"
                        "    import logging\n"
                        "    USE_CENTRALIZED_LOGGING = False\n"
                    )
                else:
                    # More complex case, add after imports
                    import_section_end = 0
                    lines = content.split("\n")
                    for i, line in enumerate(lines):
                        if line.startswith("import ") or line.startswith("from "):
                            import_section_end = i
                    
                    if import_section_end > 0:
                        lines.insert(import_section_end + 1, "")
                        lines.insert(import_section_end + 2, "# Import Centralized Logging System")
                        lines.insert(import_section_end + 3, "try:")
                        lines.insert(import_section_end + 4, "    from hermes.utils.logging_helper import setup_logging")
                        lines.insert(import_section_end + 5, "    USE_CENTRALIZED_LOGGING = True")
                        lines.insert(import_section_end + 6, "except ImportError:")
                        lines.insert(import_section_end + 7, "    # Fall back to standard logging if Hermes is not available")
                        lines.insert(import_section_end + 8, "    import logging")
                        lines.insert(import_section_end + 9, "    USE_CENTRALIZED_LOGGING = False")
                        content = "\n".join(lines)
            
                # Find logger initialization
                logger_init_patterns = [
                    "logger = logging.getLogger",
                    "logging.basicConfig"
                ]
                
                for pattern in logger_init_patterns:
                    if pattern in content:
                        # Simple case: direct logger assignment
                        if pattern == "logger = logging.getLogger" and "logger = logging.getLogger" in content:
                            # Extract module name
                            if 'logger = logging.getLogger("' in content:
                                module_name = content.split('logger = logging.getLogger("')[1].split('"')[0]
                                module_name = f'"{module_name}"'
                            elif "logger = logging.getLogger('" in content:
                                module_name = content.split("logger = logging.getLogger('")[1].split("'")[0]
                                module_name = f"'{module_name}'"
                            elif "logger = logging.getLogger(__name__" in content:
                                module_name = "__name__"
                            else:
                                module_name = '"harmonia"'
                            
                            content = content.replace(
                                f'logger = logging.getLogger({module_name})',
                                f'if USE_CENTRALIZED_LOGGING:\n'
                                f'    # Use Centralized Logging System\n'
                                f'    logger = setup_logging({module_name})\n'
                                f'else:\n'
                                f'    # Fall back to standard logging\n'
                                f'    logger = logging.getLogger({module_name})'
                            )
                            break
                        
                        # Check for basicConfig
                        elif pattern == "logging.basicConfig" and "logging.basicConfig" in content:
                            logger_line = content.split("logging.basicConfig")[1].split("\n")[0]
                            if "getLogger" in content.split("logging.basicConfig")[1].split("\n\n")[0]:
                                # basicConfig followed by getLogger
                                config_and_logger = "logging.basicConfig" + content.split("logging.basicConfig")[1].split("\n\n")[0]
                                
                                # Extract logger name
                                if "logger = logging.getLogger(" in config_and_logger:
                                    if 'logger = logging.getLogger("' in config_and_logger:
                                        module_name = config_and_logger.split('logger = logging.getLogger("')[1].split('"')[0]
                                        module_name = f'"{module_name}"'
                                    elif "logger = logging.getLogger('" in config_and_logger:
                                        module_name = config_and_logger.split("logger = logging.getLogger('")[1].split("'")[0]
                                        module_name = f"'{module_name}'"
                                    else:
                                        module_name = '"harmonia"'
                                else:
                                    module_name = '"harmonia"'
                                
                                content = content.replace(
                                    config_and_logger,
                                    f'if USE_CENTRALIZED_LOGGING:\n'
                                    f'    # Use Centralized Logging System\n'
                                    f'    logger = setup_logging({module_name})\n'
                                    f'else:\n'
                                    f'    # Fall back to standard logging\n'
                                    f'    {config_and_logger}'
                                )
                                break
            
            # Write the updated file
            with open(file_path, "w") as f:
                f.write(content)
            
            logger.info(f"Successfully updated {file_path.name} to use Centralized Logging")
            updated_any = True
    
    if updated_any:
        # Create a README file to explain the changes
        readme_path = harmonia_path / "LOGGING_UPDATE.md"
        
        with open(readme_path, "w") as f:
            f.write("""# Centralized Logging Update

Harmonia has been updated to use the Centralized Logging System (CLS) from Hermes. This provides the following benefits:

1. **Structured Logging**: All logs follow a standardized schema
2. **Schema Versioning**: Log schema evolution is tracked for backward compatibility
3. **Effective Timestamps**: Distinguish between when an event occurred vs. when it was logged
4. **Log Levels**: Standardized log levels (FATAL, ERROR, WARN, INFO, NORMAL, DEBUG, TRACE)
5. **Contextual Information**: Rich context for all log entries
6. **Correlation**: Track related log entries across components
7. **Storage**: Logs are stored centrally for easier debugging and analysis

## Compatibility

The update is backward compatible - if Hermes is not available, Harmonia will fall back to using standard Python logging.

## How to Use

No changes are needed to use the basic logging functionality. For advanced features:

```python
# Access Hermes logging features if available
if USE_CENTRALIZED_LOGGING:
    # Log with context
    logger.info("User action", context={"user_id": "user123"})
    
    # Create correlated logger
    op_logger = logger.with_correlation("operation-123")
    op_logger.info("Operation started")
    op_logger.info("Operation completed")
```

## Next Steps

More Harmonia modules will be updated to use the Centralized Logging System in future updates.
""")
        
        logger.normal("Created LOGGING_UPDATE.md for Harmonia with information about the changes")
    
    return updated_any


def update_hermes_itself(logger):
    """Update Hermes's internal files to use the Centralized Logging System."""
    logger.info("Updating Hermes's internal files...")
    
    # Get Hermes directory
    hermes_path = Path(__file__).parent.parent
    
    # Files to update
    files_to_update = [
        hermes_path / "hermes" / "core" / "vector_engine.py",
        hermes_path / "hermes" / "core" / "message_bus.py",
        hermes_path / "hermes" / "core" / "service_discovery.py",
        hermes_path / "hermes" / "core" / "registration.py"
    ]
    
    updated_any = False
    
    for file_path in files_to_update:
        if file_path.exists():
            # Read the file
            with open(file_path, "r") as f:
                content = f.read()
            
            # Skip if already using the centralized logging
            if "from hermes.utils.logging_helper import setup_logging" in content:
                logger.info(f"{file_path.name} already using the Centralized Logging System")
                continue
            
            # Check if using standard logging
            if "import logging" in content and "logger = logging.getLogger" in content:
                # Extract module name
                if 'logger = logging.getLogger("' in content:
                    module_name = content.split('logger = logging.getLogger("')[1].split('"')[0]
                    module_name_str = f'"{module_name}"'
                elif "logger = logging.getLogger('" in content:
                    module_name = content.split("logger = logging.getLogger('")[1].split("'")[0]
                    module_name_str = f"'{module_name}'"
                elif "logger = logging.getLogger(__name__" in content:
                    module_name = file_path.stem
                    module_name_str = "__name__"
                else:
                    module_name = file_path.stem
                    module_name_str = f'"hermes.core.{module_name}"'
                
                # Replace imports
                content = content.replace(
                    "import logging",
                    "from hermes.core.logging import get_logger"
                )
                
                # Replace logger initialization
                content = content.replace(
                    f"logger = logging.getLogger({module_name_str})",
                    f"logger = get_logger({module_name_str})"
                )
                
                # Write the updated file
                with open(file_path, "w") as f:
                    f.write(content)
                
                logger.info(f"Updated {file_path.name} to use the Centralized Logging System")
                updated_any = True
    
    return updated_any


def main():
    """Main function to parse arguments and run the update."""
    parser = argparse.ArgumentParser(description="Update Tekton components to use Hermes centralized services")
    
    parser.add_argument(
        "--tekton-root",
        type=str,
        default=None,
        help="Path to Tekton root directory (defaults to ../)"
    )
    
    parser.add_argument(
        "--components",
        type=str,
        nargs="*",
        choices=["engram", "ergon", "athena", "harmonia", "hermes", "all"],
        default=["all"],
        help="Components to update (defaults to all)"
    )
    
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip components that already use centralized services"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    logger = setup_logging("hermes.scripts.update_all_components")
    
    # Determine Tekton root path
    if args.tekton_root:
        tekton_root = Path(args.tekton_root)
    else:
        tekton_root = Path(__file__).parent.parent.parent
    
    logger.info(f"Using Tekton root path: {tekton_root}")
    
    # Determine components to update
    components = args.components
    if "all" in components:
        components = ["engram", "ergon", "athena", "harmonia", "hermes"]
    
    # Update components
    results = {}
    
    if "hermes" in components:
        results["hermes"] = update_hermes_itself(logger)
    
    if "engram" in components:
        results["engram"] = update_engram(tekton_root, logger)
    
    if "ergon" in components:
        results["ergon"] = update_ergon(tekton_root, logger)
    
    if "athena" in components:
        results["athena"] = update_athena(tekton_root, logger)
    
    if "harmonia" in components:
        results["harmonia"] = update_harmonia(tekton_root, logger)
    
    # Print summary
    logger.info("Update summary:")
    for component, success in results.items():
        logger.info(f"  {component}: {'Updated' if success else 'Failed'}")
    
    return True


if __name__ == "__main__":
    main()