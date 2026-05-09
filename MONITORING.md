# 🚀 Theo dõi tiến độ chạy project

## 1️⃣ Kiểm tra trạng thái hiện tại (dễ nhất)

```bash
cd /workspaces/Credit-Card-Fraud-Detection-Database/voltdb_setup
bash check_progress.sh
```

**Output bạn sẽ thấy:**
```
📦 Data Loader Container: Up X minutes
✓ Data loader is RUNNING

====== DATABASE ROW COUNTS ======
🟦 VoltDB: TransactionCount: 100000
🟨 PostgreSQL: TransactionCount: 50000
🟧 MySQL: TransactionCount: 75000
✓ Dashboard is RUNNING at http://localhost:8501
```

---

## 2️⃣ Xem logs real-time của data loader

Xem tiến độ đang chạy:
```bash
docker logs python_data_loader -f
```

**Dùng Ctrl+C để dừng xem logs**

---

## 3️⃣ Khi nào chạy xong?

### ✅ Data loader hoàn tất khi bạn thấy:
```
✓ Hoàn thành nạp dữ liệu vào tất cả các cơ sở dữ liệu!
```

### ✅ Dashboard sẵn sàng:
- Tất cả database có số records = 100,000 (hoặc số lượng records trong CSV)
- Dashboard accessible tại http://localhost:8501

---

## 4️⃣ Cách khác để kiểm tra

### Truy cập trực tiếp từng database:

**MySQL:**
```bash
docker exec mysql_server mysql -uroot -ppassword fraud_db -e "SELECT COUNT(*) as total FROM TransactionData;"
```

**PostgreSQL:**
```bash
docker exec postgres_server psql -U admin -d fraud_db -c "SELECT COUNT(*) FROM TransactionData;"
```

**VoltDB:**
```bash
docker exec voltdb_server /opt/voltdb/bin/voltdb sqlcmd --query="SELECT COUNT(*) FROM TransactionData;"
```

---

## 5️⃣ Nếu muốn dừng mọi thứ

```bash
docker-compose down
```

---

## 📊 Timeline dự kiến

| Status | Thời gian |
|--------|----------|
| Khơi động containers | ~30 giây |
| Tạo schema | ~10 giây |
| Load 100,000 records | ~2-5 phút |
| **Sẵn sàng** | **3-5 phút** |

