#!/bin/bash

echo "📂 Checking directory structure for CrewAI podcast app..."
echo ""

# Check main directories
echo "Main directories:"
DIRS=("./podcast" "./podcast/src" "./podcast/src/podcast" "./podcast/templates" "./podcast/static")
for dir in "${DIRS[@]}"; do
  if [ -d "$dir" ]; then
    echo "✅ $dir exists"
  else
    echo "❌ $dir missing"
    mkdir -p "$dir"
    echo "   Created $dir"
  fi
done

echo ""
echo "Critical files:"
FILES=("./podcast/app.py" "./podcast/src/podcast/crew.py" "./requirements.txt" "./pyproject.toml")
for file in "${FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "✅ $file exists"
  else
    echo "❌ $file missing"
  fi
done

echo ""
echo "Tool files:"
TOOL_FILES=("./podcast/src/podcast/tools/elevenlabs.py" "./podcast/src/podcast/tools/web_search.py")
for file in "${TOOL_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "✅ $file exists"
  else
    echo "❌ $file missing"
    dir=$(dirname "$file")
    mkdir -p "$dir"
    echo "   Created directory $dir"
  fi
done

echo ""
echo "🔍 Checking import statements in app.py..."
if grep -q "from crew.podcast" ./podcast/app.py; then
  echo "❌ Found problematic import (crew.podcast) in app.py"
  echo "   Please update to 'from podcast.src.podcast'"
else
  echo "✅ No problematic imports found in app.py"
fi

echo ""
echo "Directory structure check complete."