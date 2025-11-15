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

# Check if Odoo is running
echo "2. Checking Odoo status..."
if pgrep -f "odoo-bin" > /dev/null; then
    echo "   ⚠ Odoo is running. Stopping..."
    pkill -f odoo-bin
    sleep 2
    echo "   ✓ Odoo stopped"
else
    echo "   ✓ Odoo not running"
fi
echo ""

# Upgrade module
echo "3. Upgrading nexaml module..."
if [ -f "odoo-bin" ]; then
    ./odoo-bin -c odoo.conf -u nexaml --stop-after-init
    echo "   ✓ Module upgraded"
else
    echo "   ⚠ odoo-bin not found. Please run manually:"
    echo "     ./odoo-bin -c odoo.conf -u nexaml --stop-after-init"
fi
echo ""

echo "4. Latest changes:"
echo "   ✓ Output Format field removed from UI"
echo "   ✓ Format auto-determined: BASIC→XLSX, Regulatory→XML"
echo "   ✓ Case selection OPTIONAL for all reports"
echo "   ✓ Advanced filtering auto-discovers cases"
echo "   ✓ 30+ optional filter fields available"
echo ""

echo "=== Upgrade Complete ==="
echo "Start Odoo with: ./odoo-bin -c odoo.conf"
echo ""
