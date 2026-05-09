-- ===== VoltDB Schema (Partitioned) =====
CREATE TABLE Account (
    account_id VARCHAR(50) NOT NULL,
    PRIMARY KEY (account_id)
);

PARTITION TABLE Account ON COLUMN account_id;

CREATE TABLE TransactionData (
    tx_id VARCHAR(50) NOT NULL,
    step INTEGER,
    type VARCHAR(20),
    amount FLOAT,
    nameOrig VARCHAR(50) NOT NULL,
    oldbalanceOrg FLOAT,
    newbalanceOrig FLOAT,
    nameDest VARCHAR(50),
    oldbalanceDest FLOAT,
    newbalanceDest FLOAT,
    isFraud TINYINT,
    isFlaggedFraud TINYINT,
    PRIMARY KEY (tx_id, nameOrig)
);

PARTITION TABLE TransactionData ON COLUMN nameOrig;

-- ===== PostgreSQL/MySQL Compatible Schema =====
-- CREATE TABLE Account (
--     account_id VARCHAR(50) NOT NULL PRIMARY KEY
-- );
--
-- CREATE TABLE TransactionData (
--     tx_id VARCHAR(50) NOT NULL,
--     step INTEGER,
--     type VARCHAR(20),
--     amount FLOAT,
--     nameOrig VARCHAR(50) NOT NULL,
--     oldbalanceOrg FLOAT,
--     newbalanceOrig FLOAT,
--     nameDest VARCHAR(50),
--     oldbalanceDest FLOAT,
--     newbalanceDest FLOAT,
--     isFraud TINYINT,
--     isFlaggedFraud TINYINT,
--     PRIMARY KEY (tx_id, nameOrig),
--     INDEX idx_nameOrig (nameOrig)
-- );
