-- ============================================================
-- DATABASE CREATION: ShopManagementDB
-- ============================================================
CREATE DATABASE IF NOT EXISTS ShopManagementDB
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE ShopManagementDB;

-- 1. STORES TABLE
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. USERS TABLE
CREATE TABLE IF NOT EXISTS Users (
    UserId INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Username VARCHAR(100) NOT NULL UNIQUE,
    PasswordHash VARCHAR(255) NOT NULL,
    Role VARCHAR(20) NOT NULL, -- 'Admin', 'Employee'
    StoreId INT NULL,
    IsActive TINYINT(1) NOT NULL DEFAULT 1,
    CreatedDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedDate DATETIME NULL,
    CONSTRAINT FK_Users_Stores FOREIGN KEY (StoreId) REFERENCES Stores(StoreId) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. PRODUCTS TABLE
CREATE TABLE IF NOT EXISTS Products (
    ProductId INT AUTO_INCREMENT PRIMARY KEY,
    ProductCode VARCHAR(50) NOT NULL UNIQUE,
    ProductName VARCHAR(200) NOT NULL,
    Quantity INT NOT NULL DEFAULT 0,
    Price DECIMAL(18,2) NOT NULL DEFAULT 0.00,
    ImagePath VARCHAR(500) NULL,
    IsActive TINYINT(1) NOT NULL DEFAULT 1,
    CreatedDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedDate DATETIME NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. INVOICES TABLE
CREATE TABLE IF NOT EXISTS Invoices (
    InvoiceId INT AUTO_INCREMENT PRIMARY KEY,
    InvoiceNo VARCHAR(30) NOT NULL UNIQUE,
    CustomerName VARCHAR(150) NOT NULL,
    CustomerPhone VARCHAR(20) NULL,
    CreatedBy INT NOT NULL,
    StoreId INT NULL,
    InvoiceDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    TotalAmount DECIMAL(18,2) NOT NULL DEFAULT 0.00,
    CONSTRAINT FK_Invoices_Users FOREIGN KEY (CreatedBy) REFERENCES Users(UserId),
    CONSTRAINT FK_Invoices_Stores FOREIGN KEY (StoreId) REFERENCES Stores(StoreId) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. INVOICE DETAILS TABLE
CREATE TABLE IF NOT EXISTS InvoiceDetails (
    InvoiceDetailId INT AUTO_INCREMENT PRIMARY KEY,
    InvoiceId INT NOT NULL,
    ProductId INT NOT NULL,
    ProductName VARCHAR(200) NOT NULL,
    Quantity INT NOT NULL,
    UnitPrice DECIMAL(18,2) NOT NULL,
    TotalAmount DECIMAL(18,2) NOT NULL,
    CONSTRAINT FK_InvoiceDetails_Invoices FOREIGN KEY (InvoiceId) REFERENCES Invoices(InvoiceId) ON DELETE CASCADE,
    CONSTRAINT FK_InvoiceDetails_Products FOREIGN KEY (ProductId) REFERENCES Products(ProductId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- INDEXES
CREATE INDEX IF NOT EXISTS idx_users_username ON Users(Username);
CREATE INDEX IF NOT EXISTS idx_users_role_active ON Users(Role, IsActive);
CREATE INDEX IF NOT EXISTS idx_products_code ON Products(ProductCode);
CREATE INDEX IF NOT EXISTS idx_invoices_no ON Invoices(InvoiceNo);
CREATE INDEX IF NOT EXISTS idx_invoices_createdby ON Invoices(CreatedBy);
CREATE INDEX IF NOT EXISTS idx_invoices_store ON Invoices(StoreId);

-- SEED DATA
-- Default Store
INSERT IGNORE INTO Stores (StoreId, StoreName, StoreCode, Address, Phone, Email, IsActive)
VALUES (1, 'Main Branch', 'MAIN01', '123 Market Road, City Centre', '9800000001', 'main@shopdesk.local', 1);

-- Default Admin and Employee (desk login)
INSERT IGNORE INTO Users (UserId, Name, Username, PasswordHash, Role, StoreId, IsActive)
VALUES 
(1, 'System Admin', 'admin', 'admin123', 'Admin', 1, 1),
(2, 'Desk Cashier', 'desk1', 'desk123', 'Employee', 1, 1);

-- Default Products
INSERT IGNORE INTO Products (ProductId, ProductCode, ProductName, Quantity, Price, ImagePath, IsActive)
VALUES 
(1, 'P001', 'Parker Roller Ball Pen', 100, 150.00, '/images/products/pen.png', 1),
(2, 'P002', 'Classmate Spiral Notebook A4', 50, 85.00, '/images/products/notebook.png', 1),
(3, 'P003', 'Apsara Platinum Pencil Set', 120, 45.00, '/images/products/pencil.png', 1),
(4, 'P004', 'Camlin Neon Highlighter Pack', 60, 110.00, '/images/products/highlighter.png', 1),
(5, 'P005', 'Casio Desk Calculator', 35, 450.00, '/images/products/calculator.png', 1);

-- NOTE: To deploy all Stored Procedures, execute StoredProcedures_Setup.sql or use the all-in-one ShopManagement_Full_Setup.sql.
