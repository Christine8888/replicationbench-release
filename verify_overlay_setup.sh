#!/bin/bash
# Verify overlay package installation and visibility

PAPER_ID="trgb-std-candle"  # Change as needed
WORKSPACE_BASE="/oak/stanford/projects/c4u/researchbench/workspace"
SINGULARITY_IMAGE="/oak/stanford/projects/c4u/researchbench/workspace/inspect_final_tool.sif"
OVERLAY_PATH="$WORKSPACE_BASE/$PAPER_ID/overlay"

echo "=== Verification Script for Overlay Setup ==="
echo ""
echo "Paper: $PAPER_ID"
echo "Overlay: $OVERLAY_PATH"
echo ""

echo "1. CHECK: What's installed in the overlay?"
echo "----------------------------------------"
ls -la $OVERLAY_PATH/lib/python3.11/site-packages/ 2>/dev/null | head -10
echo ""

echo "2. CHECK: Can launch.py see overlay packages?"
echo "--------------------------------------------"
singularity exec \
    --overlay $OVERLAY_PATH \
    --bind $OVERLAY_PATH:$OVERLAY_PATH:rw \
    --bind /tmp:/tmp:rw \
    $SINGULARITY_IMAGE \
    bash -c "
        export PYTHONPATH=$OVERLAY_PATH/lib/python3.11/site-packages:\$PYTHONPATH
        export PATH=$OVERLAY_PATH/bin:\$PATH
        python3 -c '
import sys
print(\"Python paths:\")
for p in sys.path[:5]:
    print(f\"  {p}\")
print()
print(\"Checking for overlay packages:\")
try:
    # Try importing a package you know is in overlay
    import numpy  # or whatever package you installed
    print(f\"  numpy found at: {numpy.__file__}\")
except ImportError as e:
    print(f\"  numpy not found: {e}\")
'
    "
echo ""

echo "3. CHECK: Runtime isolation test"
echo "--------------------------------"
echo "Installing test package to /tmp/.local (runtime only)..."
singularity exec \
    --overlay $OVERLAY_PATH \
    --bind $OVERLAY_PATH:$OVERLAY_PATH:rw \
    --bind /tmp:/tmp:rw \
    $SINGULARITY_IMAGE \
    bash -c "
        export PYTHONUSERBASE=/tmp/.local
        export HOME=/tmp
        export PYTHONPATH=$OVERLAY_PATH/lib/python3.11/site-packages:/tmp/.local/lib/python3.11/site-packages:\$PYTHONPATH

        # Install test package to /tmp/.local
        python3 -m pip install --user --quiet cowsay

        # Verify it's in /tmp/.local (not overlay)
        echo 'Test package location:'
        python3 -c 'import cowsay; print(f\"  cowsay at: {cowsay.__file__}\")'

        # Show it's NOT in overlay
        echo ''
        echo 'Confirming NOT in overlay:'
        if [ -d '$OVERLAY_PATH/lib/python3.11/site-packages/cowsay' ]; then
            echo '  ERROR: Package found in overlay (should be in /tmp only)!'
        else
            echo '  ✓ Correctly isolated to /tmp/.local (not in overlay)'
        fi
    "

echo ""
echo "=== Summary ==="
echo "1. Overlay packages at: $OVERLAY_PATH/lib/python3.11/site-packages/"
echo "2. Launch.py PYTHONPATH includes: $OVERLAY_PATH/lib/python3.11/site-packages"
echo "3. Runtime installs go to: /tmp/.local (ephemeral, not overlay)"