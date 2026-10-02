# 🏪 Shop Management System (3-Tier Enterprise Architecture) — Complete Project Guide & Documentation

> **Project Architecture:** ASP.NET Core MVC (.NET 10) + Business Access Layer (BAL) + Data Access Layer (DAL) + MySQL 8.0 Database  
> **Database Layer:** 100% Stored Procedure Driven (`ShopManagement_Full_Setup.sql`), ACID compliant transactions, Row-level Locks (`FOR UPDATE`)  
> **Frontend Stack:** Vanilla JS + jQuery + Kendo UI Grids + Bootstrap 5 + SweetAlert2 (Modular files in `wwwroot/js/`)  
> **Key Capabilities:** Multi-Role (Admin & Desk Cashier), Dynamic POS Billing with Real-time Stock Deduction, Product Upsert (Auto-stock merge), Excel Bulk Import/Export via ClosedXML, Multi-branch Stores, Invoice Printing.

---

## 📑 Table of Contents

1. [Architecture & System Flow Overview](#1-architecture--system-flow-overview)
2. [Database Design & Complete SQL Scripts (`ShopManagement_Full_Setup.sql`)](#2-database-design--complete-sql-scripts)
3. [Step-by-Step Project Creation from Scratch](#3-step-by-step-project-creation-from-scratch)
4. [Complete Solution Folder Structure](#4-complete-solution-folder-structure)
5. [Layer-by-Layer Complete Active Source Code](#5-layer-by-layer-complete-active-source-code)
   - [5.1 Data Access Layer (ShopManagement.DataAccess)](#51-data-access-layer-shopmanagementdataaccess)
   - [5.2 Business Access Layer (ShopManagement.Business)](#52-business-access-layer-shopmanagementbusiness)
   - [5.3 Web Presentation Layer (ShopManagement.Web)](#53-web-presentation-layer-shopmanagementweb)
6. [Architectural Decisions & Data Flow Lifecycle](#6-architectural-decisions--data-flow-lifecycle)
7. [Step-by-Step Setup, Build & Run Guide](#7-step-by-step-setup-build--run-guide)

---

# 1. Architecture & System Flow Overview

The system follows a strict **3-Tier Separation of Concerns** design pattern:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER (ShopManagement.Web)              │
│  - ASP.NET Core MVC Controllers & Razor Views                          │
│  - Separated JS modules (employee.js, product.js, invoice-create.js)   │
│  - Kendo UI Grids, SweetAlert2, Bootstrap 5 UI, AJAX Endpoints         │
│  - Session-based Authentication & Role authorization (Admin/Employee)  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Calls BAL methods)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER (ShopManagement.Business)       │
│  - Input validation, Sanitization, Business calculations               │
│  - Stock thresholds & Upsert logic handling                            │
│  - ClosedXML Excel streaming and batch parsing                         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Calls DAL methods)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   DATA ACCESS LAYER (ShopManagement.DataAccess)        │
│  - Lightweight DbHelper (Zero embedded SQL procedure bloat)            │
│  - Parameterized MySqlConnector calls to Stored Procedures             │
│  - Database Transactions (ACID compliance with FOR UPDATE row locks)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (MySQL Port: 3306)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         MYSQL DATABASE (ShopManagementDB)              │
│  - Tables: Stores, Users, Products, Invoices, InvoiceDetails           │
│  - All 19 Stored Procedures (CRUD, Stock Check, Invoicing, Metrics)    │
│  - Foreign Keys, Auto-increments, Unique Indexes                       │
└────────────────────────────────────────────────────────────────────────┘
```

---

# 2. Database Design & Complete SQL Scripts

### Complete Master SQL Setup Script (`ShopManagement_Full_Setup.sql`)
```sql
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

```

---

# 5. Layer-by-Layer Complete Active Source Code

## 5.1 Data Access Layer (ShopManagement.DataAccess)

### 5.1.1 `DbHelper.cs`
```csharp
using System;
using System.Data;
using MySqlConnector;

namespace ShopManagement.DataAccess
{
    /// <summary>
    /// Lightweight, high-performance database helper for MySQL operations.
    /// Executes plain SQL text and Stored Procedures via ADO.NET and MySqlConnector.
    /// Stored Procedure definitions are maintained centrally in the master SQL setup script.
    /// </summary>
    public static class DbHelper
    {
        public static string ConnectionString { get; set; } = "Server=localhost;Database=ShopManagementDB;User ID=root;Password=root;Port=3306;AllowUserVariables=True;";

        public static MySqlConnection GetConnection()
        {
            var conn = new MySqlConnection(ConnectionString);
            if (conn.State != ConnectionState.Open)
            {
                conn.Open();
            }
            return conn;
        }

        public static DataTable ExecuteDataTable(string query, MySqlParameter[] parameters = null, CommandType commandType = CommandType.Text)
        {
            var dt = new DataTable();
            using (var conn = GetConnection())
            using (var cmd = new MySqlCommand(query, conn))
            {
                cmd.CommandType = commandType;
                if (parameters != null && parameters.Length > 0)
                {
                    cmd.Parameters.AddRange(parameters);
                }

                using (var adapter = new MySqlDataAdapter(cmd))
                {
                    adapter.Fill(dt);
                }
            }
            return dt;
        }

        public static int ExecuteNonQuery(string query, MySqlParameter[] parameters = null, CommandType commandType = CommandType.Text)
        {
            using (var conn = GetConnection())
            using (var cmd = new MySqlCommand(query, conn))
            {
                cmd.CommandType = commandType;
                if (parameters != null && parameters.Length > 0)
                {
                    cmd.Parameters.AddRange(parameters);
                }
                return cmd.ExecuteNonQuery();
            }
        }

        public static object ExecuteScalar(string query, MySqlParameter[] parameters = null, CommandType commandType = CommandType.Text)
        {
            using (var conn = GetConnection())
            using (var cmd = new MySqlCommand(query, conn))
            {
                cmd.CommandType = commandType;
                if (parameters != null && parameters.Length > 0)
                {
                    cmd.Parameters.AddRange(parameters);
                }
                return cmd.ExecuteScalar();
            }
        }

        #region Stored Procedure Convenience Helpers

        public static DataTable ExecuteStoredProcedureDataTable(string spName, MySqlParameter[] parameters = null)
        {
            return ExecuteDataTable(spName, parameters, CommandType.StoredProcedure);
        }

        public static int ExecuteStoredProcedureNonQuery(string spName, MySqlParameter[] parameters = null)
        {
            return ExecuteNonQuery(spName, parameters, CommandType.StoredProcedure);
        }

        public static object ExecuteStoredProcedureScalar(string spName, MySqlParameter[] parameters = null)
        {
            return ExecuteScalar(spName, parameters, CommandType.StoredProcedure);
        }

        #endregion

        /// <summary>
        /// Verifies database connectivity on application startup.
        /// Table schema, stored procedures, and triggers are deployed via the master SQL file.
        /// </summary>
        public static void InitializeDatabase()
        {
            try
            {
                using (var conn = GetConnection())
                {
                    // Simple connectivity test
                    using (var cmd = new MySqlCommand("SELECT 1;", conn))
                    {
                        cmd.ExecuteScalar();
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[DbHelper.InitializeDatabase] Warning: {ex.Message}");
            }
        }
    }
}

```

### 5.1.2 `AccountDAL.cs`
```csharp
using System.Data;
using MySqlConnector;

namespace ShopManagement.DataAccess
{
    public class AccountDAL
    {
        public DataTable ValidateUser(string username, string password)
        {
            var parameters = new[]
            {
                new MySqlParameter("@p_Username", username),
                new MySqlParameter("@p_Password", password)
            };

            return DbHelper.ExecuteDataTable("sp_ValidateUser", parameters, CommandType.StoredProcedure);
        }
    }
}

```

### 5.1.3 `EmployeeDAL.cs`
```csharp
using System;
using System.Data;
using MySqlConnector;

namespace ShopManagement.DataAccess
{
    public class EmployeeDAL
    {
        public DataTable GetAllEmployees()
        {
            return DbHelper.ExecuteDataTable("sp_GetAllEmployees", null, CommandType.StoredProcedure);
        }

        public DataTable GetEmployeeById(int userId)
        {
            var parameters = new[] { new MySqlParameter("@p_UserId", userId) };
            return DbHelper.ExecuteDataTable("sp_GetEmployeeById", parameters, CommandType.StoredProcedure);
        }

        public bool CreateEmployee(string name, string username, string password, int? storeId)
        {
            var parameters = new[]
            {
                new MySqlParameter("@p_Name",     name),
                new MySqlParameter("@p_Username", username),
                new MySqlParameter("@p_Password", password),
                new MySqlParameter("@p_StoreId",  storeId.HasValue ? (object)storeId.Value : DBNull.Value)
            };
            return DbHelper.ExecuteNonQuery("sp_CreateEmployee", parameters, CommandType.StoredProcedure) > 0;
        }

        public bool UpdateEmployee(int userId, string name, string password, bool isActive, int? storeId)
        {
            var parameters = new[]
            {
                new MySqlParameter("@p_UserId",   userId),
                new MySqlParameter("@p_Name",     name),
                new MySqlParameter("@p_Password", string.IsNullOrWhiteSpace(password) ? (object)DBNull.Value : password),
                new MySqlParameter("@p_IsActive", isActive ? 1 : 0),
                new MySqlParameter("@p_StoreId",  storeId.HasValue ? (object)storeId.Value : DBNull.Value)
            };
            return DbHelper.ExecuteNonQuery("sp_UpdateEmployee", parameters, CommandType.StoredProcedure) > 0;
        }

        public bool ResetPassword(int userId, string newPassword)
        {
            var parameters = new[]
            {
                new MySqlParameter("@p_UserId",   userId),
                new MySqlParameter("@p_Password", newPassword)
            };
            return DbHelper.ExecuteNonQuery("sp_ResetEmployeePassword", parameters, CommandType.StoredProcedure) > 0;
        }

        public bool ToggleStatus(int userId)
        {
            var parameters = new[] { new MySqlParameter("@p_UserId", userId) };
            return DbHelper.ExecuteNonQuery("sp_ToggleEmployeeStatus", parameters, CommandType.StoredProcedure) > 0;
        }

        public bool DeleteEmployee(int userId)
        {
            var parameters = new[] { new MySqlParameter("@p_UserId", userId) };
            return DbHelper.ExecuteNonQuery("sp_DeleteEmployee", parameters, CommandType.StoredProcedure) > 0;
        }
    }
}

```

### 5.1.4 `StoreDAL.cs`
```csharp
using System;
using System.Data;
using MySqlConnector;

namespace ShopManagement.DataAccess
{
    public class StoreDAL
    {
        public DataTable GetAllStores(bool activeOnly = false)
        {
            var parameters = new[] { new MySqlParameter("@p_ActiveOnly", activeOnly) };
            return DbHelper.ExecuteDataTable("sp_GetAllStores", parameters, CommandType.StoredProcedure);
        }

        public DataTable GetStoreById(int storeId)
        {
            var parameters = new[] { new MySqlParameter("@p_StoreId", storeId) };
            return DbHelper.ExecuteDataTable("sp_GetStoreById", parameters, CommandType.StoredProcedure);
        }

        public bool CreateStore(string storeCode, string storeName, string address, string phone, string email, out string errorMessage)
        {
            errorMessage = string.Empty;
            try
            {
                var parameters = new[]
                {
                    new MySqlParameter("@p_StoreCode", storeCode),
                    new MySqlParameter("@p_StoreName", storeName),
                    new MySqlParameter("@p_Address",   string.IsNullOrWhiteSpace(address) ? (object)DBNull.Value : address),
                    new MySqlParameter("@p_Phone",     string.IsNullOrWhiteSpace(phone) ? (object)DBNull.Value : phone),
                    new MySqlParameter("@p_Email",     string.IsNullOrWhiteSpace(email) ? (object)DBNull.Value : email)
                };
                return DbHelper.ExecuteNonQuery("sp_CreateStore", parameters, CommandType.StoredProcedure) > 0;
            }
            catch (Exception ex)
            {
                errorMessage = ex.Message.Contains("Duplicate") ? "Store code already exists." : ex.Message;
                return false;
            }
        }

        public bool UpdateStore(int storeId, string storeName, string address, string phone, string email, bool isActive)
        {
            var parameters = new[]
            {
                new MySqlParameter("@p_StoreId",   storeId),
                new MySqlParameter("@p_StoreName", storeName),
                new MySqlParameter("@p_Address",   string.IsNullOrWhiteSpace(address) ? (object)DBNull.Value : address),
                new MySqlParameter("@p_Phone",     string.IsNullOrWhiteSpace(phone) ? (object)DBNull.Value : phone),
                new MySqlParameter("@p_Email",     string.IsNullOrWhiteSpace(email) ? (object)DBNull.Value : email),
                new MySqlParameter("@p_IsActive",  isActive ? 1 : 0)
            };
            return DbHelper.ExecuteNonQuery("sp_UpdateStore", parameters, CommandType.StoredProcedure) > 0;
        }

        public bool DeleteStore(int storeId)
        {
            var parameters = new[] { new MySqlParameter("@p_StoreId", storeId) };
            return DbHelper.ExecuteNonQuery("sp_DeleteStore", parameters, CommandType.StoredProcedure) > 0;
        }

        public DataTable GetStoreStats()
        {
            return DbHelper.ExecuteDataTable("sp_GetStoreStats", null, CommandType.StoredProcedure);
        }
    }
}

```

### 5.1.5 `ProductDAL.cs`
```csharp
using System;
using System.Data;
using MySqlConnector;

namespace ShopManagement.DataAccess
{
    public class ProductDAL
    {
        public DataTable GetAllProducts(bool activeOnly = true)
        {
            var parameters = new[] { new MySqlParameter("@p_ActiveOnly", activeOnly) };
            return DbHelper.ExecuteDataTable("sp_GetAllProducts", parameters, CommandType.StoredProcedure);
        }

        public DataTable GetProductById(int productId)
        {
            var parameters = new[] { new MySqlParameter("@p_ProductId", productId) };
            return DbHelper.ExecuteDataTable("sp_GetProductById", parameters, CommandType.StoredProcedure);
        }

        public DataTable CheckProductExists(string productCode, string productName)
        {
            var parameters = new[]
            {
                new MySqlParameter("@p_ProductCode", productCode ?? string.Empty),
                new MySqlParameter("@p_ProductName", productName ?? string.Empty)
            };
            return DbHelper.ExecuteDataTable("sp_CheckProductExists", parameters, CommandType.StoredProcedure);
        }

        public bool UpsertProduct(string productCode, string productName, int quantity, decimal price, string imagePath, out string operation)
        {
            var dtExisting = CheckProductExists(productCode, productName);

            if (dtExisting != null && dtExisting.Rows.Count > 0)
            {
                int existingId = Convert.ToInt32(dtExisting.Rows[0]["ProductId"]);
                string existingImage = Convert.ToString(dtExisting.Rows[0]["ImagePath"]);
                int currentQty = Convert.ToInt32(dtExisting.Rows[0]["Quantity"]);

                string resolvedImage = string.IsNullOrWhiteSpace(imagePath) ? existingImage : imagePath;

                var updateParams = new[]
                {
                    new MySqlParameter("@p_ProductId",   existingId),
                    new MySqlParameter("@p_ProductName", productName),
                    new MySqlParameter("@p_Quantity",    currentQty + quantity),
                    new MySqlParameter("@p_Price",       price),
                    new MySqlParameter("@p_ImagePath",   resolvedImage ?? "/images/products/default-product.svg")
                };

                int rows = DbHelper.ExecuteNonQuery("sp_UpdateProduct", updateParams, CommandType.StoredProcedure);
                operation = "Updated (Stock Incremented)";
                return rows > 0;
            }
            else
            {
                string defaultImage = string.IsNullOrWhiteSpace(imagePath)
                    ? "/images/products/default-product.svg"
                    : imagePath;

                var insertParams = new[]
                {
                    new MySqlParameter("@p_ProductCode", productCode),
                    new MySqlParameter("@p_ProductName", productName),
                    new MySqlParameter("@p_Quantity",    quantity),
                    new MySqlParameter("@p_Price",       price),
                    new MySqlParameter("@p_ImagePath",   defaultImage)
                };

                int rows = DbHelper.ExecuteNonQuery("sp_CreateProduct", insertParams, CommandType.StoredProcedure);
                operation = "Created New Product";
                return rows > 0;
            }
        }

        public bool UpdateProduct(int productId, string productName, int quantity, decimal price, string newImagePath, out string errorMessage)
        {
            errorMessage = string.Empty;
            try
            {
                var parameters = new[]
                {
                    new MySqlParameter("@p_ProductId",   productId),
                    new MySqlParameter("@p_ProductName", productName),
                    new MySqlParameter("@p_Quantity",    quantity),
                    new MySqlParameter("@p_Price",       price),
                    new MySqlParameter("@p_ImagePath",   string.IsNullOrWhiteSpace(newImagePath) ? (object)DBNull.Value : newImagePath)
                };

                return DbHelper.ExecuteNonQuery("sp_UpdateProduct", parameters, CommandType.StoredProcedure) > 0;
            }
            catch (Exception ex)
            {
                errorMessage = ex.Message;
                return false;
            }
        }

        public bool DeleteProduct(int productId)
        {
            var parameters = new[] { new MySqlParameter("@p_ProductId", productId) };
            return DbHelper.ExecuteNonQuery("sp_DeleteProduct", parameters, CommandType.StoredProcedure) > 0;
        }

        public DataTable SearchAvailableProducts(string term)
        {
            var parameters = new[] { new MySqlParameter("@p_Term", term ?? string.Empty) };
            return DbHelper.ExecuteDataTable("sp_SearchAvailableProducts", parameters, CommandType.StoredProcedure);
        }
    }
}

```

### 5.1.6 `InvoiceDAL.cs`
```csharp
using System;
using System.Data;
using MySqlConnector;

namespace ShopManagement.DataAccess
{
    public class InvoiceDAL
    {
        public bool CreateInvoice(string customerName, string customerPhone, int createdBy, DataTable items, out string invoiceNo, out string errorMessage)
        {
            invoiceNo    = "INV-" + DateTime.Now.ToString("yyyyMMddHHmmss");
            errorMessage = string.Empty;

            using (var conn = DbHelper.GetConnection())
            using (var trans = conn.BeginTransaction())
            {
                try
                {
                    decimal grandTotal = 0;

                    // ── Step 1: Validate stock availability for every item (FOR UPDATE lock) ──
                    foreach (DataRow row in items.Rows)
                    {
                        int     productId = Convert.ToInt32(row["ProductId"]);
                        int     qty       = Convert.ToInt32(row["Quantity"]);
                        decimal unitPrice = Convert.ToDecimal(row["UnitPrice"]);
                        grandTotal += qty * unitPrice;

                        using (var cmd = new MySqlCommand("sp_CheckProductStock", conn, trans))
                        {
                            cmd.CommandType = CommandType.StoredProcedure;
                            cmd.Parameters.AddWithValue("p_ProductId", productId);

                            using (var reader = cmd.ExecuteReader())
                            {
                                if (!reader.Read())
                                {
                                    reader.Close();
                                    errorMessage = $"Product ID {productId} does not exist or is inactive.";
                                    trans.Rollback();
                                    return false;
                                }

                                string prodName    = reader["ProductName"].ToString();
                                int    stockOnHand = Convert.ToInt32(reader["Quantity"]);
                                reader.Close();

                                if (stockOnHand < qty)
                                {
                                    errorMessage = $"Insufficient stock for '{prodName}'. Available: {stockOnHand}, Requested: {qty}.";
                                    trans.Rollback();
                                    return false;
                                }
                            }
                        }
                    }

                    // ── Step 2: Insert Invoice Header → get new InvoiceId ──
                    int invoiceId;
                    using (var cmd = new MySqlCommand("sp_InsertInvoiceHeader", conn, trans))
                    {
                        cmd.CommandType = CommandType.StoredProcedure;
                        cmd.Parameters.AddWithValue("p_InvoiceNo",     invoiceNo);
                        cmd.Parameters.AddWithValue("p_CustomerName",  customerName);
                        cmd.Parameters.AddWithValue("p_CustomerPhone", string.IsNullOrWhiteSpace(customerPhone) ? (object)DBNull.Value : customerPhone);
                        cmd.Parameters.AddWithValue("p_CreatedBy",     createdBy);
                        cmd.Parameters.AddWithValue("p_TotalAmount",   grandTotal);

                        using (var reader = cmd.ExecuteReader())
                        {
                            reader.Read();
                            invoiceId = Convert.ToInt32(reader["NewInvoiceId"]);
                        }
                    }

                    // ── Step 3: Insert each detail row and deduct stock ──
                    foreach (DataRow row in items.Rows)
                    {
                        int     productId = Convert.ToInt32(row["ProductId"]);
                        string  prodName  = Convert.ToString(row["ProductName"]) ?? "";
                        int     qty       = Convert.ToInt32(row["Quantity"]);
                        decimal unitPrice = Convert.ToDecimal(row["UnitPrice"]);
                        decimal lineTotal = qty * unitPrice;

                        // 3a. Insert detail line
                        using (var cmd = new MySqlCommand("sp_InsertInvoiceDetail", conn, trans))
                        {
                            cmd.CommandType = CommandType.StoredProcedure;
                            cmd.Parameters.AddWithValue("p_InvoiceId",   invoiceId);
                            cmd.Parameters.AddWithValue("p_ProductId",   productId);
                            cmd.Parameters.AddWithValue("p_ProductName", prodName);
                            cmd.Parameters.AddWithValue("p_Quantity",    qty);
                            cmd.Parameters.AddWithValue("p_UnitPrice",   unitPrice);
                            cmd.Parameters.AddWithValue("p_TotalAmount", lineTotal);
                            cmd.ExecuteNonQuery();
                        }

                        // 3b. Deduct stock
                        using (var cmd = new MySqlCommand("sp_DeductProductStock", conn, trans))
                        {
                            cmd.CommandType = CommandType.StoredProcedure;
                            cmd.Parameters.AddWithValue("p_ProductId", productId);
                            cmd.Parameters.AddWithValue("p_Quantity",  qty);
                            cmd.ExecuteNonQuery();
                        }
                    }

                    trans.Commit();
                    return true;
                }
                catch (Exception ex)
                {
                    trans.Rollback();
                    errorMessage = ex.Message;
                    return false;
                }
            }
        }


        public DataTable GetInvoiceHistory(int? createdBy = null)
        {
            var parameters = new[]
            {
                new MySqlParameter("@p_CreatedBy", createdBy.HasValue ? (object)createdBy.Value : DBNull.Value)
            };
            return DbHelper.ExecuteDataTable("sp_GetInvoiceHistory", parameters, CommandType.StoredProcedure);
        }

        public DataTable GetInvoiceHeader(int invoiceId)
        {
            var parameters = new[] { new MySqlParameter("@p_InvoiceId", invoiceId) };
            return DbHelper.ExecuteDataTable("sp_GetInvoiceHeader", parameters, CommandType.StoredProcedure);
        }

        public DataTable GetInvoiceDetails(int invoiceId)
        {
            var parameters = new[] { new MySqlParameter("@p_InvoiceId", invoiceId) };
            return DbHelper.ExecuteDataTable("sp_GetInvoiceDetails", parameters, CommandType.StoredProcedure);
        }

        public DataTable GetDashboardMetrics()
        {
            return DbHelper.ExecuteDataTable("sp_GetDashboardMetrics", null, CommandType.StoredProcedure);
        }
    }
}

```

---

## 5.2 Business Access Layer (ShopManagement.Business)

### 5.2.1 `AccountBAL.cs`
```csharp
using System;
using System.Data;
using ShopManagement.DataAccess;

namespace ShopManagement.Business
{
    public class AccountBAL
    {
        private readonly AccountDAL _dal = new AccountDAL();

        public DataTable Login(string username, string password)
        {
            if (string.IsNullOrWhiteSpace(username) || string.IsNullOrWhiteSpace(password))
            {
                return new DataTable();
            }

            return _dal.ValidateUser(username.Trim(), password.Trim());
        }
    }
}

```

### 5.2.2 `EmployeeBAL.cs`
```csharp
using System;
using System.Data;
using ShopManagement.DataAccess;

namespace ShopManagement.Business
{
    public class EmployeeBAL
    {
        private readonly EmployeeDAL _dal = new EmployeeDAL();

        public DataTable GetAllEmployees()
        {
            return _dal.GetAllEmployees();
        }

        public DataTable GetEmployeeById(int userId)
        {
            return _dal.GetEmployeeById(userId);
        }

        public bool CreateEmployee(string name, string username, string password, int? storeId, out string errorMessage)
        {
            errorMessage = string.Empty;
            if (string.IsNullOrWhiteSpace(name) || string.IsNullOrWhiteSpace(username) || string.IsNullOrWhiteSpace(password))
            {
                errorMessage = "All fields (Name, Username, Password) are required.";
                return false;
            }

            try
            {
                return _dal.CreateEmployee(name.Trim(), username.Trim(), password.Trim(), storeId);
            }
            catch (Exception ex)
            {
                errorMessage = ex.Message.Contains("Duplicate") || ex.Message.Contains("UNIQUE")
                    ? "Username already exists. Please choose a different username."
                    : ex.Message;
                return false;
            }
        }

        public bool UpdateEmployee(int userId, string name, string password, bool isActive, int? storeId, out string errorMessage)
        {
            errorMessage = string.Empty;
            if (string.IsNullOrWhiteSpace(name))
            {
                errorMessage = "Name is required.";
                return false;
            }

            try
            {
                return _dal.UpdateEmployee(userId, name.Trim(), password?.Trim(), isActive, storeId);
            }
            catch (Exception ex)
            {
                errorMessage = ex.Message;
                return false;
            }
        }

        public bool ResetPassword(int userId, string newPassword, out string errorMessage)
        {
            errorMessage = string.Empty;
            if (string.IsNullOrWhiteSpace(newPassword))
            {
                errorMessage = "New password cannot be empty.";
                return false;
            }

            try
            {
                return _dal.ResetPassword(userId, newPassword.Trim());
            }
            catch (Exception ex)
            {
                errorMessage = ex.Message;
                return false;
            }
        }

        public bool ToggleStatus(int userId)
        {
            return _dal.ToggleStatus(userId);
        }

        public bool DeleteEmployee(int userId)
        {
            return _dal.DeleteEmployee(userId);
        }
    }
}

```

### 5.2.3 `StoreBAL.cs`
```csharp
using System;
using System.Data;
using ShopManagement.DataAccess;

namespace ShopManagement.Business
{
    public class StoreBAL
    {
        private readonly StoreDAL _dal = new StoreDAL();

        public DataTable GetAllStores(bool activeOnly = false)
        {
            return _dal.GetAllStores(activeOnly);
        }

        public DataTable GetStoreById(int storeId)
        {
            return _dal.GetStoreById(storeId);
        }

        public DataTable GetStoreStats()
        {
            return _dal.GetStoreStats();
        }

        public bool CreateStore(string storeCode, string storeName, string address, string phone, string email, out string errorMessage)
        {
            errorMessage = string.Empty;

            if (string.IsNullOrWhiteSpace(storeCode) || string.IsNullOrWhiteSpace(storeName))
            {
                errorMessage = "Store Code and Store Name are required.";
                return false;
            }

            return _dal.CreateStore(storeCode.Trim().ToUpper(), storeName.Trim(), address, phone, email, out errorMessage);
        }

        public bool UpdateStore(int storeId, string storeName, string address, string phone, string email, bool isActive, out string errorMessage)
        {
            errorMessage = string.Empty;

            if (string.IsNullOrWhiteSpace(storeName))
            {
                errorMessage = "Store Name is required.";
                return false;
            }

            return _dal.UpdateStore(storeId, storeName.Trim(), address, phone, email, isActive);
        }

        public bool DeleteStore(int storeId)
        {
            return _dal.DeleteStore(storeId);
        }
    }
}

```

### 5.2.4 `ProductBAL.cs`
```csharp
using System;
using System.Data;
using ShopManagement.DataAccess;

namespace ShopManagement.Business
{
    public class ProductBAL
    {
        private readonly ProductDAL _dal = new ProductDAL();

        public DataTable GetAllProducts(bool activeOnly = true)
        {
            return _dal.GetAllProducts(activeOnly);
        }

        public DataTable GetProductById(int productId)
        {
            return _dal.GetProductById(productId);
        }

        /// <summary>
        /// Upsert: If product already exists (by code OR name), increment its stock.
        /// If not found, create a new product. Missing image defaults to default-product.svg.
        /// </summary>
        public bool UpsertProduct(string productCode, string productName, int quantity, decimal price, string imagePath, out string operation)
        {
            if (string.IsNullOrWhiteSpace(productCode) || string.IsNullOrWhiteSpace(productName))
            {
                operation = "Product code and name are required.";
                return false;
            }

            if (quantity < 0) quantity = 0;
            if (price < 0) price = 0;

            return _dal.UpsertProduct(productCode.Trim(), productName.Trim(), quantity, price, imagePath, out operation);
        }

        /// <summary>
        /// Edit existing product: sets exact quantity, price, name, and optionally updates image.
        /// </summary>
        public bool UpdateProduct(int productId, string productName, int quantity, decimal price, string newImagePath, out string errorMessage)
        {
            errorMessage = string.Empty;

            if (string.IsNullOrWhiteSpace(productName))
            {
                errorMessage = "Product Name is required.";
                return false;
            }

            if (quantity < 0) quantity = 0;
            if (price < 0) price = 0;

            return _dal.UpdateProduct(productId, productName.Trim(), quantity, price, newImagePath, out errorMessage);
        }

        public bool DeleteProduct(int productId)
        {
            return _dal.DeleteProduct(productId);
        }

        public DataTable SearchAvailableProducts(string term)
        {
            return _dal.SearchAvailableProducts(term);
        }
    }
}

```

### 5.2.5 `InvoiceBAL.cs`
```csharp
using System;
using System.Data;
using ShopManagement.DataAccess;

namespace ShopManagement.Business
{
    public class InvoiceBAL
    {
        private readonly InvoiceDAL _dal = new InvoiceDAL();

        public bool CreateInvoice(string customerName, string customerPhone, int createdBy, DataTable items, out string invoiceNo, out string errorMessage)
        {
            invoiceNo = string.Empty;
            errorMessage = string.Empty;

            if (string.IsNullOrWhiteSpace(customerName))
            {
                errorMessage = "Customer Name is required.";
                return false;
            }

            if (items == null || items.Rows.Count == 0)
            {
                errorMessage = "Invoice must contain at least one product item.";
                return false;
            }

            return _dal.CreateInvoice(customerName.Trim(), customerPhone?.Trim(), createdBy, items, out invoiceNo, out errorMessage);
        }

        public DataTable GetInvoiceHistory(int? createdBy = null)
        {
            return _dal.GetInvoiceHistory(createdBy);
        }

        public DataTable GetInvoiceHeader(int invoiceId)
        {
            return _dal.GetInvoiceHeader(invoiceId);
        }

        public DataTable GetInvoiceDetails(int invoiceId)
        {
            return _dal.GetInvoiceDetails(invoiceId);
        }

        public DataTable GetDashboardMetrics()
        {
            return _dal.GetDashboardMetrics();
        }
    }
}

```

### 5.2.6 `ExcelBAL.cs`
```csharp
using System;
using System.Data;
using System.IO;
using ClosedXML.Excel;

namespace ShopManagement.Business
{
    public class ExcelBAL
    {
        private readonly ProductBAL _productBAL = new ProductBAL();

        public DataTable ProcessExcelProductImport(Stream fileStream, out int totalCount, out int insertedCount, out int updatedCount, out int failedCount)
        {
            totalCount = 0;
            insertedCount = 0;
            updatedCount = 0;
            failedCount = 0;

            var resultDt = new DataTable("ImportResults");
            resultDt.Columns.Add("RowNumber", typeof(int));
            resultDt.Columns.Add("ProductCode", typeof(string));
            resultDt.Columns.Add("ProductName", typeof(string));
            resultDt.Columns.Add("Quantity", typeof(int));
            resultDt.Columns.Add("Price", typeof(decimal));
            resultDt.Columns.Add("Status", typeof(string));
            resultDt.Columns.Add("Message", typeof(string));

            using (var workbook = new XLWorkbook(fileStream))
            {
                var worksheet = workbook.Worksheet(1);
                var rows = worksheet.RangeUsed().RowsUsed();

                bool isFirstRow = true;
                int rowNum = 1;

                foreach (var row in rows)
                {
                    if (isFirstRow)
                    {
                        // Header row: ProductCode | ProductName | Quantity | Price | ImagePath
                        isFirstRow = false;
                        rowNum++;
                        continue;
                    }

                    totalCount++;
                    string productCode = row.Cell(1).GetString()?.Trim();
                    string productName = row.Cell(2).GetString()?.Trim();
                    string qtyStr = row.Cell(3).GetString()?.Trim();
                    string priceStr = row.Cell(4).GetString()?.Trim();
                    string imagePath = row.Cell(5).GetString()?.Trim();

                    if (string.IsNullOrWhiteSpace(productCode) && string.IsNullOrWhiteSpace(productName))
                    {
                        // empty row
                        continue;
                    }

                    int qty = 0;
                    decimal price = 0;
                    bool isQtyValid = int.TryParse(qtyStr, out qty);
                    bool isPriceValid = decimal.TryParse(priceStr, out price);

                    if (string.IsNullOrWhiteSpace(productCode) || string.IsNullOrWhiteSpace(productName) || !isQtyValid || !isPriceValid)
                    {
                        failedCount++;
                        resultDt.Rows.Add(rowNum, productCode, productName, qty, price, "Failed", "Invalid data format or missing required fields.");
                        rowNum++;
                        continue;
                    }

                    string operation;
                    bool success = _productBAL.UpsertProduct(productCode, productName, qty, price, imagePath, out operation);

                    if (success)
                    {
                        if (operation.Contains("Updated"))
                            updatedCount++;
                        else
                            insertedCount++;

                        resultDt.Rows.Add(rowNum, productCode, productName, qty, price, "Success", operation);
                    }
                    else
                    {
                        failedCount++;
                        resultDt.Rows.Add(rowNum, productCode, productName, qty, price, "Failed", operation);
                    }

                    rowNum++;
                }
            }

            return resultDt;
        }

        public byte[] GenerateSampleExcelTemplate()
        {
            using (var workbook = new XLWorkbook())
            {
                var ws = workbook.Worksheets.Add("Products");

                // Headers
                ws.Cell(1, 1).Value = "ProductCode";
                ws.Cell(1, 2).Value = "ProductName";
                ws.Cell(1, 3).Value = "Quantity";
                ws.Cell(1, 4).Value = "Price";
                ws.Cell(1, 5).Value = "ImagePath";

                // Header styling
                var headerRange = ws.Range("A1:E1");
                headerRange.Style.Font.Bold = true;
                headerRange.Style.Fill.BackgroundColor = XLColor.FromHtml("#2563EB");
                headerRange.Style.Font.FontColor = XLColor.White;

                // Sample data rows
                ws.Cell(2, 1).Value = "P101";
                ws.Cell(2, 2).Value = "Wireless Optical Mouse";
                ws.Cell(2, 3).Value = 25;
                ws.Cell(2, 4).Value = 499.00;
                ws.Cell(2, 5).Value = "/images/products/mouse.png";

                ws.Cell(3, 1).Value = "P102";
                ws.Cell(3, 2).Value = "Mechanical Gaming Keyboard";
                ws.Cell(3, 3).Value = 15;
                ws.Cell(3, 4).Value = 1899.00;
                ws.Cell(3, 5).Value = "/images/products/keyboard.png";

                ws.Cell(4, 1).Value = "P001"; // Test existing upsert
                ws.Cell(4, 2).Value = "Parker Roller Ball Pen";
                ws.Cell(4, 3).Value = 50; // Will be added to existing stock
                ws.Cell(4, 4).Value = 150.00;
                ws.Cell(4, 5).Value = "/images/products/pen.png";

                ws.Columns().AdjustToContents();

                using (var ms = new MemoryStream())
                {
                    workbook.SaveAs(ms);
                    return ms.ToArray();
                }
            }
        }
    }
}

```

---

## 5.3 Web Presentation Layer (ShopManagement.Web)

### 5.3.1 `Program.cs`
```csharp
using System;
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using ShopManagement.DataAccess;

var builder = WebApplication.CreateBuilder(args);

// Configure Database Connection String
string connectionString = builder.Configuration.GetConnectionString("DefaultConnection") 
    ?? "Server=localhost;Database=ShopManagementDB;User ID=root;Password=root;Port=3306;AllowUserVariables=True;";
DbHelper.ConnectionString = connectionString;

// Add services to the container.
builder.Services.AddControllersWithViews();

builder.Services.AddHttpContextAccessor();
builder.Services.AddDistributedMemoryCache();
builder.Services.AddSession(options =>
{
    options.IdleTimeout = TimeSpan.FromHours(4);
    options.Cookie.HttpOnly = true;
    options.Cookie.IsEssential = true;
});

var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Account/Login");
}

// DbHelper initialization to ensure tables and columns exist
try
{
    DbHelper.InitializeDatabase();
}
catch (Exception ex)
{
    Console.WriteLine($"DB Initialization note: {ex.Message}");
}

app.UseStaticFiles();

app.UseRouting();

app.UseSession();
app.UseAuthorization();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");

app.Run();

```

### 5.3.2 `appsettings.json`
```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost;Database=ShopManagementDB;User ID=root;Password=root;Port=3306;AllowUserVariables=True;"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  },
  "AllowedHosts": "*"
}

```

### 5.3.3 Controllers

#### `AccountController.cs`
```csharp
using System;
using System.Data;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using ShopManagement.Business;

namespace ShopManagement.Web.Controllers
{
    public class AccountController : Controller
    {
        private readonly AccountBAL _accountBAL = new AccountBAL();

        [HttpGet]
        public IActionResult Index()
        {
            return RedirectToAction("Login");
        }

        [HttpGet]
        public IActionResult Login()
        {
            string? role = HttpContext.Session.GetString("Role");
            if (!string.IsNullOrEmpty(role))
            {
                return role.Equals("Admin", StringComparison.OrdinalIgnoreCase) 
                    ? RedirectToAction("Index", "Product") 
                    : RedirectToAction("Create", "Invoice");
            }
            return View();
        }

        [HttpPost]
        public IActionResult Login(string username, string password)
        {
            if (string.IsNullOrWhiteSpace(username) || string.IsNullOrWhiteSpace(password))
            {
                ViewBag.Error = "Please enter both username and password.";
                return View();
            }

            DataTable dt = _accountBAL.Login(username, password);

            if (dt != null && dt.Rows.Count > 0)
            {
                DataRow row = dt.Rows[0];
                int userId = Convert.ToInt32(row["UserId"]);
                string fullName = Convert.ToString(row["Name"]) ?? "";
                string user = Convert.ToString(row["Username"]) ?? "";
                string role = Convert.ToString(row["Role"]) ?? "";

                HttpContext.Session.SetInt32("UserId", userId);
                HttpContext.Session.SetString("Username", user);
                HttpContext.Session.SetString("FullName", fullName);
                HttpContext.Session.SetString("Role", role);

                if (role.Equals("Admin", StringComparison.OrdinalIgnoreCase))
                {
                    return RedirectToAction("Index", "Product");
                }
                else
                {
                    return RedirectToAction("Create", "Invoice");
                }
            }

            ViewBag.Error = "Invalid credentials or account is inactive.";
            return View();
        }

        [HttpGet]
        public IActionResult Logout()
        {
            HttpContext.Session.Clear();
            return RedirectToAction("Login");
        }
    }
}

```

#### `DashboardController.cs`
```csharp
using System;
using System.Data;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using ShopManagement.Business;

namespace ShopManagement.Web.Controllers
{
    public class DashboardController : Controller
    {
        private readonly InvoiceBAL _invoiceBAL = new InvoiceBAL();

        [HttpGet]
        public IActionResult Index()
        {
            string? role = HttpContext.Session.GetString("Role");
            if (string.IsNullOrEmpty(role))
            {
                return RedirectToAction("Login", "Account");
            }

            if (!role.Equals("Admin", StringComparison.OrdinalIgnoreCase))
            {
                return RedirectToAction("Create", "Invoice");
            }

            DataTable dtMetrics = _invoiceBAL.GetDashboardMetrics();
            return View(dtMetrics);
        }
    }
}

```

#### `EmployeeController.cs`
```csharp
using System;
using System.Data;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json;
using ShopManagement.Business;

namespace ShopManagement.Web.Controllers
{
    public class EmployeeController : Controller
    {
        private readonly EmployeeBAL _employeeBAL = new EmployeeBAL();
        private readonly StoreBAL _storeBAL = new StoreBAL();

        private bool IsAdmin()
        {
            string? role = HttpContext.Session.GetString("Role");
            return !string.IsNullOrEmpty(role) && role.Equals("Admin", StringComparison.OrdinalIgnoreCase);
        }

        [HttpGet]
        public IActionResult Index()
        {
            if (!IsAdmin()) return RedirectToAction("Login", "Account");
            return View();
        }

        [HttpGet]
        public IActionResult GetEmployeesJson()
        {
            if (!IsAdmin()) return Unauthorized();
            try
            {
                DataTable dt = _employeeBAL.GetAllEmployees();
                var list = new System.Collections.Generic.List<System.Collections.Generic.Dictionary<string, object?>>();
                foreach (DataRow r in dt.Rows)
                {
                    var d = new System.Collections.Generic.Dictionary<string, object?>();
                    foreach (DataColumn c in dt.Columns)
                    {
                        d[c.ColumnName] = r[c] == DBNull.Value ? null : r[c];
                    }
                    list.Add(d);
                }
                return Content(JsonConvert.SerializeObject(list), "application/json");
            }
            catch (Exception ex)
            {
                return Json(new { error = ex.Message });
            }
        }

        [HttpPost]
        public IActionResult Add(string name, string username, string password, int? storeId)
        {
            if (!IsAdmin()) return Json(new { success = false, message = "Unauthorized" });

            if (string.IsNullOrWhiteSpace(name) || string.IsNullOrWhiteSpace(username) || string.IsNullOrWhiteSpace(password))
            {
                return Json(new { success = false, message = "Please enter Name, Username, and Password." });
            }

            string errorMessage;
            bool success = _employeeBAL.CreateEmployee(name.Trim(), username.Trim(), password.Trim(), storeId, out errorMessage);

            return Json(new { success, message = success ? $"Desk login for '{username.Trim()}' created successfully!" : errorMessage });
        }

        [HttpPost]
        public IActionResult Update(int userId, string name, string? password, bool isActive, int? storeId)
        {
            if (!IsAdmin()) return Json(new { success = false, message = "Unauthorized" });

            string errorMessage;
            bool success = _employeeBAL.UpdateEmployee(userId, name, password, isActive, storeId, out errorMessage);
            return Json(new { success, message = success ? "Desk login updated successfully!" : errorMessage });
        }

        [HttpPost]
        public IActionResult ResetPassword(int userId, string newPassword)
        {
            if (!IsAdmin()) return Json(new { success = false, message = "Unauthorized" });

            string errorMessage;
            bool success = _employeeBAL.ResetPassword(userId, newPassword, out errorMessage);
            return Json(new { success, message = success ? "Password changed successfully!" : errorMessage });
        }

        [HttpPost]
        public IActionResult ToggleStatus(int userId)
        {
            if (!IsAdmin()) return Json(new { success = false, message = "Unauthorized" });

            bool success = _employeeBAL.ToggleStatus(userId);
            return Json(new { success, message = success ? "Desk login status toggled successfully." : "Error toggling status." });
        }

        [HttpPost]
        public IActionResult Delete(int userId)
        {
            if (!IsAdmin()) return Json(new { success = false, message = "Unauthorized" });

            bool success = _employeeBAL.DeleteEmployee(userId);
            return Json(new { success, message = success ? "Desk login deactivated successfully." : "Error updating desk login." });
        }
    }
}

```

#### `StoreController.cs`
```csharp
using System;
using System.Data;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json;
using ShopManagement.Business;

namespace ShopManagement.Web.Controllers
{
    public class StoreController : Controller
    {
        private readonly StoreBAL _storeBAL = new StoreBAL();

        private bool IsAdmin()
        {
            string? role = HttpContext.Session.GetString("Role");
            return !string.IsNullOrEmpty(role) && role.Equals("Admin", StringComparison.OrdinalIgnoreCase);
        }

        [HttpGet]
        public IActionResult Index()
        {
            if (!IsAdmin()) return RedirectToAction("Login", "Account");
            return View();
        }

        [HttpGet]
        public IActionResult GetStoresJson()
        {
            if (!IsAdmin()) return Unauthorized();
            DataTable dt = _storeBAL.GetAllStores(false);
            return Content(JsonConvert.SerializeObject(dt), "application/json");
        }

        [HttpGet]
        public IActionResult GetActiveStoresJson()
        {
            if (string.IsNullOrEmpty(HttpContext.Session.GetString("Role"))) return Unauthorized();
            DataTable dt = _storeBAL.GetAllStores(activeOnly: true);
            return Content(JsonConvert.SerializeObject(dt), "application/json");
        }

        [HttpGet]
        public IActionResult GetStoreStatsJson()
        {
            if (!IsAdmin()) return Unauthorized();
            DataTable dt = _storeBAL.GetStoreStats();
            return Content(JsonConvert.SerializeObject(dt), "application/json");
        }

        [HttpPost]
        public IActionResult Create(string storeCode, string storeName, string address, string phone, string email)
        {
            if (!IsAdmin()) return Json(new { success = false, message = "Unauthorized" });

            string errorMessage;
            bool success = _storeBAL.CreateStore(storeCode, storeName, address, phone, email, out errorMessage);

            return Json(new
            {
                success = success,
                message = success ? $"Store '{storeName}' created successfully!" : errorMessage
            });
        }

        [HttpPost]
        public IActionResult Update(int storeId, string storeName, string address, string phone, string email, bool isActive)
        {
            if (!IsAdmin()) return Json(new { success = false, message = "Unauthorized" });

            string errorMessage;
            bool success = _storeBAL.UpdateStore(storeId, storeName, address, phone, email, isActive, out errorMessage);

            return Json(new { success = success, message = success ? "Store updated successfully!" : errorMessage });
        }

        [HttpPost]
        public IActionResult Delete(int storeId)
        {
            if (!IsAdmin()) return Json(new { success = false, message = "Unauthorized" });

            bool success = _storeBAL.DeleteStore(storeId);
            return Json(new { success = success, message = success ? "Store deactivated." : "Error deactivating store." });
        }
    }
}

```

#### `ProductController.cs`
```csharp
using System;
using System.Data;
using System.IO;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json;
using ShopManagement.Business;

namespace ShopManagement.Web.Controllers
{
    public class ProductController : Controller
    {
        private readonly ProductBAL _productBAL = new ProductBAL();
        private readonly ExcelBAL _excelBAL = new ExcelBAL();
        private readonly IWebHostEnvironment _env;

        public ProductController(IWebHostEnvironment env)
        {
            _env = env;
        }

        private bool IsAdmin()
        {
            string? role = HttpContext.Session.GetString("Role");
            return !string.IsNullOrEmpty(role) && role.Equals("Admin", StringComparison.OrdinalIgnoreCase);
        }

        [HttpGet]
        public IActionResult Index()
        {
            if (!IsAdmin()) return RedirectToAction("Login", "Account");
            return View();
        }

        [HttpGet]
        public IActionResult GetProductsJson()
        {
            if (string.IsNullOrEmpty(HttpContext.Session.GetString("Role")))
                return Unauthorized();

            DataTable dt = _productBAL.GetAllProducts(true);
            return Content(JsonConvert.SerializeObject(dt), "application/json");
        }

        [HttpGet]
        public IActionResult GetProductByIdJson(int id)
        {
            if (!IsAdmin()) return Unauthorized();
            DataTable dt = _productBAL.GetProductById(id);
            return Content(JsonConvert.SerializeObject(dt), "application/json");
        }

        [HttpGet]
        public IActionResult SearchAvailable(string term)
        {
            DataTable dt = _productBAL.SearchAvailableProducts(term);
            return Content(JsonConvert.SerializeObject(dt), "application/json");
        }

        // ------------------------------------------------------------------
        // UPSERT: Add new or increment stock on existing product
        // ------------------------------------------------------------------
        [HttpPost]
        public IActionResult Add(string productCode, string productName, int quantity, decimal price, IFormFile? imageFile)
        {
            if (!IsAdmin()) return Json(new { success = false, message = "Unauthorized" });

            if (string.IsNullOrWhiteSpace(productCode) || string.IsNullOrWhiteSpace(productName))
                return Json(new { success = false, message = "Product Code and Product Name are required." });

            string? imagePath = SaveUploadedImage(imageFile);

            string operation;
            bool success = _productBAL.UpsertProduct(productCode, productName, quantity, price, imagePath, out operation);

            return Json(new { success, message = operation });
        }

        // ------------------------------------------------------------------
        // EDIT: Update an existing product (exact quantity, price, name, image)
        // ------------------------------------------------------------------
        [HttpPost]
        public IActionResult Edit(int productId, string productName, int quantity, decimal price, IFormFile? imageFile)
        {
            if (!IsAdmin()) return Json(new { success = false, message = "Unauthorized" });

            if (string.IsNullOrWhiteSpace(productName))
                return Json(new { success = false, message = "Product Name is required." });

            string? newImagePath = SaveUploadedImage(imageFile);

            string errorMessage;
            bool success = _productBAL.UpdateProduct(productId, productName, quantity, price, newImagePath, out errorMessage);

            return Json(new { success, message = success ? "Product updated successfully!" : errorMessage });
        }

        [HttpPost]
        public IActionResult Delete(int productId)
        {
            if (!IsAdmin()) return Json(new { success = false, message = "Unauthorized" });

            bool success = _productBAL.DeleteProduct(productId);
            return Json(new { success, message = success ? "Product deleted successfully." : "Error deleting product." });
        }

        // ------------------------------------------------------------------
        // Excel Import
        // ------------------------------------------------------------------
        [HttpGet]
        public IActionResult Import()
        {
            if (!IsAdmin()) return RedirectToAction("Login", "Account");
            return View();
        }

        [HttpPost]
        public IActionResult Import(IFormFile excelFile)
        {
            if (!IsAdmin()) return RedirectToAction("Login", "Account");

            if (excelFile == null || excelFile.Length == 0)
            {
                ViewBag.Error = "Please select a valid Excel file (.xlsx).";
                return View();
            }

            try
            {
                int total, inserted, updated, failed;
                using (var stream = excelFile.OpenReadStream())
                {
                    DataTable resultDt = _excelBAL.ProcessExcelProductImport(stream, out total, out inserted, out updated, out failed);

                    ViewBag.Total    = total;
                    ViewBag.Inserted = inserted;
                    ViewBag.Updated  = updated;
                    ViewBag.Failed   = failed;
                    ViewBag.Success  = true;

                    return View(resultDt);
                }
            }
            catch (Exception ex)
            {
                ViewBag.Error = "Error parsing Excel: " + ex.Message;
                return View();
            }
        }

        [HttpGet]
        public IActionResult DownloadTemplate()
        {
            byte[] fileBytes = _excelBAL.GenerateSampleExcelTemplate();
            return File(fileBytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "Products_Import_Template.xlsx");
        }

        // ------------------------------------------------------------------
        // Shared helper: save uploaded image file and return web path
        // ------------------------------------------------------------------
        private string? SaveUploadedImage(IFormFile? imageFile)
        {
            if (imageFile == null || imageFile.Length == 0) return null;

            string uploadFolder = Path.Combine(_env.WebRootPath, "uploads", "products");
            if (!Directory.Exists(uploadFolder))
                Directory.CreateDirectory(uploadFolder);

            string uniqueFileName = $"{Guid.NewGuid()}_{Path.GetFileName(imageFile.FileName)}";
            string filePath = Path.Combine(uploadFolder, uniqueFileName);
            using (var stream = new FileStream(filePath, FileMode.Create))
            {
                imageFile.CopyTo(stream);
            }
            return $"/uploads/products/{uniqueFileName}";
        }
    }
}

```

#### `InvoiceController.cs`
```csharp
using System;
using System.Data;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using ShopManagement.Business;

namespace ShopManagement.Web.Controllers
{
    public class InvoiceController : Controller
    {
        private readonly InvoiceBAL _invoiceBAL = new InvoiceBAL();
        private readonly ProductBAL _productBAL = new ProductBAL();

        private bool IsLoggedIn()
        {
            return !string.IsNullOrEmpty(HttpContext.Session.GetString("Role"));
        }

        [HttpGet]
        public IActionResult Create()
        {
            if (!IsLoggedIn()) return RedirectToAction("Login", "Account");
            return View();
        }

        [HttpPost]
        public IActionResult Create(string customerName, string customerPhone, string itemsJson)
        {
            if (!IsLoggedIn()) return Json(new { success = false, message = "Session expired. Please log in again." });

            if (string.IsNullOrWhiteSpace(customerName))
            {
                return Json(new { success = false, message = "Customer name is required." });
            }

            if (string.IsNullOrWhiteSpace(itemsJson))
            {
                return Json(new { success = false, message = "Please select at least one product." });
            }

            try
            {
                var jArray = JArray.Parse(itemsJson);
                if (jArray.Count == 0)
                {
                    return Json(new { success = false, message = "Invoice must contain at least one product." });
                }

                var itemsDt = new DataTable("InvoiceItems");
                itemsDt.Columns.Add("ProductId", typeof(int));
                itemsDt.Columns.Add("ProductName", typeof(string));
                itemsDt.Columns.Add("Quantity", typeof(int));
                itemsDt.Columns.Add("UnitPrice", typeof(decimal));

                foreach (var item in jArray)
                {
                    int productId = item["productId"]?.Value<int>() ?? 0;
                    string productName = item["productName"]?.Value<string>() ?? "";
                    int qty = item["quantity"]?.Value<int>() ?? 0;
                    decimal unitPrice = item["unitPrice"]?.Value<decimal>() ?? 0;

                    if (productId <= 0 || qty <= 0)
                    {
                        return Json(new { success = false, message = "Invalid product or quantity in line items." });
                    }

                    itemsDt.Rows.Add(productId, productName, qty, unitPrice);
                }

                int createdBy = HttpContext.Session.GetInt32("UserId") ?? 1;
                string invoiceNo;
                string errorMessage;

                bool success = _invoiceBAL.CreateInvoice(customerName, customerPhone, createdBy, itemsDt, out invoiceNo, out errorMessage);

                if (success)
                {
                    return Json(new { success = true, invoiceNo = invoiceNo, message = $"Invoice {invoiceNo} generated successfully!" });
                }
                else
                {
                    return Json(new { success = false, message = errorMessage });
                }
            }
            catch (Exception ex)
            {
                return Json(new { success = false, message = "Error creating invoice: " + ex.Message });
            }
        }

        [HttpGet]
        public IActionResult History()
        {
            if (!IsLoggedIn()) return RedirectToAction("Login", "Account");
            return View();
        }

        [HttpGet]
        public IActionResult GetInvoicesJson()
        {
            if (!IsLoggedIn()) return Unauthorized();

            // If Admin, sees all invoices; if Employee, sees all or own
            DataTable dt = _invoiceBAL.GetInvoiceHistory();
            string json = JsonConvert.SerializeObject(dt);
            return Content(json, "application/json");
        }

        [HttpGet]
        public IActionResult Details(int id)
        {
            if (!IsLoggedIn()) return RedirectToAction("Login", "Account");

            DataTable dtHeader = _invoiceBAL.GetInvoiceHeader(id);
            if (dtHeader == null || dtHeader.Rows.Count == 0)
            {
                return NotFound("Invoice not found.");
            }

            DataTable dtDetails = _invoiceBAL.GetInvoiceDetails(id);

            ViewBag.Header = dtHeader.Rows[0];
            return View(dtDetails);
        }

        [HttpGet]
        public IActionResult GetInvoiceDetailsJson(int id)
        {
            if (!IsLoggedIn()) return Unauthorized();

            DataTable dtHeader = _invoiceBAL.GetInvoiceHeader(id);
            if (dtHeader == null || dtHeader.Rows.Count == 0)
            {
                string notFoundJson = JsonConvert.SerializeObject(new { success = false, message = "Invoice not found" });
                return Content(notFoundJson, "application/json");
            }

            DataTable dtDetails = _invoiceBAL.GetInvoiceDetails(id);

            // Serialize header rows and detail rows manually to avoid DataTable column-type serialization issues
            var headerRows = new System.Collections.Generic.List<System.Collections.Generic.Dictionary<string, object?>>();
            foreach (DataRow r in dtHeader.Rows)
            {
                var dict = new System.Collections.Generic.Dictionary<string, object?>();
                foreach (DataColumn col in dtHeader.Columns)
                    dict[col.ColumnName] = r[col] == DBNull.Value ? null : r[col];
                headerRows.Add(dict);
            }

            var detailRows = new System.Collections.Generic.List<System.Collections.Generic.Dictionary<string, object?>>();
            foreach (DataRow r in dtDetails.Rows)
            {
                var dict = new System.Collections.Generic.Dictionary<string, object?>();
                foreach (DataColumn col in dtDetails.Columns)
                    dict[col.ColumnName] = r[col] == DBNull.Value ? null : r[col];
                detailRows.Add(dict);
            }

            string json = JsonConvert.SerializeObject(new { success = true, header = headerRows, details = detailRows });
            return Content(json, "application/json");
        }
    }
}

```

---

### 5.3.4 Standalone Frontend JavaScript (`wwwroot/js/`)

#### `employee.js`
```javascript
// employee.js - Desk Logins (Staff Accounts) page logic

var addModal, editModal;

$(document).ready(function () {
    addModal  = new bootstrap.Modal(document.getElementById('addEmployeeModal'));
    editModal = new bootstrap.Modal(document.getElementById('editEmployeeModal'));
    loadEmployeesGrid();

    $("#addEmployeeForm").on("submit", function (e) {
        e.preventDefault();
        $.post("/Employee/Add", $(this).serialize(), function (res) {
            if (res.success) {
                Swal.fire({ icon: 'success', title: 'Created', text: res.message, timer: 1500, showConfirmButton: false });
                addModal.hide();
                $("#addEmployeeForm")[0].reset();
                $("#employeesGrid").data("kendoGrid").dataSource.read();
            } else {
                Swal.fire({ icon: 'error', title: 'Error', text: res.message });
            }
        });
    });

    $("#editEmployeeForm").on("submit", function (e) {
        e.preventDefault();
        $.post("/Employee/Update", $(this).serialize(), function (res) {
            if (res.success) {
                Swal.fire({ icon: 'success', title: 'Updated', text: res.message, timer: 1500, showConfirmButton: false });
                editModal.hide();
                $("#employeesGrid").data("kendoGrid").dataSource.read();
            } else {
                Swal.fire({ icon: 'error', title: 'Error', text: res.message });
            }
        });
    });
});

function loadEmployeesGrid() {
    $("#employeesGrid").kendoGrid({
        dataSource: {
            transport: { read: { url: "/Employee/GetEmployeesJson", dataType: "json" } },
            schema: {
                model: {
                    id: "UserId",
                    fields: {
                        UserId:     { type: "number" },
                        Name:       { type: "string" },
                        Username:   { type: "string" },
                        Role:       { type: "string" },
                        StoreName:  { type: "string" },
                        IsActive:   { type: "number" },
                        CreatedDate:{ type: "date" }
                    }
                }
            },
            pageSize: 10
        },
        pageable: true,
        sortable: true,
        filterable: true,
        columns: [
            { field: "Name", title: "Full Name" },
            { field: "Username", title: "Username", width: 150 },
            { field: "StoreName", title: "Branch / Store", width: 160 },
            {
                field: "IsActive", title: "Status", width: 120,
                template: d => d.IsActive === 1 ? '<span class="badge bg-success">Active</span>' : '<span class="badge bg-secondary">Disabled</span>'
            },
            {
                title: "Actions", width: 220, filterable: false, sortable: false,
                template: d => `
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="openEditModal(${d.UserId}, '${(d.Name||'').replace(/'/g,"\\'")}', ${d.IsActive})">Edit</button>
                    <button class="btn btn-sm btn-outline-secondary me-1" onclick="toggleStatus(${d.UserId})">Toggle</button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteEmployee(${d.UserId})">Deactivate</button>
                `
            }
        ]
    });
}

function openAddModal() {
    $("#addEmployeeForm")[0].reset();
    addModal.show();
}

function openEditModal(userId, name, isActive) {
    $("#edit_userId").val(userId);
    $("#edit_name").val(name);
    $("#edit_isActive").prop("checked", isActive === 1);
    editModal.show();
}

function toggleStatus(userId) {
    $.post("/Employee/ToggleStatus", { userId: userId }, function (res) {
        $("#employeesGrid").data("kendoGrid").dataSource.read();
    });
}

function deleteEmployee(userId) {
    Swal.fire({
        title: 'Deactivate Login?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, Deactivate'
    }).then((res) => {
        if (res.isConfirmed) {
            $.post("/Employee/Delete", { userId: userId }, function (r) {
                $("#employeesGrid").data("kendoGrid").dataSource.read();
            });
        }
    });
}

```

#### `product.js`
```javascript
// product.js - Product Inventory page logic

var upsertModal, editModal;

$(document).ready(function () {
    upsertModal = new bootstrap.Modal(document.getElementById('upsertProductModal'));
    editModal   = new bootstrap.Modal(document.getElementById('editProductModal'));
    loadProductsGrid();

    $("#upsertProductForm").on("submit", function (e) {
        e.preventDefault();
        var formData = new FormData(this);
        $.ajax({
            url: "/Product/Add",
            type: "POST",
            data: formData,
            contentType: false,
            processData: false,
            success: function (res) {
                if (res.success) {
                    Swal.fire({ icon: 'success', title: 'Saved', text: res.message, timer: 1500, showConfirmButton: false });
                    upsertModal.hide();
                    $("#upsertProductForm")[0].reset();
                    $("#productsGrid").data("kendoGrid").dataSource.read();
                } else {
                    Swal.fire({ icon: 'error', title: 'Error', text: res.message });
                }
            }
        });
    });

    $("#editProductForm").on("submit", function (e) {
        e.preventDefault();
        var formData = new FormData(this);
        $.ajax({
            url: "/Product/Edit",
            type: "POST",
            data: formData,
            contentType: false,
            processData: false,
            success: function (res) {
                if (res.success) {
                    Swal.fire({ icon: 'success', title: 'Updated', text: res.message, timer: 1500, showConfirmButton: false });
                    editModal.hide();
                    $("#productsGrid").data("kendoGrid").dataSource.read();
                } else {
                    Swal.fire({ icon: 'error', title: 'Error', text: res.message });
                }
            }
        });
    });
});

function loadProductsGrid() {
    $("#productsGrid").kendoGrid({
        dataSource: {
            transport: { read: { url: "/Product/GetProductsJson", dataType: "json" } },
            schema: {
                model: {
                    id: "ProductId",
                    fields: {
                        ProductId:   { type: "number" },
                        ProductCode: { type: "string" },
                        ProductName: { type: "string" },
                        Quantity:    { type: "number" },
                        Price:       { type: "number" },
                        ImagePath:   { type: "string" }
                    }
                }
            },
            pageSize: 10
        },
        pageable: true,
        sortable: true,
        filterable: true,
        columns: [
            {
                field: "ImagePath", title: "Image", width: 80, filterable: false, sortable: false,
                template: d => `<img src="${d.ImagePath || '/images/products/default-product.svg'}" style="width:40px;height:40px;object-fit:cover;border:1px solid #ccc;" />`
            },
            { field: "ProductCode", title: "Code", width: 120 },
            { field: "ProductName", title: "Product Name" },
            {
                field: "Quantity", title: "Stock", width: 100,
                template: d => `<strong>${d.Quantity}</strong>`
            },
            {
                field: "Price", title: "Price (Rs.)", width: 120,
                template: d => `Rs.${parseFloat(d.Price).toFixed(2)}`
            },
            {
                title: "Actions", width: 160, filterable: false, sortable: false,
                template: d => `
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="openEditModal(${d.ProductId})">Edit</button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteProduct(${d.ProductId}, '${(d.ProductName||'').replace(/'/g,"\\'")}')">Delete</button>
                `
            }
        ]
    });
}

function openUpsertModal() {
    $("#upsertProductForm")[0].reset();
    $("#upsert_imgPreview").attr("src", "/images/products/default-product.svg");
    upsertModal.show();
}

function openEditModal(productId) {
    $.getJSON("/Product/GetProductByIdJson?id=" + productId, function (data) {
        if (data && data.length > 0) {
            var item = data[0];
            $("#edit_productId").val(item.ProductId);
            $("#edit_productCode").val(item.ProductCode);
            $("#edit_productName").val(item.ProductName);
            $("#edit_quantity").val(item.Quantity);
            $("#edit_price").val(item.Price);
            $("#edit_imgPreview").attr("src", item.ImagePath || "/images/products/default-product.svg");
            editModal.show();
        }
    });
}

function deleteProduct(productId, name) {
    Swal.fire({
        title: 'Delete ' + name + '?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, Delete'
    }).then((res) => {
        if (res.isConfirmed) {
            $.post("/Product/Delete", { productId: productId }, function (r) {
                if (r.success) {
                    $("#productsGrid").data("kendoGrid").dataSource.read();
                } else {
                    Swal.fire('Error', r.message, 'error');
                }
            });
        }
    });
}

function previewImage(input, imgId) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = e => { document.getElementById(imgId).src = e.target.result; };
        reader.readAsDataURL(input.files[0]);
    }
}

```

#### `store.js`
```javascript
// store.js - Stores & Branch Management page logic

var createModal, editModal;

$(document).ready(function () {
    createModal = new bootstrap.Modal(document.getElementById('createStoreModal'));
    editModal   = new bootstrap.Modal(document.getElementById('editStoreModal'));
    loadStoresGrid();

    $("#createStoreForm").on("submit", function (e) {
        e.preventDefault();
        $.post("/Store/Create", $(this).serialize(), function (res) {
            if (res.success) {
                Swal.fire({ icon: 'success', title: 'Created', text: res.message, timer: 1500, showConfirmButton: false });
                createModal.hide();
                $("#createStoreForm")[0].reset();
                $("#storesGrid").data("kendoGrid").dataSource.read();
            } else {
                Swal.fire({ icon: 'error', title: 'Error', text: res.message });
            }
        });
    });

    $("#editStoreForm").on("submit", function (e) {
        e.preventDefault();
        $.post("/Store/Update", $(this).serialize(), function (res) {
            if (res.success) {
                Swal.fire({ icon: 'success', title: 'Updated', text: res.message, timer: 1500, showConfirmButton: false });
                editModal.hide();
                $("#storesGrid").data("kendoGrid").dataSource.read();
            } else {
                Swal.fire({ icon: 'error', title: 'Error', text: res.message });
            }
        });
    });
});

function loadStoresGrid() {
    $("#storesGrid").kendoGrid({
        dataSource: {
            transport: { read: { url: "/Store/GetStoresJson", dataType: "json" } },
            schema: {
                model: {
                    id: "StoreId",
                    fields: {
                        StoreId:   { type: "number" },
                        StoreCode: { type: "string" },
                        StoreName: { type: "string" },
                        Phone:     { type: "string" },
                        Address:   { type: "string" },
                        IsActive:  { type: "number" }
                    }
                }
            },
            pageSize: 10
        },
        pageable: true,
        sortable: true,
        filterable: true,
        columns: [
            { field: "StoreCode", title: "Code", width: 120 },
            { field: "StoreName", title: "Store Name" },
            { field: "Phone", title: "Phone", width: 140 },
            { field: "Address", title: "Address" },
            {
                field: "IsActive", title: "Status", width: 120,
                template: d => d.IsActive === 1 ? '<span class="badge bg-success">Active</span>' : '<span class="badge bg-secondary">Inactive</span>'
            },
            {
                title: "Actions", width: 160, filterable: false, sortable: false,
                template: d => `
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="openEditModal(${d.StoreId}, '${(d.StoreName||'').replace(/'/g,"\\'")}', '${(d.Phone||'').replace(/'/g,"\\'")}', '${(d.Address||'').replace(/'/g,"\\'")}', ${d.IsActive})">Edit</button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteStore(${d.StoreId})">Delete</button>
                `
            }
        ]
    });
}

function openCreateModal() {
    $("#createStoreForm")[0].reset();
    createModal.show();
}

function openEditModal(id, name, phone, address, isActive) {
    $("#edit_storeId").val(id);
    $("#edit_storeName").val(name);
    $("#edit_phone").val(phone);
    $("#edit_address").val(address);
    $("#edit_isActive").prop("checked", isActive === 1);
    editModal.show();
}

function deleteStore(storeId) {
    Swal.fire({
        title: 'Deactivate Store?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, Deactivate'
    }).then((res) => {
        if (res.isConfirmed) {
            $.post("/Store/Delete", { storeId: storeId }, function (r) {
                $("#storesGrid").data("kendoGrid").dataSource.read();
            });
        }
    });
}

```

#### `invoice-create.js`
```javascript
// invoice-create.js - New Invoice (POS) page logic

var cart = [];
var selectedProduct = null;

$(document).ready(function () {
    initProductDropdown();
});

function initProductDropdown() {
    $("#productDropdown").kendoDropDownList({
        dataTextField: "ProductName",
        dataValueField: "ProductId",
        filter: "contains",
        optionLabel: "-- Choose a product --",
        template: d => d.ProductId ? `${d.ProductName} [Code: ${d.ProductCode}] - Rs.${parseFloat(d.Price).toFixed(2)} (Stock: ${d.Quantity})` : d.ProductName,
        dataSource: {
            transport: { read: { url: "/Product/GetProductsJson", dataType: "json" } },
            schema: {
                parse: function (response) {
                    return response.filter(x => x.Quantity > 0);
                }
            }
        },
        change: function (e) {
            var item = this.dataItem();
            if (item && item.ProductId) {
                selectedProduct = item;
                $("#txtPrice").val(parseFloat(item.Price).toFixed(2));
                $("#numQty").attr("max", item.Quantity).val(1);
            } else {
                selectedProduct = null;
                $("#txtPrice").val("0.00");
            }
        }
    });
}

function addItemToCart() {
    if (!selectedProduct) {
        Swal.fire({ icon: 'warning', title: 'Select Product', text: 'Please select a product first.' });
        return;
    }

    var qty = parseInt($("#numQty").val()) || 1;
    if (qty <= 0) {
        Swal.fire({ icon: 'warning', title: 'Invalid Qty', text: 'Quantity must be at least 1.' });
        return;
    }

    var existing = cart.find(x => x.productId === selectedProduct.ProductId);
    var maxStock = selectedProduct.Quantity;

    if (existing) {
        if (existing.quantity + qty > maxStock) {
            Swal.fire({ icon: 'warning', title: 'Stock Limit', text: `Cannot add more. Available stock: ${maxStock}` });
            return;
        }
        existing.quantity += qty;
    } else {
        if (qty > maxStock) {
            Swal.fire({ icon: 'warning', title: 'Stock Limit', text: `Only ${maxStock} units available.` });
            return;
        }
        cart.push({
            productId: selectedProduct.ProductId,
            productName: selectedProduct.ProductName,
            unitPrice: parseFloat(selectedProduct.Price),
            quantity: qty,
            maxStock: maxStock
        });
    }

    renderCart();
    // Reset dropdown
    $("#productDropdown").data("kendoDropDownList").value("");
    selectedProduct = null;
    $("#txtPrice").val("0.00");
    $("#numQty").val(1);
}

function renderCart() {
    var $tbody = $("#cartTableBody");
    $tbody.empty();

    if (cart.length === 0) {
        $tbody.html('<tr id="emptyCartRow"><td colspan="6" class="text-center text-muted py-4">No items added yet. Select a product and click Add to Cart.</td></tr>');
        $("#lblTotalItems").text("0");
        $("#lblGrandTotal").text("Rs.0.00");
        return;
    }

    var grandTotal = 0;
    var totalItems = 0;

    cart.forEach((item, index) => {
        var lineTotal = item.quantity * item.unitPrice;
        grandTotal += lineTotal;
        totalItems += item.quantity;

        $tbody.append(`
            <tr>
                <td>${index + 1}</td>
                <td>${item.productName}</td>
                <td class="text-center">${item.quantity}</td>
                <td class="text-end">Rs.${item.unitPrice.toFixed(2)}</td>
                <td class="text-end">Rs.${lineTotal.toFixed(2)}</td>
                <td class="text-center">
                    <button type="button" class="btn btn-sm btn-outline-danger py-0 px-2" onclick="removeItem(${index})">&times;</button>
                </td>
            </tr>
        `);
    });

    $("#lblTotalItems").text(totalItems);
    $("#lblGrandTotal").text("Rs." + grandTotal.toFixed(2));
}

function removeItem(index) {
    cart.splice(index, 1);
    renderCart();
}

function clearCart() {
    cart = [];
    renderCart();
}

function submitInvoice() {
    var custName = $("#txtCustName").val().trim();
    var custPhone = $("#txtCustPhone").val().trim();

    if (!custName) {
        Swal.fire({ icon: 'warning', title: 'Missing Info', text: 'Please enter customer name.' });
        return;
    }

    if (cart.length === 0) {
        Swal.fire({ icon: 'warning', title: 'Empty Cart', text: 'Please add at least one product to the bill.' });
        return;
    }

    $.post("/Invoice/Create", {
        customerName: custName,
        customerPhone: custPhone,
        itemsJson: JSON.stringify(cart)
    }, function (res) {
        if (res.success) {
            Swal.fire({
                icon: 'success',
                title: 'Invoice Created!',
                text: 'Bill No: ' + res.invoiceNo,
                confirmButtonText: 'View History'
            }).then(() => {
                window.location.href = "/Invoice/History";
            });
        } else {
            Swal.fire({ icon: 'error', title: 'Billing Error', text: res.message });
        }
    });
}

```

#### `invoice-history.js`
```javascript
// invoice-history.js - Invoice History page logic

var detailsModal;

$(document).ready(function () {
    detailsModal = new bootstrap.Modal(document.getElementById('invoiceDetailsModal'));
    loadInvoicesGrid();
});

function loadInvoicesGrid() {
    $("#invoicesGrid").kendoGrid({
        dataSource: {
            transport: { read: { url: "/Invoice/GetInvoicesJson", dataType: "json" } },
            schema: {
                model: {
                    id: "InvoiceId",
                    fields: {
                        InvoiceId:     { type: "number" },
                        InvoiceNo:     { type: "string" },
                        CustomerName:  { type: "string" },
                        CustomerPhone: { type: "string" },
                        TotalAmount:   { type: "number" },
                        InvoiceDate:   { type: "date" },
                        CreatedByName: { type: "string" }
                    }
                }
            },
            pageSize: 10
        },
        pageable: true,
        sortable: true,
        filterable: true,
        columns: [
            { field: "InvoiceNo", title: "Invoice No", width: 160 },
            { field: "CustomerName", title: "Customer Name" },
            { field: "CustomerPhone", title: "Phone", width: 140 },
            { field: "CreatedByName", title: "Cashier", width: 140 },
            {
                field: "InvoiceDate", title: "Date", width: 170,
                template: d => kendo.toString(kendo.parseDate(d.InvoiceDate), 'dd-MMM-yyyy hh:mm tt')
            },
            {
                field: "TotalAmount", title: "Total (Rs.)", width: 130,
                template: d => `Rs.${parseFloat(d.TotalAmount).toFixed(2)}`
            },
            {
                title: "Actions", width: 110, filterable: false, sortable: false,
                template: d => `<button class="btn btn-sm btn-outline-primary" onclick="viewDetails(${d.InvoiceId})">Details</button>`
            }
        ]
    });
}

function viewDetails(invoiceId) {
    $.getJSON("/Invoice/GetInvoiceDetailsJson?id=" + invoiceId, function (res) {
        if (res.success && res.header.length > 0) {
            var h = res.header[0];
            $("#modalInvoiceNo, #infoInvNo").text(h.InvoiceNo);
            $("#infoInvDate").text(kendo.toString(kendo.parseDate(h.InvoiceDate), 'dd-MMM-yyyy hh:mm tt'));
            $("#infoCustName").text(h.CustomerName);
            $("#infoCustPhone").text(h.CustomerPhone || "N/A");
            $("#infoBilledBy").text(h.CreatedByName);
            $("#modalGrandTotal").text("Rs." + parseFloat(h.TotalAmount).toFixed(2));

            var $tbody = $("#modalInvoiceDetailsBody");
            $tbody.empty();

            res.details.forEach((d, idx) => {
                $tbody.append(`
                    <tr>
                        <td>${idx + 1}</td>
                        <td>${d.ProductName} <span class="text-muted small">(${d.ProductCode || ''})</span></td>
                        <td class="text-center">${d.Quantity}</td>
                        <td class="text-end">Rs.${parseFloat(d.UnitPrice).toFixed(2)}</td>
                        <td class="text-end">Rs.${parseFloat(d.TotalAmount).toFixed(2)}</td>
                    </tr>
                `);
            });

            detailsModal.show();
        }
    });
}

function printInvoiceModal() {
    var printContents = document.getElementById("printableInvoiceArea").innerHTML;
    var win = window.open('', '', 'height=650,width=800');
    win.document.write('<html><head><title>Print Bill</title>');
    win.document.write('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">');
    win.document.write('</head><body class="p-4">');
    win.document.write(printContents);
    win.document.write('</body></html>');
    win.document.close();
    win.focus();
    setTimeout(() => { win.print(); win.close(); }, 500);
}

```

---

### 5.3.5 Razor Views

#### `Views/Shared/_Layout.cshtml`
```html
@using Microsoft.AspNetCore.Http
@inject IHttpContextAccessor HttpContextAccessor
@{
    var role = HttpContextAccessor.HttpContext?.Session.GetString("Role") ?? "";
    var fullName = HttpContextAccessor.HttpContext?.Session.GetString("FullName") ?? "User";
    var username = HttpContextAccessor.HttpContext?.Session.GetString("Username") ?? "";
    bool isLoggedIn = !string.IsNullOrEmpty(role);
}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>@ViewData["Title"] - Shop Management</title>

    <!-- Bootstrap 5 CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" />

    <!-- FontAwesome 6 -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" />

    <!-- Kendo UI Styles -->
    <link rel="stylesheet" href="https://kendo.cdn.telerik.com/themes/7.0.2/default/default-main.css" />

    <!-- SweetAlert2 -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/sweetalert2@11/dist/sweetalert2.min.css" />

    <style>
        body { font-size: 15px; background: #ffffff; color: #212529; }
        .app-wrapper { display: flex; min-height: 100vh; }
        .sidebar { width: 220px; flex-shrink: 0; background: #ffffff; border-right: 1px solid #dee2e6; }
        .sidebar-link { display: block; padding: 10px 16px; color: #333333; text-decoration: none; font-size: 15px; }
        .sidebar-link:hover { background: #f8f9fa; color: #000000; }
        .sidebar-link.active { font-weight: bold; background: #e9ecef; color: #000000; }
        .main-content { flex: 1; display: flex; flex-direction: column; }
        .page-body { padding: 1.25rem; flex: 1; }
    </style>

    <!-- jQuery & Kendo -->
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <script src="https://kendo.cdn.telerik.com/2023.3.1114/js/kendo.all.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
</head>
<body>
    @if (isLoggedIn)
    {
        <div class="app-wrapper">
            <!-- Sidebar -->
            <aside class="sidebar d-flex flex-column">
                @{
                    var currentPath = (HttpContextAccessor.HttpContext?.Request.Path.Value ?? "").ToLowerInvariant();
                }
                <div class="p-3 border-bottom">
                    <span class="fs-5 fw-bold text-dark">Shop Management</span>
                </div>
                <div class="py-2 flex-grow-1">
                    @if (role.Equals("Admin", StringComparison.OrdinalIgnoreCase))
                    {
                        <a href="/Product/Index" class="sidebar-link @(currentPath == "/product" || currentPath.StartsWith("/product/index") ? "active" : "")">
                            Product Inventory
                        </a>
                        <a href="/Product/Import" class="sidebar-link @(currentPath.Contains("/product/import") ? "active" : "")">
                            Excel Bulk Import
                        </a>
                        <a href="/Employee/Index" class="sidebar-link @(currentPath.Contains("/employee") ? "active" : "")">
                            Desk Logins
                        </a>
                        <a href="/Store/Index" class="sidebar-link @(currentPath.Contains("/store") ? "active" : "")">
                            Stores / Branches
                        </a>
                    }
                    else
                    {
                        <a href="/Invoice/Create" class="sidebar-link @(currentPath.Contains("/invoice/create") ? "active" : "")">
                            New Invoice (POS)
                        </a>
                        <a href="/Invoice/History" class="sidebar-link @(currentPath.Contains("/invoice/history") ? "active" : "")">
                            Invoice History
                        </a>
                    }
                </div>

                <div class="p-3 border-top">
                    <div class="fw-semibold">@fullName</div>
                    <div class="text-muted small">Role: @role</div>
                    <a href="/Account/Logout" class="text-danger small mt-1 d-inline-block">Logout</a>
                </div>
            </aside>

            <!-- Main Content -->
            <div class="main-content">
                <nav class="d-flex align-items-center justify-content-between px-3 border-bottom bg-white" style="height:52px;">
                    <h5 class="m-0 fw-bold">@ViewData["Title"]</h5>
                    <div>
                        <span class="me-3 text-muted">User: <strong>@username</strong> (@role)</span>
                        <a href="/Account/Logout" class="btn btn-outline-danger btn-sm">Logout</a>
                    </div>
                </nav>

                <main role="main" class="page-body">
                    @RenderBody()
                </main>
            </div>
        </div>
    }
    else
    {
        <main role="main">
            @RenderBody()
        </main>
    }

    <!-- Bootstrap 5 JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    @await RenderSectionAsync("Scripts", required: false)
</body>
</html>

```

#### `Views/Account/Login.cshtml`
```html
@{
    ViewData["Title"] = "Login";
    Layout = "_Layout";
}

<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-md-5 col-lg-4">
            <div class="card border shadow-sm">
                <div class="card-header bg-white border-bottom text-center py-3">
                    <h5 class="fw-bold mb-0 text-dark">Shop Management</h5>
                    <small class="text-muted">Sign in to your account</small>
                </div>
                <div class="card-body p-4">
                    @if (ViewBag.Error != null)
                    {
                        <div class="alert alert-danger py-2 small mb-3" role="alert">
                            @ViewBag.Error
                        </div>
                    }

                    <form method="post" action="/Account/Login">
                        <div class="mb-3">
                            <label class="form-label small fw-semibold">Username</label>
                            <input type="text" name="username" id="txtUsername" class="form-control" placeholder="Enter username" required autofocus />
                        </div>

                        <div class="mb-3">
                            <label class="form-label small fw-semibold">Password</label>
                            <input type="password" name="password" id="txtPassword" class="form-control" placeholder="Enter password" required />
                        </div>

                        <button type="submit" class="btn btn-primary w-100 py-2">
                            Sign In
                        </button>
                    </form>

                    <div class="mt-4 pt-3 border-top text-center">
                        <div class="text-muted small mb-2">Demo Credentials:</div>
                        <div class="btn-group btn-group-sm w-100">
                            <button type="button" class="btn btn-outline-secondary" onclick="fillCredentials('admin', 'admin123')">
                                Admin (admin / admin123)
                            </button>
                            <button type="button" class="btn btn-outline-secondary" onclick="fillCredentials('desk1', 'desk123')">
                                Cashier (desk1 / desk123)
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
    function fillCredentials(u, p) {
        document.getElementById('txtUsername').value = u;
        document.getElementById('txtPassword').value = p;
    }
</script>

```

#### `Views/Product/Index.cshtml`
```html
@{
    ViewData["Title"] = "Product Inventory";
    Layout = "_Layout";
}

<div class="d-flex justify-content-between align-items-center mb-3">
    <h4 class="mb-0">Product Inventory</h4>
    <div>
        <a href="/Product/Import" class="btn btn-outline-secondary me-2">Excel Import</a>
        <button type="button" class="btn btn-primary" onclick="openUpsertModal()">+ Add / Upsert Stock</button>
    </div>
</div>

<div id="productsGrid"></div>

<!-- Add / Upsert Modal -->
<div class="modal fade" id="upsertProductModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Add / Upsert Product</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form id="upsertProductForm" enctype="multipart/form-data">
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label fw-semibold">Product Code / SKU *</label>
                        <input type="text" class="form-control" name="productCode" id="upsert_productCode" required />
                        <div class="form-text">Agar code pehle se hai toh stock add ho jayega.</div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-semibold">Product Name *</label>
                        <input type="text" class="form-control" name="productName" id="upsert_productName" required />
                    </div>
                    <div class="row g-2 mb-3">
                        <div class="col-6">
                            <label class="form-label fw-semibold">Quantity *</label>
                            <input type="number" class="form-control" name="quantity" min="0" value="10" required />
                        </div>
                        <div class="col-6">
                            <label class="form-label fw-semibold">Price (₹) *</label>
                            <input type="number" step="0.01" class="form-control" name="price" min="0" value="100.00" required />
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-semibold">Image (Optional)</label>
                        <input type="file" class="form-control" name="imageFile" accept="image/*" onchange="previewImage(this, 'upsert_imgPreview')" />
                        <div class="mt-2 text-center">
                            <img id="upsert_imgPreview" src="/images/products/default-product.svg" style="width:70px;height:70px;object-fit:cover;border:1px solid #ccc;" />
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-primary">Save Product</button>
                </div>
            </form>
        </div>
    </div>
</div>

<!-- Edit Modal -->
<div class="modal fade" id="editProductModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Edit Product Details</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form id="editProductForm" enctype="multipart/form-data">
                <input type="hidden" name="productId" id="edit_productId" />
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label fw-semibold">Product Code (Read-Only)</label>
                        <input type="text" class="form-control bg-light" id="edit_productCode" readonly />
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-semibold">Product Name *</label>
                        <input type="text" class="form-control" name="productName" id="edit_productName" required />
                    </div>
                    <div class="row g-2 mb-3">
                        <div class="col-6">
                            <label class="form-label fw-semibold">Exact Quantity *</label>
                            <input type="number" class="form-control" name="quantity" id="edit_quantity" min="0" required />
                        </div>
                        <div class="col-6">
                            <label class="form-label fw-semibold">Price (₹) *</label>
                            <input type="number" step="0.01" class="form-control" name="price" id="edit_price" min="0" required />
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-semibold">Change Image (Optional)</label>
                        <input type="file" class="form-control" name="imageFile" accept="image/*" onchange="previewImage(this, 'edit_imgPreview')" />
                        <div class="mt-2 text-center">
                            <img id="edit_imgPreview" src="/images/products/default-product.svg" style="width:70px;height:70px;object-fit:cover;border:1px solid #ccc;" />
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-primary">Update Product</button>
                </div>
            </form>
        </div>
    </div>
</div>

@section Scripts {
    <script src="~/js/product.js"></script>
}

```

#### `Views/Product/Import.cshtml`
```html
@using System.Data
@model DataTable
@{
    ViewData["Title"] = "Excel Bulk Product Import";
    Layout = "_Layout";
}

<div class="d-flex align-items-center justify-content-between mb-4">
    <div>
        <h4 class="fw-bold mb-1">Excel Bulk Product Import</h4>
        <p class="text-muted small mb-0">Upload an Excel (.xlsx) file to automatically insert new products or increment stock for existing products.</p>
    </div>
    <div>
        <a href="/Product/DownloadTemplate" class="btn btn-outline-primary">
            <i class="fa-solid fa-download me-1"></i> Download Sample Excel Template
        </a>
    </div>
</div>

<div class="row g-4">
    <div class="col-lg-5">
        <div class="card card-custom p-4">
            <h5 class="fw-bold mb-3"><i class="fa-solid fa-cloud-arrow-up text-primary me-2"></i> Upload Excel File</h5>

            @if (ViewBag.Error != null)
            {
                <div class="alert alert-danger py-2 small mb-3">
                    <i class="fa-solid fa-circle-exclamation me-1"></i> @ViewBag.Error
                </div>
            }

            <form method="post" action="/Product/Import" enctype="multipart/form-data">
                <div class="mb-3">
                    <label class="form-label small fw-semibold">Select Excel File (.xlsx)</label>
                    <input type="file" name="excelFile" class="form-control" accept=".xlsx" required />
                    <div class="form-text small">Accepted columns: ProductCode, ProductName, Quantity, Price</div>
                        <div class="d-flex align-items-center gap-2 mt-2 p-2 rounded" style="background:#f0f4ff;">
                            <img src="/images/products/default-product.svg" style="width:32px;height:32px;border-radius:6px;" />
                            <span class="small" style="color:#4f46e5;">
                                <strong>Image column zaruri nahi hai</strong> — Excel mein image nahi di to sabhi products ko
                                <em>default placeholder image</em> auto-set hogi. Baad mein Edit se change kar sakte ho.
                            </span>
                        </div>
                </div>

                <div class="alert alert-warning py-2 small mb-4">
                    <i class="fa-solid fa-lightbulb me-1"></i> <strong>Upsert Behavior:</strong>
                    If a product with the same ProductCode exists, its stock will be incremented. If it does not exist, a new product will be created.
                </div>

                <button type="submit" class="btn btn-success w-100 py-2 fw-semibold">
                    <i class="fa-solid fa-file-import me-1"></i> Process & Import Products
                </button>
            </form>
        </div>
    </div>

    <div class="col-lg-7">
        @if (ViewBag.Success == true)
        {
            <div class="card card-custom p-4 mb-4">
                <h5 class="fw-bold mb-3"><i class="fa-solid fa-chart-simple text-success me-2"></i> Import Summary</h5>
                <div class="row text-center g-3">
                    <div class="col-3">
                        <div class="p-2 border rounded bg-light">
                            <div class="text-muted small">Total Processed</div>
                            <h4 class="fw-bold text-dark mb-0">@ViewBag.Total</h4>
                        </div>
                    </div>
                    <div class="col-3">
                        <div class="p-2 border rounded bg-light">
                            <div class="text-muted small">New Inserted</div>
                            <h4 class="fw-bold text-success mb-0">@ViewBag.Inserted</h4>
                        </div>
                    </div>
                    <div class="col-3">
                        <div class="p-2 border rounded bg-light">
                            <div class="text-muted small">Stock Updated</div>
                            <h4 class="fw-bold text-primary mb-0">@ViewBag.Updated</h4>
                        </div>
                    </div>
                    <div class="col-3">
                        <div class="p-2 border rounded bg-light">
                            <div class="text-muted small">Failed / Skipped</div>
                            <h4 class="fw-bold text-danger mb-0">@ViewBag.Failed</h4>
                        </div>
                    </div>
                </div>
            </div>

            @if (Model != null && Model.Rows.Count > 0)
            {
                <div class="card card-custom p-4">
                    <h6 class="fw-bold mb-3">Row-by-Row Execution Log</h6>
                    <div class="table-responsive" style="max-height: 400px; overflow-y: auto;">
                        <table class="table table-sm table-hover align-middle">
                            <thead class="table-light sticky-top">
                                <tr>
                                    <th>Row</th>
                                    <th>SKU</th>
                                    <th>Product Name</th>
                                    <th>Qty</th>
                                    <th>Price</th>
                                    <th>Status</th>
                                    <th>Details</th>
                                </tr>
                            </thead>
                            <tbody>
                                @foreach (DataRow row in Model.Rows)
                                {
                                    string status = Convert.ToString(row["Status"]) ?? "";
                                    bool isOk = status.Equals("Success", StringComparison.OrdinalIgnoreCase);
                                    <tr>
                                        <td>@row["RowNumber"]</td>
                                        <td><code>@row["ProductCode"]</code></td>
                                        <td>@row["ProductName"]</td>
                                        <td>@row["Quantity"]</td>
                                        <td>₹@row["Price"]</td>
                                        <td>
                                            <span class="badge @(isOk ? "bg-success" : "bg-danger")">@status</span>
                                        </td>
                                        <td class="small text-muted">@row["Message"]</td>
                                    </tr>
                                }
                            </tbody>
                        </table>
                    </div>
                </div>
            }
        }
        else
        {
            <div class="card card-custom p-5 text-center text-muted">
                <i class="fa-solid fa-file-excel fa-4x mb-3 text-secondary" style="opacity: 0.4;"></i>
                <h6 class="fw-bold">No Import Run Yet</h6>
                <p class="small mb-0">Select an Excel spreadsheet on the left and submit to process inventory items.</p>
            </div>
        }
    </div>
</div>

```

#### `Views/Employee/Index.cshtml`
```html
@{
    ViewData["Title"] = "Desk Logins";
    Layout = "_Layout";
}

<div class="d-flex justify-content-between align-items-center mb-3">
    <h4 class="mb-0">Desk Logins (Staff Accounts)</h4>
    <button type="button" class="btn btn-primary" onclick="openAddModal()">+ Create Desk Login</button>
</div>

<div id="employeesGrid"></div>

<!-- Add Modal -->
<div class="modal fade" id="addEmployeeModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">New Desk Login</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form id="addEmployeeForm">
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label fw-semibold">Staff Full Name *</label>
                        <input type="text" name="name" class="form-control" required />
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-semibold">Username *</label>
                        <input type="text" name="username" class="form-control" required />
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-semibold">Password *</label>
                        <input type="password" name="password" class="form-control" required />
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-primary">Create Login</button>
                </div>
            </form>
        </div>
    </div>
</div>

<!-- Edit Modal -->
<div class="modal fade" id="editEmployeeModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Edit Desk Login</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form id="editEmployeeForm">
                <input type="hidden" name="userId" id="edit_userId" />
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label fw-semibold">Staff Full Name *</label>
                        <input type="text" name="name" id="edit_name" class="form-control" required />
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-semibold">New Password (leave blank to keep current)</label>
                        <input type="password" name="password" class="form-control" placeholder="••••••••" />
                    </div>
                    <div class="form-check mb-3">
                        <input type="checkbox" name="isActive" id="edit_isActive" value="true" class="form-check-input" />
                        <label class="form-check-label" for="edit_isActive">Active (can login)</label>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-primary">Update Login</button>
                </div>
            </form>
        </div>
    </div>
</div>

@section Scripts {
    <script src="~/js/employee.js"></script>
}


```

#### `Views/Store/Index.cshtml`
```html
@{
    ViewData["Title"] = "Stores / Branches";
    Layout = "_Layout";
}

<div class="d-flex justify-content-between align-items-center mb-3">
    <h4 class="mb-0">Stores & Branch Management</h4>
    <button type="button" class="btn btn-primary" onclick="openCreateModal()">+ Create New Branch</button>
</div>

<div id="storesGrid"></div>

<!-- Create Modal -->
<div class="modal fade" id="createStoreModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Create Store Branch</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form id="createStoreForm">
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label fw-semibold">Store Code *</label>
                        <input type="text" class="form-control" name="storeCode" placeholder="e.g. BR02" required />
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-semibold">Store Name *</label>
                        <input type="text" class="form-control" name="storeName" placeholder="e.g. West Branch" required />
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-semibold">Phone</label>
                        <input type="text" class="form-control" name="phone" placeholder="9800000001" />
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-semibold">Address</label>
                        <input type="text" class="form-control" name="address" placeholder="Store address" />
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-primary">Save Store</button>
                </div>
            </form>
        </div>
    </div>
</div>

<!-- Edit Modal -->
<div class="modal fade" id="editStoreModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Edit Store Branch</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form id="editStoreForm">
                <input type="hidden" name="storeId" id="edit_storeId" />
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label fw-semibold">Store Name *</label>
                        <input type="text" class="form-control" name="storeName" id="edit_storeName" required />
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-semibold">Phone</label>
                        <input type="text" class="form-control" name="phone" id="edit_phone" />
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-semibold">Address</label>
                        <input type="text" class="form-control" name="address" id="edit_address" />
                    </div>
                    <div class="form-check mb-3">
                        <input type="checkbox" class="form-check-input" name="isActive" id="edit_isActive" value="true" />
                        <label class="form-check-label" for="edit_isActive">Active Branch</label>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-primary">Update Store</button>
                </div>
            </form>
        </div>
    </div>
</div>

@section Scripts {
    <script src="~/js/store.js"></script>
}


```

#### `Views/Invoice/Create.cshtml`
```html
@{
    ViewData["Title"] = "New Customer Invoice (POS)";
    Layout = "_Layout";
}

<div class="d-flex justify-content-between align-items-center mb-3">
    <h4 class="mb-0">New Invoice (Billing POS)</h4>
    <a href="/Invoice/History" class="btn btn-outline-secondary">Invoice History</a>
</div>

<div class="row g-3">
    <!-- Left Column: Customer details & product selector -->
    <div class="col-md-5">
        <div class="border p-3 rounded mb-3 bg-white">
            <h6 class="fw-bold mb-3">1. Customer Information</h6>
            <div class="mb-3">
                <label class="form-label fw-semibold">Customer Name *</label>
                <input type="text" class="form-control" id="txtCustName" placeholder="e.g. Ramesh Sharma" required />
            </div>
            <div class="mb-2">
                <label class="form-label fw-semibold">Phone Number</label>
                <input type="text" class="form-control" id="txtCustPhone" placeholder="e.g. 9876543210" />
            </div>
        </div>

        <div class="border p-3 rounded bg-white">
            <h6 class="fw-bold mb-3">2. Add Product to Bill</h6>
            <div class="mb-3">
                <label class="form-label fw-semibold">Search / Select Product *</label>
                <input id="productDropdown" style="width: 100%;" />
            </div>
            <div class="row g-2 mb-3">
                <div class="col-6">
                    <label class="form-label fw-semibold">Quantity *</label>
                    <input type="number" class="form-control" id="numQty" value="1" min="1" />
                </div>
                <div class="col-6">
                    <label class="form-label fw-semibold">Unit Price (₹)</label>
                    <input type="text" class="form-control bg-light" id="txtPrice" readonly value="0.00" />
                </div>
            </div>
            <button type="button" class="btn btn-primary w-100" onclick="addItemToCart()">+ Add to Cart</button>
        </div>
    </div>

    <!-- Right Column: Cart items table & Billing summary -->
    <div class="col-md-7">
        <div class="border p-3 rounded bg-white">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h6 class="fw-bold mb-0">3. Invoice Items Cart</h6>
                <button type="button" class="btn btn-sm btn-outline-secondary" onclick="clearCart()">Clear</button>
            </div>

            <table class="table table-bordered align-middle">
                <thead class="table-light">
                    <tr>
                        <th>#</th>
                        <th>Product</th>
                        <th class="text-center" style="width:90px;">Qty</th>
                        <th class="text-end" style="width:110px;">Price</th>
                        <th class="text-end" style="width:110px;">Total</th>
                        <th style="width:50px;"></th>
                    </tr>
                </thead>
                <tbody id="cartTableBody">
                    <tr id="emptyCartRow">
                        <td colspan="6" class="text-center text-muted py-4">No items added yet. Select a product and click Add to Cart.</td>
                    </tr>
                </tbody>
            </table>

            <div class="d-flex justify-content-between align-items-center pt-2 border-top">
                <div>
                    Total Items: <strong id="lblTotalItems">0</strong>
                </div>
                <div class="text-end">
                    <span class="fs-5 me-2">Grand Total:</span>
                    <strong class="fs-4 text-primary" id="lblGrandTotal">₹0.00</strong>
                </div>
            </div>

            <button type="button" class="btn btn-success w-100 mt-3 py-2 fs-5" onclick="submitInvoice()">
                Confirm & Generate Invoice
            </button>
        </div>
    </div>
</div>

@section Scripts {
    <script src="~/js/invoice-create.js"></script>
}


```

#### `Views/Invoice/History.cshtml`
```html
@{
    ViewData["Title"] = "Invoice History";
    Layout = "_Layout";
}

<div class="d-flex justify-content-between align-items-center mb-3">
    <h4 class="mb-0">Invoice History</h4>
    <a href="/Invoice/Create" class="btn btn-primary">+ New Invoice (POS)</a>
</div>

<div id="invoicesGrid"></div>

<!-- Invoice Details Modal -->
<div class="modal fade" id="invoiceDetailsModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Invoice: <span id="modalInvoiceNo"></span></h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body" id="printableInvoiceArea">
                <div class="d-flex justify-content-between border-bottom pb-2 mb-3">
                    <div>
                        <h5 class="mb-0">Shop Management</h5>
                        <div class="text-muted small">Sales Receipt</div>
                    </div>
                    <div class="text-end small">
                        <div><strong>Invoice:</strong> <span id="infoInvNo"></span></div>
                        <div><strong>Date:</strong> <span id="infoInvDate"></span></div>
                        <div><strong>Cashier:</strong> <span id="infoBilledBy"></span></div>
                    </div>
                </div>

                <div class="mb-3 small">
                    <strong>Customer:</strong> <span id="infoCustName"></span> | 
                    <strong>Phone:</strong> <span id="infoCustPhone"></span>
                </div>

                <table class="table table-bordered table-sm align-middle">
                    <thead class="table-light">
                        <tr>
                            <th>#</th>
                            <th>Product</th>
                            <th class="text-center" style="width:80px;">Qty</th>
                            <th class="text-end" style="width:110px;">Price</th>
                            <th class="text-end" style="width:110px;">Total</th>
                        </tr>
                    </thead>
                    <tbody id="modalInvoiceDetailsBody"></tbody>
                    <tfoot>
                        <tr>
                            <th colspan="4" class="text-end">Grand Total:</th>
                            <th class="text-end" id="modalGrandTotal">₹0.00</th>
                        </tr>
                    </tfoot>
                </table>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                <button type="button" class="btn btn-outline-dark" onclick="printInvoiceModal()">Print Bill</button>
            </div>
        </div>
    </div>
</div>

@section Scripts {
    <script src="~/js/invoice-history.js"></script>
}


```

#### `Views/Dashboard/Index.cshtml`
```html
@using System.Data
@model DataTable
@{
    ViewData["Title"] = "Dashboard Overview";
    Layout = "_Layout";

    long totalProducts = 0;
    long lowStock = 0;
    long totalInvoices = 0;
    decimal totalRevenue = 0;
    long totalEmployees = 0;

    if (Model != null && Model.Rows.Count > 0)
    {
        var row = Model.Rows[0];
        totalProducts = Convert.ToInt64(row["TotalProducts"]);
        lowStock = Convert.ToInt64(row["LowStockProducts"]);
        totalInvoices = Convert.ToInt64(row["TotalInvoices"]);
        totalRevenue = Convert.ToDecimal(row["TotalRevenue"]);
        totalEmployees = Convert.ToInt64(row["TotalEmployees"]);
    }
}

<div class="row g-3 mb-4">
    <!-- Total Products -->
    <div class="col-12 col-sm-6 col-xl-3">
        <div class="card card-custom p-3 h-100">
            <div class="d-flex align-items-center justify-content-between">
                <div>
                    <span class="text-muted small fw-medium text-uppercase">Total Inventory</span>
                    <h3 class="fw-bold mt-1 mb-0 text-dark">@totalProducts</h3>
                </div>
                <div class="p-3 rounded-3" style="background-color: #e0e7ff; color: #4f46e5;">
                    <i class="fa-solid fa-boxes-stacked fa-xl"></i>
                </div>
            </div>
            <div class="mt-3">
                <a href="/Product" class="small text-primary text-decoration-none fw-semibold">
                    View Products <i class="fa-solid fa-arrow-right ms-1"></i>
                </a>
            </div>
        </div>
    </div>

    <!-- Low Stock Alert -->
    <div class="col-12 col-sm-6 col-xl-3">
        <div class="card card-custom p-3 h-100">
            <div class="d-flex align-items-center justify-content-between">
                <div>
                    <span class="text-muted small fw-medium text-uppercase">Low Stock Alert</span>
                    <h3 class="fw-bold mt-1 mb-0 text-warning">@lowStock</h3>
                </div>
                <div class="p-3 rounded-3" style="background-color: #fef3c7; color: #d97706;">
                    <i class="fa-solid fa-triangle-exclamation fa-xl"></i>
                </div>
            </div>
            <div class="mt-3">
                <span class="text-muted small">&le; 10 units remaining</span>
            </div>
        </div>
    </div>

    <!-- Total Invoices -->
    <div class="col-12 col-sm-6 col-xl-3">
        <div class="card card-custom p-3 h-100">
            <div class="d-flex align-items-center justify-content-between">
                <div>
                    <span class="text-muted small fw-medium text-uppercase">Invoices Issued</span>
                    <h3 class="fw-bold mt-1 mb-0 text-dark">@totalInvoices</h3>
                </div>
                <div class="p-3 rounded-3" style="background-color: #dcfce7; color: #16a34a;">
                    <i class="fa-solid fa-file-invoice-dollar fa-xl"></i>
                </div>
            </div>
            <div class="mt-3">
                <a href="/Invoice/History" class="small text-success text-decoration-none fw-semibold">
                    View History <i class="fa-solid fa-arrow-right ms-1"></i>
                </a>
            </div>
        </div>
    </div>

    <!-- Total Revenue -->
    <div class="col-12 col-sm-6 col-xl-3">
        <div class="card card-custom p-3 h-100">
            <div class="d-flex align-items-center justify-content-between">
                <div>
                    <span class="text-muted small fw-medium text-uppercase">Total Sales</span>
                    <h3 class="fw-bold mt-1 mb-0 text-dark">₹@totalRevenue.ToString("N2")</h3>
                </div>
                <div class="p-3 rounded-3" style="background-color: #f3e8ff; color: #9333ea;">
                    <i class="fa-solid fa-indian-rupee-sign fa-xl"></i>
                </div>
            </div>
            <div class="mt-3">
                <span class="text-muted small">Active Employees: <strong>@totalEmployees</strong></span>
            </div>
        </div>
    </div>
</div>

<!-- Quick Action Shortcuts -->
<div class="card card-custom p-4 mb-4">
    <h5 class="fw-bold mb-3"><i class="fa-solid fa-bolt me-2 text-primary"></i> Quick Operations</h5>
    <div class="row g-3">
        <div class="col-md-3">
            <a href="/Invoice/Create" class="btn btn-primary w-100 py-3 d-flex flex-column align-items-center gap-2 rounded-3 shadow-sm">
                <i class="fa-solid fa-receipt fa-2x"></i>
                <span class="fw-semibold">Generate New Invoice</span>
            </a>
        </div>
        <div class="col-md-3">
            <a href="/Product" class="btn btn-outline-primary w-100 py-3 d-flex flex-column align-items-center gap-2 rounded-3">
                <i class="fa-solid fa-box-open fa-2x"></i>
                <span class="fw-semibold">Add / Update Product</span>
            </a>
        </div>
        <div class="col-md-3">
            <a href="/Product/Import" class="btn btn-outline-success w-100 py-3 d-flex flex-column align-items-center gap-2 rounded-3">
                <i class="fa-solid fa-file-excel fa-2x"></i>
                <span class="fw-semibold">Excel Bulk Import</span>
            </a>
        </div>
        <div class="col-md-3">
            <a href="/Employee" class="btn btn-outline-dark w-100 py-3 d-flex flex-column align-items-center gap-2 rounded-3">
                <i class="fa-solid fa-user-plus fa-2x"></i>
                <span class="fw-semibold">Create Desk Login</span>
            </a>
        </div>
    </div>
</div>

```

---

# 6. Architectural Decisions & Data Flow Lifecycle
- **Stored Procedures:** Centralized schema governance, execution plan caching, SQL injection immunity.
- **Transactions & Row Locks:** `sp_CheckProductStock` uses `FOR UPDATE` lock to guarantee stock safety in concurrent checkout environments.
- **Frontend Isolation:** All scripts reside in `wwwroot/js/` for clean separation and browser caching.

---

# 7. Step-by-Step Setup, Build & Run Guide
1. Run `ShopManagement_Full_Setup.sql` in MySQL.
2. Check `appsettings.json` connection string.
3. Run:
   ```bash
   dotnet restore
   dotnet build ShopManagement.slnx -c Release
   dotnet run --project ShopManagement.Web
   ```
