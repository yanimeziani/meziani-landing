#!/bin/bash
set -e

# Create symbolic links for easier imports
echo "Creating symbolic links for module imports..."
if [ -d "/app/podcast/src/podcast/tools" ]; then
  # Create a symlink in the python path
  ln -sf /app/podcast/src/podcast/tools /app/podcast/tools
  echo "Created symbolic link: /app/podcast/tools -> /app/podcast/src/podcast/tools"
fi

# Create any missing __init__.py files
find /app/podcast -type d -not -path "*/\.*" | while read dir; do
  if [ ! -f "$dir/__init__.py" ]; then
    touch "$dir/__init__.py"
    echo "Created __init__.py in $dir"
  fi
done

# Print debug information
echo "Environment:"
echo "PYTHONPATH: $PYTHONPATH"
echo "Directory structure:"
find /app -type d -maxdepth 3 | sort

# Execute the command
exec "$@"