-- ============================================================================
-- SHOP MANAGEMENT SYSTEM - COMPLETE MASTER DATABASE & STORED PROCEDURES SCRIPT
-- ============================================================================
-- Database Engine : MySQL 8.0+ / MariaDB 10.4+
-- Character Set   : utf8mb4 (Full Unicode / Emoji / Multilingual Support)
-- Collation       : utf8mb4_unicode_ci
-- Execution Order : Run this script once on a fresh or existing MySQL instance.
--                   It creates the database, all tables, indexes, seed records,
--                   and all 19 Stored Procedures required by the application.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- STEP 1: CREATE & SELECT DATABASE
-- ----------------------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS ShopManagementDB
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE ShopManagementDB;

-- ----------------------------------------------------------------------------
-- STEP 2: CREATE CORE SCHEMA TABLES
-- ----------------------------------------------------------------------------

-- 1. Stores Table (Branch Locations)
CREATE TABLE IF NOT EXISTS Stores (
    StoreId      INT AUTO_INCREMENT PRIMARY KEY,
    StoreName    VARCHAR(200) NOT NULL,
    StoreCode    VARCHAR(50)  NOT NULL UNIQUE,
    Address      VARCHAR(500) NULL,
    Phone        VARCHAR(20)  NULL,
    Email        VARCHAR(150) NULL,
    IsActive     TINYINT(1)   NOT NULL DEFAULT 1,
    CreatedDate  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedDate  DATETIME     NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Users Table (Admin & Cashier Staff)
CREATE TABLE IF NOT EXISTS Users (
    UserId       INT AUTO_INCREMENT PRIMARY KEY,
    Name         VARCHAR(100) NOT NULL,
    Username     VARCHAR(100) NOT NULL UNIQUE,
    PasswordHash VARCHAR(255) NOT NULL,
    Role         VARCHAR(20)  NOT NULL, -- 'Admin', 'Employee'
    StoreId      INT          NULL,
    IsActive     TINYINT(1)   NOT NULL DEFAULT 1,
    CreatedDate  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedDate  DATETIME     NULL,
    CONSTRAINT FK_Users_Stores FOREIGN KEY (StoreId) REFERENCES Stores(StoreId) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Products Table (Inventory & Pricing)
CREATE TABLE IF NOT EXISTS Products (
    ProductId    INT AUTO_INCREMENT PRIMARY KEY,
    ProductCode  VARCHAR(50)    NOT NULL UNIQUE,
    ProductName  VARCHAR(200)   NOT NULL,
    Quantity     INT            NOT NULL DEFAULT 0,
    Price        DECIMAL(18,2)  NOT NULL DEFAULT 0.00,
    ImagePath    VARCHAR(500)   NULL,
    IsActive     TINYINT(1)     NOT NULL DEFAULT 1,
    CreatedDate  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedDate  DATETIME       NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Invoices Table (Billing Headers)
CREATE TABLE IF NOT EXISTS Invoices (
    InvoiceId     INT AUTO_INCREMENT PRIMARY KEY,
    InvoiceNo     VARCHAR(30)    NOT NULL UNIQUE,
    CustomerName  VARCHAR(150)   NOT NULL,
    CustomerPhone VARCHAR(20)    NULL,
    CreatedBy     INT            NOT NULL,
    StoreId       INT            NULL,
    InvoiceDate   DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    TotalAmount   DECIMAL(18,2)  NOT NULL DEFAULT 0.00,
    CONSTRAINT FK_Invoices_Users FOREIGN KEY (CreatedBy) REFERENCES Users(UserId),
    CONSTRAINT FK_Invoices_Stores FOREIGN KEY (StoreId) REFERENCES Stores(StoreId) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Invoice Details Table (Billing Line Items)
CREATE TABLE IF NOT EXISTS InvoiceDetails (
    InvoiceDetailId INT AUTO_INCREMENT PRIMARY KEY,
    InvoiceId       INT            NOT NULL,
    ProductId       INT            NOT NULL,
    ProductName     VARCHAR(200)   NOT NULL,
    Quantity        INT            NOT NULL,
    UnitPrice       DECIMAL(18,2)  NOT NULL,
    TotalAmount     DECIMAL(18,2)  NOT NULL,
    CONSTRAINT FK_InvoiceDetails_Invoices FOREIGN KEY (InvoiceId) REFERENCES Invoices(InvoiceId) ON DELETE CASCADE,
    CONSTRAINT FK_InvoiceDetails_Products FOREIGN KEY (ProductId) REFERENCES Products(ProductId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- STEP 3: PERFORMANCE INDEXES
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_users_username ON Users(Username);
CREATE INDEX IF NOT EXISTS idx_users_role_active ON Users(Role, IsActive);
CREATE INDEX IF NOT EXISTS idx_products_code ON Products(ProductCode);
CREATE INDEX IF NOT EXISTS idx_products_active ON Products(IsActive);
CREATE INDEX IF NOT EXISTS idx_invoices_no ON Invoices(InvoiceNo);
CREATE INDEX IF NOT EXISTS idx_invoices_createdby ON Invoices(CreatedBy);
CREATE INDEX IF NOT EXISTS idx_invoices_store ON Invoices(StoreId);
CREATE INDEX IF NOT EXISTS idx_invoices_date ON Invoices(InvoiceDate);
CREATE INDEX IF NOT EXISTS idx_invoicedetails_invoiceid ON InvoiceDetails(InvoiceId);
CREATE INDEX IF NOT EXISTS idx_invoicedetails_productid ON InvoiceDetails(ProductId);

-- ----------------------------------------------------------------------------
-- STEP 4: INITIAL SEED DATA
-- ----------------------------------------------------------------------------

-- Default Store Branch
INSERT IGNORE INTO Stores (StoreId, StoreName, StoreCode, Address, Phone, Email, IsActive)
VALUES (1, 'Main Branch', 'MAIN01', '123 Market Road, City Centre', '9800000001', 'main@shopdesk.local', 1);

-- Default Users (Admin & Cashier)
INSERT IGNORE INTO Users (UserId, Name, Username, PasswordHash, Role, StoreId, IsActive)
VALUES 
(1, 'System Admin', 'admin', 'admin123', 'Admin', 1, 1),
(2, 'Desk Cashier', 'desk1', 'desk123', 'Employee', 1, 1);

-- Default Starter Products
INSERT IGNORE INTO Products (ProductId, ProductCode, ProductName, Quantity, Price, ImagePath, IsActive)
VALUES 
(1, 'P001', 'Parker Roller Ball Pen', 100, 150.00, '/images/products/pen.png', 1),
(2, 'P002', 'Classmate Spiral Notebook A4', 50, 85.00, '/images/products/notebook.png', 1),
(3, 'P003', 'Apsara Platinum Pencil Set', 120, 45.00, '/images/products/pencil.png', 1),
(4, 'P004', 'Camlin Neon Highlighter Pack', 60, 110.00, '/images/products/highlighter.png', 1),
(5, 'P005', 'Casio Desk Calculator', 35, 450.00, '/images/products/calculator.png', 1);

-- ----------------------------------------------------------------------------
-- STEP 5: STORED PROCEDURES (19 ENTERPRISE PROCEDURES)
-- ----------------------------------------------------------------------------
DELIMITER //

-- ============================================================================
-- MODULE 1: AUTHENTICATION & ACCOUNT
-- ============================================================================

DROP PROCEDURE IF EXISTS sp_ValidateUser//
CREATE PROCEDURE sp_ValidateUser(
    IN p_Username VARCHAR(100),
    IN p_Password VARCHAR(255)
)
BEGIN
    SELECT UserId, Name, Username, Role, StoreId, IsActive 
    FROM Users 
    WHERE Username = p_Username AND PasswordHash = p_Password AND IsActive = 1;
END//

-- ============================================================================
-- MODULE 2: EMPLOYEE MANAGEMENT
-- ============================================================================

DROP PROCEDURE IF EXISTS sp_GetAllEmployees//
CREATE PROCEDURE sp_GetAllEmployees()
BEGIN
    SELECT u.UserId, u.Name, u.Username, u.Role, u.IsActive, u.CreatedDate,
           u.StoreId, COALESCE(s.StoreName, 'Main Branch') AS StoreName
    FROM Users u
    LEFT JOIN Stores s ON s.StoreId = u.StoreId
    WHERE u.Role = 'Employee'
    ORDER BY u.UserId DESC;
END//

DROP PROCEDURE IF EXISTS sp_GetEmployeeById//
CREATE PROCEDURE sp_GetEmployeeById(
    IN p_UserId INT
)
BEGIN
    SELECT u.UserId, u.Name, u.Username, u.Role, u.IsActive, u.StoreId,
           COALESCE(s.StoreName, 'Main Branch') AS StoreName
    FROM Users u
    LEFT JOIN Stores s ON s.StoreId = u.StoreId
    WHERE u.UserId = p_UserId;
END//

DROP PROCEDURE IF EXISTS sp_CreateEmployee//
CREATE PROCEDURE sp_CreateEmployee(
    IN p_Name VARCHAR(100),
    IN p_Username VARCHAR(100),
    IN p_Password VARCHAR(255),
    IN p_StoreId INT
)
BEGIN
    INSERT INTO Users (Name, Username, PasswordHash, Role, StoreId, IsActive, CreatedDate)
    VALUES (p_Name, p_Username, p_Password, 'Employee', p_StoreId, 1, NOW());
END//

DROP PROCEDURE IF EXISTS sp_UpdateEmployee//
CREATE PROCEDURE sp_UpdateEmployee(
    IN p_UserId INT,
    IN p_Name VARCHAR(100),
    IN p_Password VARCHAR(255),
    IN p_IsActive TINYINT(1),
    IN p_StoreId INT
)
BEGIN
    IF p_Password IS NOT NULL AND TRIM(p_Password) <> '' THEN
        UPDATE Users 
        SET Name = p_Name, 
            PasswordHash = p_Password, 
            IsActive = p_IsActive, 
            StoreId = p_StoreId, 
            UpdatedDate = NOW() 
        WHERE UserId = p_UserId;
    ELSE
        UPDATE Users 
        SET Name = p_Name, 
            IsActive = p_IsActive, 
            StoreId = p_StoreId, 
            UpdatedDate = NOW() 
        WHERE UserId = p_UserId;
    END IF;
END//

DROP PROCEDURE IF EXISTS sp_ResetEmployeePassword//
CREATE PROCEDURE sp_ResetEmployeePassword(
    IN p_UserId INT,
    IN p_Password VARCHAR(255)
)
BEGIN
    UPDATE Users 
    SET PasswordHash = p_Password, 
        UpdatedDate = NOW() 
    WHERE UserId = p_UserId;
END//

DROP PROCEDURE IF EXISTS sp_ToggleEmployeeStatus//
CREATE PROCEDURE sp_ToggleEmployeeStatus(
    IN p_UserId INT
)
BEGIN
    UPDATE Users 
    SET IsActive = CASE WHEN IsActive = 1 THEN 0 ELSE 1 END, 
        UpdatedDate = NOW() 
    WHERE UserId = p_UserId;
END//

DROP PROCEDURE IF EXISTS sp_DeleteEmployee//
CREATE PROCEDURE sp_DeleteEmployee(
    IN p_UserId INT
)
BEGIN
    UPDATE Users 
    SET IsActive = 0, 
        UpdatedDate = NOW() 
    WHERE UserId = p_UserId;
END//

-- ============================================================================
-- MODULE 3: STORE BRANCH MANAGEMENT
-- ============================================================================

DROP PROCEDURE IF EXISTS sp_GetAllStores//
CREATE PROCEDURE sp_GetAllStores(
    IN p_ActiveOnly BOOLEAN
)
BEGIN
    IF p_ActiveOnly THEN
        SELECT StoreId, StoreCode, StoreName, Address, Phone, Email, IsActive, CreatedDate
        FROM Stores 
        WHERE IsActive = 1 
        ORDER BY StoreName ASC;
    ELSE
        SELECT StoreId, StoreCode, StoreName, Address, Phone, Email, IsActive, CreatedDate
        FROM Stores 
        ORDER BY StoreId DESC;
    END IF;
END//

DROP PROCEDURE IF EXISTS sp_GetStoreById//
CREATE PROCEDURE sp_GetStoreById(
    IN p_StoreId INT
)
BEGIN
    SELECT StoreId, StoreCode, StoreName, Address, Phone, Email, IsActive 
    FROM Stores 
    WHERE StoreId = p_StoreId;
END//

DROP PROCEDURE IF EXISTS sp_CreateStore//
CREATE PROCEDURE sp_CreateStore(
    IN p_StoreCode VARCHAR(50),
    IN p_StoreName VARCHAR(200),
    IN p_Address   VARCHAR(500),
    IN p_Phone     VARCHAR(20),
    IN p_Email     VARCHAR(150)
)
BEGIN
    INSERT INTO Stores (StoreCode, StoreName, Address, Phone, Email, IsActive, CreatedDate)
    VALUES (p_StoreCode, p_StoreName, p_Address, p_Phone, p_Email, 1, NOW());
END//

DROP PROCEDURE IF EXISTS sp_UpdateStore//
CREATE PROCEDURE sp_UpdateStore(
    IN p_StoreId   INT,
    IN p_StoreName VARCHAR(200),
    IN p_Address   VARCHAR(500),
    IN p_Phone     VARCHAR(20),
    IN p_Email     VARCHAR(150),
    IN p_IsActive  TINYINT(1)
)
BEGIN
    UPDATE Stores 
    SET StoreName = p_StoreName, 
        Address = p_Address, 
        Phone = p_Phone, 
        Email = p_Email, 
        IsActive = p_IsActive, 
        UpdatedDate = NOW()
    WHERE StoreId = p_StoreId;
END//

DROP PROCEDURE IF EXISTS sp_DeleteStore//
CREATE PROCEDURE sp_DeleteStore(
    IN p_StoreId INT
)
BEGIN
    UPDATE Stores 
    SET IsActive = 0, 
        UpdatedDate = NOW() 
    WHERE StoreId = p_StoreId;
END//

DROP PROCEDURE IF EXISTS sp_GetStoreStats//
CREATE PROCEDURE sp_GetStoreStats()
BEGIN
    SELECT 
        s.StoreId, s.StoreName, s.StoreCode, s.IsActive,
        COUNT(DISTINCT u.UserId) AS TotalEmployees,
        COUNT(DISTINCT i.InvoiceId) AS TotalInvoices,
        COALESCE(SUM(i.TotalAmount), 0) AS TotalRevenue
    FROM Stores s
    LEFT JOIN Users u ON u.StoreId = s.StoreId AND u.Role = 'Employee' AND u.IsActive = 1
    LEFT JOIN Invoices i ON i.StoreId = s.StoreId
    GROUP BY s.StoreId, s.StoreName, s.StoreCode, s.IsActive
    ORDER BY s.StoreId ASC;
END//

-- ============================================================================
-- MODULE 4: PRODUCT & INVENTORY MANAGEMENT
-- ============================================================================

DROP PROCEDURE IF EXISTS sp_GetAllProducts//
CREATE PROCEDURE sp_GetAllProducts(
    IN p_ActiveOnly BOOLEAN
)
BEGIN
    IF p_ActiveOnly THEN
        SELECT ProductId, ProductCode, ProductName, Quantity, Price, ImagePath, IsActive, CreatedDate, UpdatedDate 
        FROM Products 
        WHERE IsActive = 1 
        ORDER BY ProductId DESC;
    ELSE
        SELECT ProductId, ProductCode, ProductName, Quantity, Price, ImagePath, IsActive, CreatedDate, UpdatedDate 
        FROM Products 
        ORDER BY ProductId DESC;
    END IF;
END//

DROP PROCEDURE IF EXISTS sp_GetProductById//
CREATE PROCEDURE sp_GetProductById(
    IN p_ProductId INT
)
BEGIN
    SELECT ProductId, ProductCode, ProductName, Quantity, Price, ImagePath, IsActive 
    FROM Products 
    WHERE ProductId = p_ProductId;
END//

DROP PROCEDURE IF EXISTS sp_CheckProductExists//
CREATE PROCEDURE sp_CheckProductExists(
    IN p_ProductCode VARCHAR(50),
    IN p_ProductName VARCHAR(200)
)
BEGIN
    SELECT ProductId, ProductCode, ProductName, Quantity, Price, ImagePath 
    FROM Products 
    WHERE ProductCode = p_ProductCode OR LOWER(ProductName) = LOWER(p_ProductName) 
    LIMIT 1;
END//

DROP PROCEDURE IF EXISTS sp_CreateProduct//
CREATE PROCEDURE sp_CreateProduct(
    IN p_ProductCode VARCHAR(50),
    IN p_ProductName VARCHAR(200),
    IN p_Quantity    INT,
    IN p_Price       DECIMAL(18,2),
    IN p_ImagePath   VARCHAR(500)
)
BEGIN
    INSERT INTO Products (ProductCode, ProductName, Quantity, Price, ImagePath, IsActive, CreatedDate)
    VALUES (p_ProductCode, p_ProductName, p_Quantity, p_Price, p_ImagePath, 1, NOW());
END//

DROP PROCEDURE IF EXISTS sp_UpdateProduct//
CREATE PROCEDURE sp_UpdateProduct(
    IN p_ProductId   INT,
    IN p_ProductName VARCHAR(200),
    IN p_Quantity    INT,
    IN p_Price       DECIMAL(18,2),
    IN p_ImagePath   VARCHAR(500)
)
BEGIN
    IF p_ImagePath IS NOT NULL AND TRIM(p_ImagePath) <> '' THEN
        UPDATE Products
        SET ProductName = p_ProductName, 
            Quantity = p_Quantity, 
            Price = p_Price, 
            ImagePath = p_ImagePath, 
            UpdatedDate = NOW()
        WHERE ProductId = p_ProductId;
    ELSE
        UPDATE Products
        SET ProductName = p_ProductName, 
            Quantity = p_Quantity, 
            Price = p_Price, 
            UpdatedDate = NOW()
        WHERE ProductId = p_ProductId;
    END IF;
END//

DROP PROCEDURE IF EXISTS sp_DeleteProduct//
CREATE PROCEDURE sp_DeleteProduct(
    IN p_ProductId INT
)
BEGIN
    UPDATE Products 
    SET IsActive = 0, 
        UpdatedDate = NOW() 
    WHERE ProductId = p_ProductId;
END//

DROP PROCEDURE IF EXISTS sp_SearchAvailableProducts//
CREATE PROCEDURE sp_SearchAvailableProducts(
    IN p_Term VARCHAR(100)
)
BEGIN
    SELECT ProductId, ProductCode, ProductName, Quantity, Price, ImagePath
    FROM Products
    WHERE IsActive = 1 AND Quantity > 0
      AND (ProductName LIKE CONCAT('%', p_Term, '%') OR ProductCode LIKE CONCAT('%', p_Term, '%'))
    ORDER BY ProductName ASC;
END//

-- ============================================================================
-- MODULE 5: INVOICE & POINT OF SALE (POS)
-- ============================================================================

DROP PROCEDURE IF EXISTS sp_GetInvoiceHistory//
CREATE PROCEDURE sp_GetInvoiceHistory(
    IN p_CreatedBy INT
)
BEGIN
    IF p_CreatedBy IS NULL OR p_CreatedBy <= 0 THEN
        SELECT 
            i.InvoiceId, i.InvoiceNo, i.CustomerName, i.CustomerPhone, 
            i.TotalAmount, i.InvoiceDate, u.Name AS CreatedByName, u.Role AS CreatedByRole
        FROM Invoices i
        INNER JOIN Users u ON i.CreatedBy = u.UserId
        ORDER BY i.InvoiceId DESC;
    ELSE
        SELECT 
            i.InvoiceId, i.InvoiceNo, i.CustomerName, i.CustomerPhone, 
            i.TotalAmount, i.InvoiceDate, u.Name AS CreatedByName, u.Role AS CreatedByRole
        FROM Invoices i
        INNER JOIN Users u ON i.CreatedBy = u.UserId
        WHERE i.CreatedBy = p_CreatedBy
        ORDER BY i.InvoiceId DESC;
    END IF;
END//

DROP PROCEDURE IF EXISTS sp_GetInvoiceHeader//
CREATE PROCEDURE sp_GetInvoiceHeader(
    IN p_InvoiceId INT
)
BEGIN
    SELECT 
        i.InvoiceId, i.InvoiceNo, i.CustomerName, i.CustomerPhone, 
        i.TotalAmount, i.InvoiceDate, u.Name AS CreatedByName, u.Username AS CreatedByUsername
    FROM Invoices i
    INNER JOIN Users u ON i.CreatedBy = u.UserId
    WHERE i.InvoiceId = p_InvoiceId;
END//

DROP PROCEDURE IF EXISTS sp_GetInvoiceDetails//
CREATE PROCEDURE sp_GetInvoiceDetails(
    IN p_InvoiceId INT
)
BEGIN
    SELECT 
        d.InvoiceDetailId, d.InvoiceId, d.ProductId, d.ProductName, 
        d.Quantity, d.UnitPrice, d.TotalAmount, p.ProductCode, p.ImagePath
    FROM InvoiceDetails d
    LEFT JOIN Products p ON d.ProductId = p.ProductId
    WHERE d.InvoiceId = p_InvoiceId;
END//

-- Transaction Step 1: Stock Validation & Row-Level Lock
DROP PROCEDURE IF EXISTS sp_CheckProductStock//
CREATE PROCEDURE sp_CheckProductStock(
    IN p_ProductId INT
)
BEGIN
    SELECT ProductId, ProductName, Quantity
    FROM Products
    WHERE ProductId = p_ProductId AND IsActive = 1
    FOR UPDATE;
END//

-- Transaction Step 2: Insert Invoice Master Header
DROP PROCEDURE IF EXISTS sp_InsertInvoiceHeader//
CREATE PROCEDURE sp_InsertInvoiceHeader(
    IN p_InvoiceNo      VARCHAR(30),
    IN p_CustomerName   VARCHAR(150),
    IN p_CustomerPhone  VARCHAR(20),
    IN p_CreatedBy      INT,
    IN p_TotalAmount    DECIMAL(18,2)
)
BEGIN
    INSERT INTO Invoices (InvoiceNo, CustomerName, CustomerPhone, CreatedBy, InvoiceDate, TotalAmount)
    VALUES (p_InvoiceNo, p_CustomerName, p_CustomerPhone, p_CreatedBy, NOW(), p_TotalAmount);
    SELECT LAST_INSERT_ID() AS NewInvoiceId;
END//

-- Transaction Step 3: Insert Invoice Item Detail
DROP PROCEDURE IF EXISTS sp_InsertInvoiceDetail//
CREATE PROCEDURE sp_InsertInvoiceDetail(
    IN p_InvoiceId    INT,
    IN p_ProductId    INT,
    IN p_ProductName  VARCHAR(200),
    IN p_Quantity     INT,
    IN p_UnitPrice    DECIMAL(18,2),
    IN p_TotalAmount  DECIMAL(18,2)
)
BEGIN
    INSERT INTO InvoiceDetails (InvoiceId, ProductId, ProductName, Quantity, UnitPrice, TotalAmount)
    VALUES (p_InvoiceId, p_ProductId, p_ProductName, p_Quantity, p_UnitPrice, p_TotalAmount);
END//

-- Transaction Step 4: Atomic Inventory Deduction
DROP PROCEDURE IF EXISTS sp_DeductProductStock//
CREATE PROCEDURE sp_DeductProductStock(
    IN p_ProductId INT,
    IN p_Quantity  INT
)
BEGIN
    UPDATE Products
    SET Quantity    = Quantity - p_Quantity,
        UpdatedDate = NOW()
    WHERE ProductId = p_ProductId;
END//

-- ============================================================================
-- MODULE 6: DASHBOARD & BUSINESS ANALYTICS
-- ============================================================================

DROP PROCEDURE IF EXISTS sp_GetDashboardMetrics//
CREATE PROCEDURE sp_GetDashboardMetrics()
BEGIN
    SELECT 
        (SELECT COUNT(*) FROM Products WHERE IsActive = 1) AS TotalProducts,
        (SELECT COUNT(*) FROM Products WHERE IsActive = 1 AND Quantity <= 10) AS LowStockProducts,
        (SELECT COUNT(*) FROM Invoices) AS TotalInvoices,
        (SELECT COALESCE(SUM(TotalAmount), 0) FROM Invoices) AS TotalRevenue,
        (SELECT COUNT(*) FROM Users WHERE Role = 'Employee' AND IsActive = 1) AS TotalEmployees;
END//

DELIMITER ;

-- ----------------------------------------------------------------------------
-- STEP 6: VERIFICATION & SUMMARY REPORT
-- ----------------------------------------------------------------------------
SELECT 'ShopManagementDB Database Setup Complete!' AS Status;

-- Check Tables
SELECT TABLE_NAME, TABLE_ROWS, DATA_LENGTH, INDEX_LENGTH
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'ShopManagementDB';

-- Check Stored Procedures Count
SELECT ROUTINE_NAME, ROUTINE_TYPE, CREATED
FROM information_schema.ROUTINES 
WHERE ROUTINE_SCHEMA = 'ShopManagementDB' 
ORDER BY ROUTINE_NAME ASC;
