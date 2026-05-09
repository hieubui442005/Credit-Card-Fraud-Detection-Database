#!/bin/bash

# Simple continuous monitoring
echo "🔄 Starting continuous monitoring... (Press Ctrl+C to stop)"
echo ""

INTERVAL=${1:-5}

while true; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⏱️  $(date '+%Y-%m-%d %H:%M:%S')"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Check container status
    CONTAINER_STATUS=$(docker ps -a --filter "name=data_loader" --format "{{.Status}}" 2>/dev/null)
    if [ -z "$CONTAINER_STATUS" ]; then
        echo "❌ Data loader container not found"
        break
    fi
    
    echo "📦 Container: $CONTAINER_STATUS"
    echo ""
    
    # Show last few lines of logs
    echo "📄 Last 15 log lines:"
    docker logs python_data_loader 2>&1 | tail -15 | sed 's/^/  /'
    
    # Show database counts
    echo ""
    echo "📊 Row Counts:"
    
    # MySQL
    MYSQL_COUNT=$(docker exec mysql_server mysql -uroot -ppassword fraud_db -e "SELECT COUNT(*) FROM TransactionData;" 2>/dev/null | tail -1)
    echo "  🟧 MySQL: $MYSQL_COUNT"
    
    # PostgreSQL
    PG_COUNT=$(docker exec postgres_server psql -U admin -d fraud_db -c "SELECT COUNT(*) FROM TransactionData;" 2>/dev/null | grep -E "^[[:space:]]*[0-9]" | head -1 | xargs)
    echo "  🟨 PostgreSQL: $PG_COUNT"
    
    # VoltDB
    echo "  🟦 VoltDB: checking..."
    
    echo ""
    sleep $INTERVAL
done
