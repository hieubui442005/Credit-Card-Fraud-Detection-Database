# Credit-Card-Fraud-Detection-Database

Thiết lập nhanh VoltDB cho bộ dữ liệu `data/transaction.csv` (Kaggle Fraud Dataset).

## 1) Cài đặt VoltDB (qua Docker)

```bash
docker pull full360/docker-voltdb-ce:latest
docker run -d --name voltdb-fraud -p 21212:21212 -p 8080:8080 full360/docker-voltdb-ce:latest
```

- SQL client port: `21212`
- VoltDB Web UI: `http://localhost:8080`

## 2) Tạo bảng trong VoltDB

```bash
docker exec -i voltdb-fraud /usr/local/opt/voltdb/6.4/bin/sqlcmd < voltdb/schema.sql
```

## 3) Nạp dữ liệu CSV vào bảng

```bash
awk -F',' 'NR==1 || NF==11' data/transaction.csv > /tmp/transaction.clean.csv
docker cp /tmp/transaction.clean.csv voltdb-fraud:/tmp/transaction.csv
rm -f /tmp/transaction.clean.csv

docker exec -it voltdb-fraud /usr/local/opt/voltdb/6.4/bin/csvloader \
  --servers=localhost \
  --port=21212 \
  --file=/tmp/transaction.csv \
  --skip=1 \
  --separator=, \
  TRANSACTION_TXN
```

## 4) Kiểm tra dữ liệu

```bash
docker exec -it voltdb-fraud /usr/local/opt/voltdb/6.4/bin/sqlcmd \
  --query="SELECT COUNT(*) AS total_rows FROM TRANSACTION_TXN;"

docker exec -it voltdb-fraud /usr/local/opt/voltdb/6.4/bin/sqlcmd \
  --query="SELECT isFraud, COUNT(*) AS cnt FROM TRANSACTION_TXN GROUP BY isFraud ORDER BY isFraud;"
```

## 5) Dừng/xóa container

```bash
docker stop voltdb-fraud
docker rm voltdb-fraud
```
