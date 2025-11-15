#!/bin/bash
# Upgrade NexAML module after code changes

echo "=== NexAML Module Upgrade Script ==="
echo ""

# Clear Python cache
echo "1. Clearing Python cache..."
find addons/nexaml -type f -name "*.pyc" -delete 2>/dev/null
find addons/nexaml -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
echo "   ✓ Cache cleared"
echo ""

# Check if using Docker
echo "2. Detecting environment..."
if docker ps | grep -q odoo; then
    echo "   ℹ Docker environment detected"
    USE_DOCKER=true
else
    echo "   ℹ Local environment detected"
    USE_DOCKER=false
fi
echo ""

# Stop Odoo
echo "3. Stopping Odoo..."
if [ "$USE_DOCKER" = true ]; then
    docker-compose down
    echo "   ✓ Docker containers stopped"
else
    if pgrep -f "odoo-bin" > /dev/null; then
        pkill -f odoo-bin
        sleep 2
        echo "   ✓ Odoo stopped"
    else
        echo "   ✓ Odoo not running"
    fi
fi
echo ""

# Upgrade module
echo "4. Upgrading nexaml module..."
if [ "$USE_DOCKER" = true ]; then
    echo "   Running upgrade in Docker..."
    docker-compose run --rm odoo odoo -u nexaml --stop-after-init
    echo "   ✓ Module upgraded"
else
    echo "   ⚠ Manual upgrade required:"
    echo ""
    echo "   Option 1: Via Odoo UI"
    echo "     1. Start Odoo"
    echo "     2. Go to Apps menu"
    echo "     3. Remove 'Apps' filter"
    echo "     4. Search 'nexaml'"
    echo "     5. Click 'Upgrade'"
    echo ""
    echo "   Option 2: Via command line (if DB configured)"
    echo "     ./odoo-bin -c odoo.conf -d YOUR_DB_NAME -u nexaml --stop-after-init"
fi
echo ""

echo "5. Latest changes:"
echo "   ✓ Output Format field removed from UI"
echo "   ✓ Format auto-determined: BASIC→XLSX, Regulatory→XML"
echo "   ✓ Case selection OPTIONAL for all reports"
echo "   ✓ Advanced filtering auto-discovers cases"
echo "   ✓ 30+ optional filter fields available"
echo ""

echo "=== Next Steps ==="
if [ "$USE_DOCKER" = true ]; then
    echo "Start Odoo with: docker-compose up -d"
else
    echo "Start Odoo and upgrade the module via UI (Apps > NexAML > Upgrade)"
fi
echo ""
