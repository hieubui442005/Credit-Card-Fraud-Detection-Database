#!/bin/bash

echo "====== STATUS CHECK ======"
echo ""

# Check data loader status
echo "📦 Data Loader Container:"
docker ps -a --filter "name=data_loader" --format "Status: {{.Status}}"
echo ""

# Check if still running
if docker ps --filter "name=data_loader" -q > /dev/null 2>&1; then
    echo "✓ Data loader is RUNNING"
    echo ""
    echo "Recent logs:"
    docker logs python_data_loader 2>&1 | tail -20
else
    echo "✗ Data loader STOPPED/EXITED"
    echo ""
    echo "Exit reason from logs:"
    docker logs python_data_loader 2>&1 | tail -10
fi

echo ""
echo "====== DATABASE ROW COUNTS ======"
echo ""

# VoltDB count  
echo "🟦 VoltDB:"
docker exec voltdb_server voltdb sqlcmd --query="SELECT COUNT(*) as TransactionCount FROM TransactionData;" 2>/dev/null || echo "❌ Cannot connect"

# PostgreSQL count
echo ""
echo "🟨 PostgreSQL:"
docker exec postgres_server psql -U admin -d fraud_db -c "SELECT COUNT(*) as TransactionCount FROM TransactionData;" 2>/dev/null || echo "❌ Cannot connect or table doesn't exist"

# MySQL count
echo ""
echo "🟧 MySQL:"
docker exec mysql_server mysql -uroot -ppassword fraud_db -e "SELECT COUNT(*) as TransactionCount FROM TransactionData;" 2>/dev/null || echo "❌ Cannot connect or table doesn't exist"

echo ""
echo "====== STREAMLIT STATUS ======"
echo ""

# Check if Streamlit is running
if curl -s http://localhost:8501 > /dev/null 2>&1; then
    echo "✓ Dashboard is RUNNING at http://localhost:8501"
else
    echo "✗ Dashboard is NOT accessible"
fi
