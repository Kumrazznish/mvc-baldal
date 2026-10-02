-- ============================================================================
-- STORED PROCEDURES SETUP SCRIPT: ShopManagementDB
-- ============================================================================
-- Contains all 19 enterprise Stored Procedures for ShopManagement System.
-- ============================================================================
USE ShopManagementDB;

DELIMITER $$

-- ------------------------------------------------------------
-- 1. ACCOUNT MODULE
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_ValidateUser$$
CREATE PROCEDURE sp_ValidateUser(
    IN p_Username VARCHAR(100),
    IN p_Password VARCHAR(255)
)
BEGIN
    SELECT UserId, Name, Username, Role, StoreId, IsActive 
    FROM Users 
    WHERE Username = p_Username AND PasswordHash = p_Password AND IsActive = 1;
END$$

-- ------------------------------------------------------------
-- 2. EMPLOYEE MODULE
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_GetAllEmployees$$
CREATE PROCEDURE sp_GetAllEmployees()
BEGIN
    SELECT u.UserId, u.Name, u.Username, u.Role, u.IsActive, u.CreatedDate,
           u.StoreId, COALESCE(s.StoreName, 'Main Branch') AS StoreName
    FROM Users u
    LEFT JOIN Stores s ON s.StoreId = u.StoreId
    WHERE u.Role = 'Employee'
    ORDER BY u.UserId DESC;
END$$

DROP PROCEDURE IF EXISTS sp_GetEmployeeById$$
CREATE PROCEDURE sp_GetEmployeeById(
    IN p_UserId INT
)
BEGIN
    SELECT u.UserId, u.Name, u.Username, u.Role, u.IsActive, u.StoreId,
           COALESCE(s.StoreName, 'Main Branch') AS StoreName
    FROM Users u
    LEFT JOIN Stores s ON s.StoreId = u.StoreId
    WHERE u.UserId = p_UserId;
END$$

DROP PROCEDURE IF EXISTS sp_CreateEmployee$$
CREATE PROCEDURE sp_CreateEmployee(
    IN p_Name VARCHAR(100),
    IN p_Username VARCHAR(100),
    IN p_Password VARCHAR(255),
    IN p_StoreId INT
)
BEGIN
    INSERT INTO Users (Name, Username, PasswordHash, Role, StoreId, IsActive, CreatedDate)
    VALUES (p_Name, p_Username, p_Password, 'Employee', p_StoreId, 1, NOW());
END$$

DROP PROCEDURE IF EXISTS sp_UpdateEmployee$$
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
END$$

DROP PROCEDURE IF EXISTS sp_ResetEmployeePassword$$
CREATE PROCEDURE sp_ResetEmployeePassword(
    IN p_UserId INT,
    IN p_Password VARCHAR(255)
)
BEGIN
    UPDATE Users 
    SET PasswordHash = p_Password, UpdatedDate = NOW() 
    WHERE UserId = p_UserId;
END$$

DROP PROCEDURE IF EXISTS sp_ToggleEmployeeStatus$$
CREATE PROCEDURE sp_ToggleEmployeeStatus(
    IN p_UserId INT
)
BEGIN
    UPDATE Users 
    SET IsActive = CASE WHEN IsActive = 1 THEN 0 ELSE 1 END, UpdatedDate = NOW() 
    WHERE UserId = p_UserId;
END$$

DROP PROCEDURE IF EXISTS sp_DeleteEmployee$$
CREATE PROCEDURE sp_DeleteEmployee(
    IN p_UserId INT
)
BEGIN
    UPDATE Users 
    SET IsActive = 0, UpdatedDate = NOW() 
    WHERE UserId = p_UserId;
END$$

-- ------------------------------------------------------------
-- 3. PRODUCT MODULE
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_GetAllProducts$$
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
END$$

DROP PROCEDURE IF EXISTS sp_GetProductById$$
CREATE PROCEDURE sp_GetProductById(
    IN p_ProductId INT
)
BEGIN
    SELECT ProductId, ProductCode, ProductName, Quantity, Price, ImagePath, IsActive 
    FROM Products 
    WHERE ProductId = p_ProductId;
END$$

DROP PROCEDURE IF EXISTS sp_CheckProductExists$$
CREATE PROCEDURE sp_CheckProductExists(
    IN p_ProductCode VARCHAR(50),
    IN p_ProductName VARCHAR(200)
)
BEGIN
    SELECT ProductId, ProductCode, ProductName, Quantity, Price, ImagePath 
    FROM Products 
    WHERE ProductCode = p_ProductCode OR LOWER(ProductName) = LOWER(p_ProductName) 
    LIMIT 1;
END$$

DROP PROCEDURE IF EXISTS sp_CreateProduct$$
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
END$$

DROP PROCEDURE IF EXISTS sp_UpdateProduct$$
CREATE PROCEDURE sp_UpdateProduct(
    IN p_ProductId INT,
    IN p_ProductName VARCHAR(200),
    IN p_Quantity INT,
    IN p_Price DECIMAL(18,2),
    IN p_ImagePath VARCHAR(500)
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
END$$

DROP PROCEDURE IF EXISTS sp_DeleteProduct$$
CREATE PROCEDURE sp_DeleteProduct(
    IN p_ProductId INT
)
BEGIN
    UPDATE Products 
    SET IsActive = 0, UpdatedDate = NOW() 
    WHERE ProductId = p_ProductId;
END$$

DROP PROCEDURE IF EXISTS sp_SearchAvailableProducts$$
CREATE PROCEDURE sp_SearchAvailableProducts(
    IN p_Term VARCHAR(100)
)
BEGIN
    SELECT ProductId, ProductCode, ProductName, Quantity, Price, ImagePath
    FROM Products
    WHERE IsActive = 1 AND Quantity > 0
      AND (ProductName LIKE CONCAT('%', p_Term, '%') OR ProductCode LIKE CONCAT('%', p_Term, '%'))
    ORDER BY ProductName ASC;
END$$

-- ------------------------------------------------------------
-- 4. STORE MODULE
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_GetAllStores$$
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
END$$

DROP PROCEDURE IF EXISTS sp_GetStoreById$$
CREATE PROCEDURE sp_GetStoreById(
    IN p_StoreId INT
)
BEGIN
    SELECT StoreId, StoreCode, StoreName, Address, Phone, Email, IsActive 
    FROM Stores 
    WHERE StoreId = p_StoreId;
END$$

DROP PROCEDURE IF EXISTS sp_CreateStore$$
CREATE PROCEDURE sp_CreateStore(
    IN p_StoreCode VARCHAR(50),
    IN p_StoreName VARCHAR(200),
    IN p_Address VARCHAR(500),
    IN p_Phone VARCHAR(20),
    IN p_Email VARCHAR(150)
)
BEGIN
    INSERT INTO Stores (StoreCode, StoreName, Address, Phone, Email, IsActive, CreatedDate)
    VALUES (p_StoreCode, p_StoreName, p_Address, p_Phone, p_Email, 1, NOW());
END$$

DROP PROCEDURE IF EXISTS sp_UpdateStore$$
CREATE PROCEDURE sp_UpdateStore(
    IN p_StoreId INT,
    IN p_StoreName VARCHAR(200),
    IN p_Address VARCHAR(500),
    IN p_Phone VARCHAR(20),
    IN p_Email VARCHAR(150),
    IN p_IsActive TINYINT(1)
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
END$$

DROP PROCEDURE IF EXISTS sp_DeleteStore$$
CREATE PROCEDURE sp_DeleteStore(
    IN p_StoreId INT
)
BEGIN
    UPDATE Stores 
    SET IsActive = 0, 
        UpdatedDate = NOW() 
    WHERE StoreId = p_StoreId;
END$$

DROP PROCEDURE IF EXISTS sp_GetStoreStats$$
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
END$$

-- ------------------------------------------------------------
-- 5. INVOICE MODULE
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_GetInvoiceHistory$$
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
END$$

DROP PROCEDURE IF EXISTS sp_GetInvoiceHeader$$
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
END$$

DROP PROCEDURE IF EXISTS sp_GetInvoiceDetails$$
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
END$$

-- Invoice Creation Stored Procedures
DROP PROCEDURE IF EXISTS sp_CheckProductStock$$
CREATE PROCEDURE sp_CheckProductStock(
    IN p_ProductId INT
)
BEGIN
    SELECT ProductId, ProductName, Quantity
    FROM Products
    WHERE ProductId = p_ProductId AND IsActive = 1
    FOR UPDATE;
END$$

DROP PROCEDURE IF EXISTS sp_InsertInvoiceHeader$$
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
END$$

DROP PROCEDURE IF EXISTS sp_InsertInvoiceDetail$$
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
END$$

DROP PROCEDURE IF EXISTS sp_DeductProductStock$$
CREATE PROCEDURE sp_DeductProductStock(
    IN p_ProductId INT,
    IN p_Quantity  INT
)
BEGIN
    UPDATE Products
    SET Quantity    = Quantity - p_Quantity,
        UpdatedDate = NOW()
    WHERE ProductId = p_ProductId;
END$$

-- ------------------------------------------------------------
-- 6. DASHBOARD MODULE
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_GetDashboardMetrics$$
CREATE PROCEDURE sp_GetDashboardMetrics()
BEGIN
    SELECT 
        (SELECT COUNT(*) FROM Products WHERE IsActive = 1) AS TotalProducts,
        (SELECT COUNT(*) FROM Products WHERE IsActive = 1 AND Quantity <= 10) AS LowStockProducts,
        (SELECT COUNT(*) FROM Invoices) AS TotalInvoices,
        (SELECT COALESCE(SUM(TotalAmount), 0) FROM Invoices) AS TotalRevenue,
        (SELECT COUNT(*) FROM Users WHERE Role = 'Employee' AND IsActive = 1) AS TotalEmployees;
END$$

DELIMITER ;
