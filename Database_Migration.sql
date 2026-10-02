-- ============================================================
-- MIGRATION SCRIPT: Add Stores table + update schema
-- ============================================================
USE ShopManagementDB;

-- 5. STORES TABLE
CREATE TABLE IF NOT EXISTS Stores (
    StoreId INT AUTO_INCREMENT PRIMARY KEY,
    StoreName VARCHAR(200) NOT NULL,
    StoreCode VARCHAR(50) NOT NULL UNIQUE,
    Address VARCHAR(500) NULL,
    Phone VARCHAR(20) NULL,
    Email VARCHAR(150) NULL,
    IsActive TINYINT(1) NOT NULL DEFAULT 1,
    CreatedDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedDate DATETIME NULL
);

-- Add StoreId to Users safely
SET @col_exists = (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'ShopManagementDB' AND TABLE_NAME = 'Users' AND COLUMN_NAME = 'StoreId'
);
SET @sql = IF(@col_exists = 0,
    'ALTER TABLE Users ADD COLUMN StoreId INT NULL AFTER Role',
    'SELECT ''StoreId already exists in Users''');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add FK for Users->Stores (only if not exists)
SET @fk_exists = (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
    WHERE TABLE_SCHEMA = 'ShopManagementDB' AND TABLE_NAME = 'Users' AND CONSTRAINT_NAME = 'FK_Users_Stores'
);
SET @sql2 = IF(@fk_exists = 0,
    'ALTER TABLE Users ADD CONSTRAINT FK_Users_Stores FOREIGN KEY (StoreId) REFERENCES Stores(StoreId)',
    'SELECT ''FK_Users_Stores already exists''');
PREPARE stmt2 FROM @sql2;
EXECUTE stmt2;
DEALLOCATE PREPARE stmt2;

-- Add StoreId to Invoices safely
SET @col2_exists = (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'ShopManagementDB' AND TABLE_NAME = 'Invoices' AND COLUMN_NAME = 'StoreId'
);
SET @sql3 = IF(@col2_exists = 0,
    'ALTER TABLE Invoices ADD COLUMN StoreId INT NULL AFTER TotalAmount',
    'SELECT ''StoreId already exists in Invoices''');
PREPARE stmt3 FROM @sql3;
EXECUTE stmt3;
DEALLOCATE PREPARE stmt3;

-- Add FK for Invoices->Stores
SET @fk2_exists = (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
    WHERE TABLE_SCHEMA = 'ShopManagementDB' AND TABLE_NAME = 'Invoices' AND CONSTRAINT_NAME = 'FK_Invoices_Stores'
);
SET @sql4 = IF(@fk2_exists = 0,
    'ALTER TABLE Invoices ADD CONSTRAINT FK_Invoices_Stores FOREIGN KEY (StoreId) REFERENCES Stores(StoreId)',
    'SELECT ''FK_Invoices_Stores already exists''');
PREPARE stmt4 FROM @sql4;
EXECUTE stmt4;
DEALLOCATE PREPARE stmt4;

-- Seed default store
INSERT IGNORE INTO Stores (StoreId, StoreName, StoreCode, Address, Phone, Email, IsActive)
VALUES (1, 'Main Branch', 'MAIN01', '123 Market Road, City Centre', '9800000001', 'main@shopdesk.local', 1);

-- Link existing employee (desk1) to default store
UPDATE Users SET StoreId = 1 WHERE UserId = 2 AND StoreId IS NULL;
