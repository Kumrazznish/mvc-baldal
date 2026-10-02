import os
import re
import html
import subprocess
import json

workspace_root = r"d:\Download\mv-baldal"

def read_file(rel_path):
    full_path = os.path.join(workspace_root, rel_path)
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    return f"// File not found: {rel_path}"

# Read all real active source files
db_helper_code = read_file(r"ShopManagement.DataAccess\DbHelper.cs")
account_dal_code = read_file(r"ShopManagement.DataAccess\AccountDAL.cs")
employee_dal_code = read_file(r"ShopManagement.DataAccess\EmployeeDAL.cs")
store_dal_code = read_file(r"ShopManagement.DataAccess\StoreDAL.cs")
product_dal_code = read_file(r"ShopManagement.DataAccess\ProductDAL.cs")
invoice_dal_code = read_file(r"ShopManagement.DataAccess\InvoiceDAL.cs")

account_bal_code = read_file(r"ShopManagement.Business\AccountBAL.cs")
employee_bal_code = read_file(r"ShopManagement.Business\EmployeeBAL.cs")
store_bal_code = read_file(r"ShopManagement.Business\StoreBAL.cs")
product_bal_code = read_file(r"ShopManagement.Business\ProductBAL.cs")
invoice_bal_code = read_file(r"ShopManagement.Business\InvoiceBAL.cs")
excel_bal_code = read_file(r"ShopManagement.Business\ExcelBAL.cs")

account_ctrl_code = read_file(r"ShopManagement.Web\Controllers\AccountController.cs")
dashboard_ctrl_code = read_file(r"ShopManagement.Web\Controllers\DashboardController.cs")
employee_ctrl_code = read_file(r"ShopManagement.Web\Controllers\EmployeeController.cs")
store_ctrl_code = read_file(r"ShopManagement.Web\Controllers\StoreController.cs")
product_ctrl_code = read_file(r"ShopManagement.Web\Controllers\ProductController.cs")
invoice_ctrl_code = read_file(r"ShopManagement.Web\Controllers\InvoiceController.cs")

employee_js = read_file(r"ShopManagement.Web\wwwroot\js\employee.js")
product_js = read_file(r"ShopManagement.Web\wwwroot\js\product.js")
store_js = read_file(r"ShopManagement.Web\wwwroot\js\store.js")
invoice_create_js = read_file(r"ShopManagement.Web\wwwroot\js\invoice-create.js")
invoice_history_js = read_file(r"ShopManagement.Web\wwwroot\js\invoice-history.js")

layout_view = read_file(r"ShopManagement.Web\Views\Shared\_Layout.cshtml")
login_view = read_file(r"ShopManagement.Web\Views\Account\Login.cshtml")
product_index_view = read_file(r"ShopManagement.Web\Views\Product\Index.cshtml")
product_import_view = read_file(r"ShopManagement.Web\Views\Product\Import.cshtml")
employee_index_view = read_file(r"ShopManagement.Web\Views\Employee\Index.cshtml")
store_index_view = read_file(r"ShopManagement.Web\Views\Store\Index.cshtml")
invoice_create_view = read_file(r"ShopManagement.Web\Views\Invoice\Create.cshtml")
invoice_history_view = read_file(r"ShopManagement.Web\Views\Invoice\History.cshtml")
dashboard_index_view = read_file(r"ShopManagement.Web\Views\Dashboard\Index.cshtml")

full_sql_code = read_file("ShopManagement_Full_Setup.sql")
appsettings_code = read_file(r"ShopManagement.Web\appsettings.json")
program_cs_code = read_file(r"ShopManagement.Web\Program.cs")

# Write Markdown Documentation
print("Writing PROJECT_DOCUMENTATION.md...")
md_path = os.path.join(workspace_root, "PROJECT_DOCUMENTATION.md")
# (reusing previous comprehensive MD content structure)
md_content = f"""# 🏪 Shop Management System (3-Tier Enterprise Architecture) — Complete Project Guide & Documentation

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
{full_sql_code}
```

---

# 5. Layer-by-Layer Complete Active Source Code

## 5.1 Data Access Layer (ShopManagement.DataAccess)

### 5.1.1 `DbHelper.cs`
```csharp
{db_helper_code}
```

### 5.1.2 `AccountDAL.cs`
```csharp
{account_dal_code}
```

### 5.1.3 `EmployeeDAL.cs`
```csharp
{employee_dal_code}
```

### 5.1.4 `StoreDAL.cs`
```csharp
{store_dal_code}
```

### 5.1.5 `ProductDAL.cs`
```csharp
{product_dal_code}
```

### 5.1.6 `InvoiceDAL.cs`
```csharp
{invoice_dal_code}
```

---

## 5.2 Business Access Layer (ShopManagement.Business)

### 5.2.1 `AccountBAL.cs`
```csharp
{account_bal_code}
```

### 5.2.2 `EmployeeBAL.cs`
```csharp
{employee_bal_code}
```

### 5.2.3 `StoreBAL.cs`
```csharp
{store_bal_code}
```

### 5.2.4 `ProductBAL.cs`
```csharp
{product_bal_code}
```

### 5.2.5 `InvoiceBAL.cs`
```csharp
{invoice_bal_code}
```

### 5.2.6 `ExcelBAL.cs`
```csharp
{excel_bal_code}
```

---

## 5.3 Web Presentation Layer (ShopManagement.Web)

### 5.3.1 `Program.cs`
```csharp
{program_cs_code}
```

### 5.3.2 `appsettings.json`
```json
{appsettings_code}
```

### 5.3.3 Controllers

#### `AccountController.cs`
```csharp
{account_ctrl_code}
```

#### `DashboardController.cs`
```csharp
{dashboard_ctrl_code}
```

#### `EmployeeController.cs`
```csharp
{employee_ctrl_code}
```

#### `StoreController.cs`
```csharp
{store_ctrl_code}
```

#### `ProductController.cs`
```csharp
{product_ctrl_code}
```

#### `InvoiceController.cs`
```csharp
{invoice_ctrl_code}
```

---

### 5.3.4 Standalone Frontend JavaScript (`wwwroot/js/`)

#### `employee.js`
```javascript
{employee_js}
```

#### `product.js`
```javascript
{product_js}
```

#### `store.js`
```javascript
{store_js}
```

#### `invoice-create.js`
```javascript
{invoice_create_js}
```

#### `invoice-history.js`
```javascript
{invoice_history_js}
```

---

### 5.3.5 Razor Views

#### `Views/Shared/_Layout.cshtml`
```html
{layout_view}
```

#### `Views/Account/Login.cshtml`
```html
{login_view}
```

#### `Views/Product/Index.cshtml`
```html
{product_index_view}
```

#### `Views/Product/Import.cshtml`
```html
{product_import_view}
```

#### `Views/Employee/Index.cshtml`
```html
{employee_index_view}
```

#### `Views/Store/Index.cshtml`
```html
{store_index_view}
```

#### `Views/Invoice/Create.cshtml`
```html
{invoice_create_view}
```

#### `Views/Invoice/History.cshtml`
```html
{invoice_history_view}
```

#### `Views/Dashboard/Index.cshtml`
```html
{dashboard_index_view}
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
"""

with open(md_path, "w", encoding="utf-8") as f:
    f.write(md_content)

print("PROJECT_DOCUMENTATION.md created successfully!")

# ============================================================================
# BUILD RICH INTERACTIVE HTML DOCUMENT
# ============================================================================
print("Building PROJECT_DOCUMENTATION.html with Interactive Workflow & Architecture Explorer...")

def esc(code_str):
    return html.escape(code_str)

# Pre-packaged Workflow Definitions in JSON for client-side rendering
workflows = {
    "invoice_checkout": {
        "title": "🛒 Invoice Creation & Atomic Stock Deduction (POS Checkout)",
        "badge": "CRITICAL TRANSACTION PIPELINE",
        "description": "Complete flow from Cashier adding items to cart, locking stock with FOR UPDATE, generating invoice, and deducting inventory atomically.",
        "steps": [
            {
                "num": 1,
                "layer": "Presentation / Client UI",
                "file": "ShopManagement.Web/wwwroot/js/invoice-create.js",
                "title": "Cashier adds products & clicks 'Complete Sale'",
                "explanation_en": "The user builds the cart in the browser. When clicking 'Complete Sale', JavaScript validates customer name and non-empty cart, serializes items into a JSON string, and sends an AJAX POST request.",
                "explanation_hi": "Cashier products add karta hai cart mein. Jab 'Complete Sale' dabata hai, JavaScript validation karta hai (Customer Name required, cart empty nahi honi chahiye) aur pura cart JSON string mein pack karke AJAX POST request bhejta hai.",
                "payload": "customerName=Rajesh Kumar&customerPhone=9876543210&itemsJson=[{\"productId\":1,\"productName\":\"Parker Pen\",\"quantity\":2,\"unitPrice\":150.00}]",
                "code": """$("#saveInvoiceBtn").on("click", function () {
    var custName  = $("#customerName").val().trim();
    var custPhone = $("#customerPhone").val().trim();

    if (!custName) {
        Swal.fire({ icon: 'warning', title: 'Customer Name Required', text: 'Please enter customer name.' });
        return;
    }
    if (cart.length === 0) {
        Swal.fire({ icon: 'warning', title: 'Cart Empty', text: 'Please add at least one product.' });
        return;
    }

    var postData = {
        customerName:  custName,
        customerPhone: custPhone,
        itemsJson:     JSON.stringify(cart)
    };

    $.post("/Invoice/Create", postData, function (res) {
        if (res.success) {
            Swal.fire({ icon: 'success', title: 'Invoice Generated', text: res.message });
            loadInvoicePreview(res.invoiceNo);
        } else {
            Swal.fire({ icon: 'error', title: 'Checkout Failed', text: res.message });
        }
    });
});"""
            },
            {
                "num": 2,
                "layer": "Network & HTTP Route",
                "file": "HTTP Protocol / Kestrel Server",
                "title": "HTTP POST /Invoice/Create",
                "explanation_en": "The request is transmitted over HTTP POST with form URL-encoded payload. ASP.NET Core routing identifies the action and passes request to InvoiceController.",
                "explanation_hi": "Yeh HTTP POST request server ko bhejti hai. Kestrel server routing match karke InvoiceController ke Create(customerName, customerPhone, itemsJson) method ko request handover karta hai.",
                "payload": "POST /Invoice/Create HTTP/1.1\nHost: localhost:5200\nContent-Type: application/x-www-form-urlencoded\nCookie: .AspNetCore.Session=...",
                "code": """POST /Invoice/Create HTTP/1.1
Host: localhost:5200
Content-Type: application/x-www-form-urlencoded
X-Requested-With: XMLHttpRequest

customerName=Rajesh+Kumar&customerPhone=9876543210&itemsJson=%5B%7B%22productId%22%3A1...%7D%5D"""
            },
            {
                "num": 3,
                "layer": "Presentation Controller",
                "file": "ShopManagement.Web/Controllers/InvoiceController.cs",
                "title": "InvoiceController.Create Action Execution",
                "explanation_en": "Validates active cashier session. Parses itemsJson using JArray into an in-memory DataTable with columns [ProductId, ProductName, Quantity, UnitPrice]. Reads cashier UserId from Session and calls InvoiceBAL.CreateInvoice().",
                "explanation_hi": "Controller pehle cashier ka session check karta hai. Uske baad JArray se JSON ko parse karta hai aur ek structured DataTable ('InvoiceItems') banata hai. Fir session se cashier ki UserId lekar InvoiceBAL.CreateInvoice() ko pass karta hai.",
                "payload": "DataTable: InvoiceItems [ProductId: 1, ProductName: 'Parker Pen', Quantity: 2, UnitPrice: 150.00]",
                "code": """[HttpPost]
public IActionResult Create(string customerName, string customerPhone, string itemsJson)
{
    if (!IsLoggedIn()) return Json(new { success = false, message = "Session expired." });

    var jArray = JArray.Parse(itemsJson);
    var itemsDt = new DataTable("InvoiceItems");
    itemsDt.Columns.Add("ProductId", typeof(int));
    itemsDt.Columns.Add("ProductName", typeof(string));
    itemsDt.Columns.Add("Quantity", typeof(int));
    itemsDt.Columns.Add("UnitPrice", typeof(decimal));

    foreach (var item in jArray)
    {
        itemsDt.Rows.Add(item["productId"].Value<int>(), item["productName"].Value<string>(), 
                         item["quantity"].Value<int>(), item["unitPrice"].Value<decimal>());
    }

    int createdBy = HttpContext.Session.GetInt32("UserId") ?? 1;
    bool success = _invoiceBAL.CreateInvoice(customerName, customerPhone, createdBy, itemsDt, out string invoiceNo, out string error);

    return Json(new { success, invoiceNo, message = success ? $"Invoice {invoiceNo} created!" : error });
}"""
            },
            {
                "num": 4,
                "layer": "Business Access Layer (BAL)",
                "file": "ShopManagement.Business/InvoiceBAL.cs",
                "title": "InvoiceBAL Business Logic Validation",
                "explanation_en": "Enforces business constraints: customer name cannot be whitespace, item table cannot be empty, and strings are trimmed. Forwards the sanitized data to InvoiceDAL.",
                "explanation_hi": "Business Layer rules check karta hai: Customer name empty toh nahi hai? Table mein atleast 1 item hai? Trim karke sanitized data ko Data Access Layer (InvoiceDAL) ko bhej deta hai.",
                "payload": "Input: customerName.Trim(), customerPhone?.Trim(), createdBy, itemsDt",
                "code": """public bool CreateInvoice(string customerName, string customerPhone, int createdBy, DataTable items, out string invoiceNo, out string errorMessage)
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
}"""
            },
            {
                "num": 5,
                "layer": "Data Access Layer (DAL)",
                "file": "ShopManagement.DataAccess/InvoiceDAL.cs",
                "title": "InvoiceDAL Transaction & 4 Stored Procedures Orchestration",
                "explanation_en": "Opens dedicated MySQL connection and starts a Transaction. Loops through items and calls sp_CheckProductStock with FOR UPDATE lock. If stock is valid, calls sp_InsertInvoiceHeader to get NewInvoiceId, then loops through items calling sp_InsertInvoiceDetail and sp_DeductProductStock. Commits transaction.",
                "explanation_hi": "DAL ek single connection open karta hai aur MySqlTransaction shuru karta hai. Step 1: sp_CheckProductStock call karke FOR UPDATE lock lagata hai taki stock safe rahe. Step 2: sp_InsertInvoiceHeader se Invoice banti hai aur NewInvoiceId milti hai. Step 3: sp_InsertInvoiceDetail aur sp_DeductProductStock se stock deduct hota hai. Sab sahi raha toh Commit(), warna Rollback().",
                "payload": "Transaction: conn.BeginTransaction() -> 4 SP Calls -> trans.Commit()",
                "code": """using (var conn = DbHelper.GetConnection())
using (var trans = conn.BeginTransaction())
{
    try
    {
        // ── Step 1: Validate stock with FOR UPDATE lock ──
        foreach (DataRow row in items.Rows)
        {
            using (var cmd = new MySqlCommand("sp_CheckProductStock", conn, trans))
            {
                cmd.CommandType = CommandType.StoredProcedure;
                cmd.Parameters.AddWithValue("p_ProductId", row["ProductId"]);
                using (var reader = cmd.ExecuteReader())
                {
                    reader.Read();
                    int stockOnHand = Convert.ToInt32(reader["Quantity"]);
                    reader.Close();
                    if (stockOnHand < Convert.ToInt32(row["Quantity"])) {
                        trans.Rollback();
                        return false;
                    }
                }
            }
        }

        // ── Step 2: Insert Header ──
        using (var cmd = new MySqlCommand("sp_InsertInvoiceHeader", conn, trans))
        {
            cmd.CommandType = CommandType.StoredProcedure;
            // ... parameters ...
            invoiceId = Convert.ToInt32(cmd.ExecuteScalar());
        }

        // ── Step 3: Insert Details & Deduct Stock ──
        foreach (DataRow row in items.Rows)
        {
            // sp_InsertInvoiceDetail ...
            // sp_DeductProductStock ...
        }

        trans.Commit();
        return true;
    }
    catch { trans.Rollback(); throw; }
}"""
            },
            {
                "num": 6,
                "layer": "Database Layer (MySQL)",
                "file": "ShopManagementDB (MySQL 8.0 Server)",
                "title": "MySQL Stored Procedures & Atomic State Persistence",
                "explanation_en": "Executes sp_CheckProductStock (InnoDB row lock), sp_InsertInvoiceHeader (inserts Invoices table), sp_InsertInvoiceDetail (inserts InvoiceDetails table), and sp_DeductProductStock (updates Products table quantity). Changes are written to the database transaction log.",
                "explanation_hi": "MySQL engine mein 4 procedures execute hote hain: Products table par exclusive row-level lock lagta hai, Invoices table mein header row banti hai, InvoiceDetails mein items save hote hain, aur Products ka Quantity column decrement ho jata hai. Poora transaction ACID compliant hai!",
                "payload": "MySQL Server: InnoDB Engine, Tables touched: Products, Invoices, InvoiceDetails",
                "code": """-- 1. Check stock with row lock
CREATE PROCEDURE sp_CheckProductStock(IN p_ProductId INT)
BEGIN
    SELECT ProductId, ProductName, Quantity FROM Products WHERE ProductId = p_ProductId AND IsActive = 1 FOR UPDATE;
END;

-- 2. Insert Invoice Header
CREATE PROCEDURE sp_InsertInvoiceHeader(...)
BEGIN
    INSERT INTO Invoices (InvoiceNo, CustomerName, CustomerPhone, CreatedBy, InvoiceDate, TotalAmount)
    VALUES (p_InvoiceNo, p_CustomerName, p_CustomerPhone, p_CreatedBy, NOW(), p_TotalAmount);
    SELECT LAST_INSERT_ID() AS NewInvoiceId;
END;

-- 3. Atomic stock deduction
CREATE PROCEDURE sp_DeductProductStock(IN p_ProductId INT, IN p_Quantity INT)
BEGIN
    UPDATE Products SET Quantity = Quantity - p_Quantity, UpdatedDate = NOW() WHERE ProductId = p_ProductId;
END;"""
            }
        ]
    },
    "employee_management": {
        "title": "👥 Staff / Cashier Onboarding & Store Assignment",
        "badge": "ROLE-PROTECTED CRUD FLOW",
        "description": "Admin creates new cashier desk credentials, assigns store branch, and loads the active staff roster into Kendo UI Grid.",
        "steps": [
            {
                "num": 1,
                "layer": "Presentation / Client UI",
                "file": "ShopManagement.Web/wwwroot/js/employee.js",
                "title": "Admin submits employee creation modal form",
                "explanation_en": "Admin fills name, username, password, and selects Store branch. The submit event is intercepted and serialized into form data sent via AJAX POST.",
                "explanation_hi": "Admin Employee modal form bharta hai aur Save dabata hai. employee.js submit event ko intercept karke $.post('/Employee/Add', ...) bhejta hai.",
                "payload": "name=Amit Patel&username=cashier2&password=pass123&storeId=1",
                "code": """$("#addEmployeeForm").on("submit", function (e) {
    e.preventDefault();
    $.post("/Employee/Add", $(this).serialize(), function (res) {
        if (res.success) {
            Swal.fire({ icon: 'success', title: 'Created', text: res.message, timer: 1500 });
            addModal.hide();
            $("#employeesGrid").data("kendoGrid").dataSource.read();
        } else {
            Swal.fire({ icon: 'error', title: 'Error', text: res.message });
        }
    });
});"""
            },
            {
                "num": 2,
                "layer": "Network & HTTP Route",
                "file": "HTTP Protocol",
                "title": "HTTP POST /Employee/Add",
                "explanation_en": "Sends serialized form data with session cookie to verify admin privileges.",
                "explanation_hi": "Browser se HTTP POST request /Employee/Add par jati hai session cookie ke saath.",
                "payload": "POST /Employee/Add HTTP/1.1\nContent-Type: application/x-www-form-urlencoded",
                "code": """POST /Employee/Add HTTP/1.1
Host: localhost:5200
Content-Type: application/x-www-form-urlencoded

name=Amit+Patel&username=cashier2&password=pass123&storeId=1"""
            },
            {
                "num": 3,
                "layer": "Presentation Controller",
                "file": "ShopManagement.Web/Controllers/EmployeeController.cs",
                "title": "EmployeeController.Add Action & Role Guard",
                "explanation_en": "Verifies session role is 'Admin'. Validates non-empty credentials and invokes EmployeeBAL.CreateEmployee().",
                "explanation_hi": "Controller pehle IsAdmin() se verify karta hai ki logged in user Admin hai. Fir EmployeeBAL.CreateEmployee() call karta hai.",
                "payload": "Parameters: (string name, string username, string password, int? storeId)",
                "code": """[HttpPost]
public IActionResult Add(string name, string username, string password, int? storeId)
{
    if (!IsAdmin()) return Json(new { success = false, message = "Unauthorized" });

    bool success = _employeeBAL.CreateEmployee(name, username, password, storeId, out string msg);
    return Json(new { success, message = msg });
}"""
            },
            {
                "num": 4,
                "layer": "Business Access Layer (BAL)",
                "file": "ShopManagement.Business/EmployeeBAL.cs",
                "title": "EmployeeBAL Business Rules",
                "explanation_en": "Validates password minimum length (>= 4 characters) and username requirements before calling EmployeeDAL.",
                "explanation_hi": "EmployeeBAL check karta hai password length 4 se zyada ho aur required fields null na ho. Uske baad EmployeeDAL ko call karta hai.",
                "payload": "name.Trim(), username.Trim(), password, storeId",
                "code": """public bool CreateEmployee(string name, string username, string password, int? storeId, out string message)
{
    if (string.IsNullOrWhiteSpace(name) || string.IsNullOrWhiteSpace(username) || string.IsNullOrWhiteSpace(password))
    {
        message = "Name, Username and Password are required.";
        return false;
    }
    if (password.Length < 4)
    {
        message = "Password must be at least 4 characters long.";
        return false;
    }
    return _dal.CreateEmployee(name.Trim(), username.Trim(), password, storeId);
}"""
            },
            {
                "num": 5,
                "layer": "Data Access Layer (DAL)",
                "file": "ShopManagement.DataAccess/EmployeeDAL.cs",
                "title": "EmployeeDAL Stored Procedure Call",
                "explanation_en": "Binds MySqlParameter array and executes stored procedure 'sp_CreateEmployee' via DbHelper.",
                "explanation_hi": "Parameters create karta hai aur DbHelper.ExecuteNonQuery('sp_CreateEmployee', ...) execute karta hai.",
                "payload": "MySqlParameters: @p_Name, @p_Username, @p_Password, @p_StoreId",
                "code": """public bool CreateEmployee(string name, string username, string password, int? storeId)
{
    var parameters = new[]
    {
        new MySqlParameter("@p_Name",     name),
        new MySqlParameter("@p_Username", username),
        new MySqlParameter("@p_Password", password),
        new MySqlParameter("@p_StoreId",  storeId.HasValue ? (object)storeId.Value : DBNull.Value)
    };
    return DbHelper.ExecuteNonQuery("sp_CreateEmployee", parameters, CommandType.StoredProcedure) > 0;
}"""
            },
            {
                "num": 6,
                "layer": "Database Layer (MySQL)",
                "file": "ShopManagementDB -> Users Table",
                "title": "MySQL sp_CreateEmployee Execution",
                "explanation_en": "Inserts a new record into Users table with Role='Employee', StoreId, IsActive=1, and CreatedDate=NOW().",
                "explanation_hi": "MySQL sp_CreateEmployee procedure run karta hai aur Users table mein record insert ho jata hai.",
                "payload": "INSERT INTO Users (Name, Username, PasswordHash, Role, StoreId, IsActive, CreatedDate) ...",
                "code": """CREATE PROCEDURE sp_CreateEmployee(
    IN p_Name VARCHAR(100),
    IN p_Username VARCHAR(100),
    IN p_Password VARCHAR(255),
    IN p_StoreId INT
)
BEGIN
    INSERT INTO Users (Name, Username, PasswordHash, Role, StoreId, IsActive, CreatedDate)
    VALUES (p_Name, p_Username, p_Password, 'Employee', p_StoreId, 1, NOW());
END;"""
            }
        ]
    },
    "product_upsert": {
        "title": "📦 Product Upsert with Image & Automatic Stock Increment",
        "badge": "SMART INVENTORY UPSERT",
        "description": "Adding a product that already exists increments current stock automatically; adding a new product creates it with image upload.",
        "steps": [
            {
                "num": 1,
                "layer": "Presentation / Client UI",
                "file": "ShopManagement.Web/wwwroot/js/product.js",
                "title": "Admin submits Product Upsert form with FormData",
                "explanation_en": "Constructs FormData object with ProductCode, ProductName, Quantity, Price, and optional Image file. Sends via AJAX POST.",
                "explanation_hi": "Product modal submit hone par product.js FormData banata hai (image file support ke saath) aur $.ajax se POST karta hai.",
                "payload": "FormData: productCode=P001, productName=Parker Pen, quantity=50, price=150, imageFile=...",
                "code": """$("#upsertProductForm").on("submit", function (e) {
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
                Swal.fire({ icon: 'success', title: 'Saved', text: res.message });
                upsertModal.hide();
                $("#productsGrid").data("kendoGrid").dataSource.read();
            }
        }
    });
});"""
            },
            {
                "num": 2,
                "layer": "Network & HTTP Route",
                "file": "HTTP Protocol",
                "title": "HTTP POST /Product/Add (multipart/form-data)",
                "explanation_en": "Transmits binary multipart data for product details and image file.",
                "explanation_hi": "Browser multipart/form-data POST request bhejta hai server ko.",
                "payload": "POST /Product/Add HTTP/1.1\nContent-Type: multipart/form-data; boundary=...",
                "code": """POST /Product/Add HTTP/1.1
Host: localhost:5200
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary..."""
            },
            {
                "num": 3,
                "layer": "Presentation Controller",
                "file": "ShopManagement.Web/Controllers/ProductController.cs",
                "title": "ProductController.Add & File Storage",
                "explanation_en": "Saves uploaded image to wwwroot/images/products/, then calls ProductBAL.UpsertProduct().",
                "explanation_hi": "Controller image ko disk pe save karta hai aur imagePath banakar ProductBAL.UpsertProduct() ko call karta hai.",
                "payload": "productCode, productName, quantity, price, imagePath",
                "code": """[HttpPost]
public IActionResult Add(string productCode, string productName, int quantity, decimal price, IFormFile? imageFile)
{
    if (!IsAdmin()) return Json(new { success = false, message = "Unauthorized" });

    string? imagePath = null;
    if (imageFile != null && imageFile.Length > 0)
    {
        var fileName = Guid.NewGuid().ToString() + Path.GetExtension(imageFile.FileName);
        var fullPath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "images", "products", fileName);
        using (var stream = new FileStream(fullPath, FileMode.Create)) { imageFile.CopyTo(stream); }
        imagePath = "/images/products/" + fileName;
    }

    bool success = _productBAL.UpsertProduct(productCode, productName, quantity, price, imagePath, out string operation);
    return Json(new { success, message = operation });
}"""
            },
            {
                "num": 4,
                "layer": "Business Access Layer (BAL)",
                "file": "ShopManagement.Business/ProductBAL.cs",
                "title": "ProductBAL Validation & Upsert Rule",
                "explanation_en": "Ensures quantity >= 0 and price >= 0, trims codes and names, then invokes ProductDAL.UpsertProduct.",
                "explanation_hi": "Validations check hoti hain: quantity aur price non-negative hone chahiye, strings sanitized hoti hain.",
                "payload": "productCode.Trim(), productName.Trim(), quantity, price, imagePath",
                "code": """public bool UpsertProduct(string productCode, string productName, int quantity, decimal price, string imagePath, out string operation)
{
    if (string.IsNullOrWhiteSpace(productCode) || string.IsNullOrWhiteSpace(productName))
    {
        operation = "Product code and name are required.";
        return false;
    }
    if (quantity < 0) quantity = 0;
    if (price < 0) price = 0;

    return _dal.UpsertProduct(productCode.Trim(), productName.Trim(), quantity, price, imagePath, out operation);
}"""
            },
            {
                "num": 5,
                "layer": "Data Access Layer (DAL)",
                "file": "ShopManagement.DataAccess/ProductDAL.cs",
                "title": "ProductDAL Stored Procedure Selection (Exists vs New)",
                "explanation_en": "Calls sp_CheckProductExists. If found, adds new quantity to existing stock and calls sp_UpdateProduct. If not found, calls sp_CreateProduct.",
                "explanation_hi": "DAL pehle sp_CheckProductExists run karta hai. Agar product pehle se exist karta hai, toh naya stock purane stock mein add hoke sp_UpdateProduct call hota hai! Agar naya product hai, toh sp_CreateProduct run hota hai.",
                "payload": "sp_CheckProductExists -> sp_UpdateProduct OR sp_CreateProduct",
                "code": """public bool UpsertProduct(string productCode, string productName, int quantity, decimal price, string imagePath, out string operation)
{
    var dtExisting = CheckProductExists(productCode, productName);

    if (dtExisting != null && dtExisting.Rows.Count > 0)
    {
        int existingId = Convert.ToInt32(dtExisting.Rows[0]["ProductId"]);
        int currentQty = Convert.ToInt32(dtExisting.Rows[0]["Quantity"]);
        // Increments stock
        var updateParams = new[] {
            new MySqlParameter("@p_ProductId", existingId),
            new MySqlParameter("@p_Quantity", currentQty + quantity),
            // ...
        };
        DbHelper.ExecuteNonQuery("sp_UpdateProduct", updateParams, CommandType.StoredProcedure);
        operation = "Updated (Stock Incremented)";
        return true;
    }
    else
    {
        // Creates new product
        var insertParams = new[] { ... };
        DbHelper.ExecuteNonQuery("sp_CreateProduct", insertParams, CommandType.StoredProcedure);
        operation = "Created New Product";
        return true;
    }
}"""
            },
            {
                "num": 6,
                "layer": "Database Layer (MySQL)",
                "file": "ShopManagementDB -> Products Table",
                "title": "MySQL sp_UpdateProduct / sp_CreateProduct Execution",
                "explanation_en": "Persists new product or increments stock on Products table.",
                "explanation_hi": "MySQL stored procedure update ya insert query execute karke product inventory ko safely synchronize karta hai.",
                "payload": "Products Table row updated / inserted",
                "code": """CREATE PROCEDURE sp_CheckProductExists(IN p_ProductCode VARCHAR(50), IN p_ProductName VARCHAR(200))
BEGIN
    SELECT ProductId, ProductCode, ProductName, Quantity, Price, ImagePath 
    FROM Products 
    WHERE ProductCode = p_ProductCode OR LOWER(ProductName) = LOWER(p_ProductName) LIMIT 1;
END;

CREATE PROCEDURE sp_CreateProduct(IN p_ProductCode VARCHAR(50), IN p_ProductName VARCHAR(200), IN p_Quantity INT, IN p_Price DECIMAL(18,2), IN p_ImagePath VARCHAR(500))
BEGIN
    INSERT INTO Products (ProductCode, ProductName, Quantity, Price, ImagePath, IsActive, CreatedDate)
    VALUES (p_ProductCode, p_ProductName, p_Quantity, p_Price, p_ImagePath, 1, NOW());
END;"""
            }
        ]
    }
}

workflows_json = json.dumps(workflows)

html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shop Management System — Enterprise Technical Documentation & Interactive Workflow Guide</title>
    <!-- Fonts & Icons -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <!-- Highlight.js -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
    <style>
        :root {{
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --primary-light: #eff6ff;
            --accent: #06b6d4;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --dark: #0f172a;
            --slate: #1e293b;
            --border: #e2e8f0;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --code-bg: #0d1117;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg);
            color: #334155;
            line-height: 1.6;
            font-size: 15px;
        }}

        /* Header Banner */
        .doc-header {{
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
            color: #ffffff;
            padding: 40px 30px;
            border-bottom: 2px solid #334155;
            position: relative;
            overflow: hidden;
        }}
        .doc-header::after {{
            content: '';
            position: absolute;
            top: -50%;
            right: -10%;
            width: 500px;
            height: 500px;
            background: radial-gradient(circle, rgba(37,99,235,0.2) 0%, transparent 70%);
            pointer-events: none;
        }}
        .header-content {{
            max-width: 1300px;
            margin: 0 auto;
            position: relative;
            z-index: 2;
        }}
        .header-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(37, 99, 235, 0.3);
            border: 1px solid rgba(59, 130, 246, 0.4);
            color: #93c5fd;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            margin-bottom: 12px;
        }}
        .doc-header h1 {{
            font-size: 28pt;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: -0.5px;
            margin-bottom: 10px;
        }}
        .doc-header p {{
            font-size: 13pt;
            color: #94a3b8;
            max-width: 900px;
            margin-bottom: 20px;
        }}
        .meta-badges {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .meta-badge {{
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.15);
            padding: 5px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            color: #e2e8f0;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}

        /* Main Container Layout */
        .main-container {{
            max-width: 1350px;
            margin: 30px auto;
            padding: 0 20px;
            display: grid;
            grid-template-columns: 280px 1fr;
            gap: 30px;
        }}

        @media (max-width: 1024px) {{
            .main-container {{
                grid-template-columns: 1fr;
            }}
            .sidebar {{
                display: none;
            }}
        }}

        /* Sidebar Navigation */
        .sidebar {{
            position: sticky;
            top: 20px;
            height: calc(100vh - 40px);
            overflow-y: auto;
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        }}
        .sidebar h4 {{
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: #94a3b8;
            margin-bottom: 14px;
            font-weight: 700;
        }}
        .sidebar ul {{
            list-style: none;
        }}
        .sidebar li {{
            margin-bottom: 8px;
        }}
        .sidebar a {{
            color: #475569;
            text-decoration: none;
            font-size: 13.5px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 10px;
            border-radius: 6px;
            transition: all 0.2s;
        }}
        .sidebar a:hover {{
            background: var(--primary-light);
            color: var(--primary);
        }}

        /* Content Area */
        .content {{
            min-width: 0;
        }}

        /* Quick Search & Filter */
        .search-box-wrap {{
            margin-bottom: 25px;
            position: relative;
        }}
        .search-input {{
            width: 100%;
            padding: 14px 20px 14px 45px;
            border: 2px solid var(--border);
            border-radius: 10px;
            font-size: 15px;
            font-family: inherit;
            background: #ffffff;
            transition: all 0.2s;
        }}
        .search-input:focus {{
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.15);
        }}
        .search-icon {{
            position: absolute;
            left: 16px;
            top: 50%;
            transform: translateY(-50%);
            color: #94a3b8;
            font-size: 16px;
        }}

        /* Interactive Workflow Explorer Component */
        .workflow-card {{
            background: #ffffff;
            border: 2px solid #3b82f6;
            border-radius: 16px;
            padding: 28px;
            margin-bottom: 35px;
            box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.12);
        }}
        .workflow-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            flex-wrap: wrap;
            gap: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 24px;
        }}
        .workflow-title-wrap h3 {{
            font-size: 20px;
            font-weight: 800;
            color: var(--dark);
            margin-bottom: 6px;
        }}
        .workflow-title-wrap p {{
            font-size: 13.5px;
            color: #64748b;
        }}
        .workflow-select-wrap {{
            min-width: 320px;
        }}
        .workflow-select-wrap label {{
            display: block;
            font-size: 12px;
            font-weight: 700;
            color: #475569;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
        }}
        .form-select {{
            width: 100%;
            padding: 11px 16px;
            border: 2px solid var(--primary);
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            color: var(--dark);
            background: #ffffff;
            cursor: pointer;
            outline: none;
        }}

        /* Pipeline Stepper / Breadcrumb */
        .pipeline-stepper {{
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 10px;
            margin-bottom: 25px;
        }}
        @media (max-width: 768px) {{
            .pipeline-stepper {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
        .pipe-node {{
            background: #f1f5f9;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            padding: 12px 10px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
            position: relative;
        }}
        .pipe-node:hover {{
            border-color: var(--primary);
            background: var(--primary-light);
        }}
        .pipe-node.active {{
            background: #eff6ff;
            border-color: var(--primary);
            box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2);
        }}
        .pipe-node .node-num {{
            display: inline-block;
            width: 22px;
            height: 22px;
            line-height: 22px;
            border-radius: 50%;
            background: #cbd5e1;
            color: #1e293b;
            font-size: 11px;
            font-weight: 800;
            margin-bottom: 4px;
        }}
        .pipe-node.active .node-num {{
            background: var(--primary);
            color: #ffffff;
        }}
        .pipe-node .node-label {{
            font-size: 11px;
            font-weight: 700;
            color: #475569;
            display: block;
        }}
        .pipe-node.active .node-label {{
            color: var(--primary);
        }}

        /* Inspector Card */
        .inspector-panel {{
            background: #f8fafc;
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px;
        }}
        .inspector-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .step-badge {{
            background: var(--primary);
            color: #ffffff;
            font-size: 11px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 4px;
            text-transform: uppercase;
        }}
        .step-file-badge {{
            background: #e2e8f0;
            color: #334155;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            padding: 4px 10px;
            border-radius: 4px;
        }}
        .inspector-title {{
            font-size: 17px;
            font-weight: 700;
            color: var(--dark);
            margin-bottom: 12px;
        }}
        .exp-box {{
            background: #ffffff;
            border-left: 4px solid var(--primary);
            padding: 14px 18px;
            border-radius: 0 8px 8px 0;
            margin-bottom: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .exp-box p {{
            margin-bottom: 6px;
            font-size: 14px;
        }}
        .exp-box .hi-text {{
            color: #0369a1;
            font-weight: 500;
        }}
        .payload-box {{
            background: #1e293b;
            color: #e2e8f0;
            padding: 10px 14px;
            border-radius: 6px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            margin-bottom: 16px;
            overflow-x: auto;
        }}
        .code-preview-wrap {{
            margin-top: 10px;
        }}
        .code-preview-wrap pre {{
            margin: 0;
            border-radius: 8px;
            max-height: 400px;
            overflow-y: auto;
        }}

        /* General Section Styling */
        section {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }}
        h2 {{
            font-size: 20pt;
            font-weight: 800;
            color: var(--dark);
            margin-bottom: 16px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--border);
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        h3 {{
            font-size: 15pt;
            font-weight: 700;
            color: var(--slate);
            margin-top: 24px;
            margin-bottom: 12px;
        }}
        h4 {{
            font-size: 12pt;
            font-weight: 700;
            color: #334155;
            margin-top: 18px;
            margin-bottom: 8px;
        }}
        p {{
            margin-bottom: 12px;
            color: #475569;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 18px 0;
            font-size: 13.5px;
        }}
        th, td {{
            padding: 10px 14px;
            border: 1px solid var(--border);
            text-align: left;
        }}
        th {{
            background: #f1f5f9;
            font-weight: 700;
            color: #1e293b;
        }}
        tr:nth-child(even) {{
            background: #f8fafc;
        }}
        pre {{
            background: var(--code-bg);
            border-radius: 8px;
            padding: 16px;
            overflow-x: auto;
            margin: 14px 0 20px 0;
        }}
        code {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
        }}
        p code, td code, li code {{
            background: #f1f5f9;
            color: #0f172a;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 12.5px;
            border: 1px solid #e2e8f0;
        }}
        pre code {{
            background: transparent !important;
            padding: 0 !important;
            border: none !important;
        }}
        .copy-btn {{
            float: right;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #cbd5e1;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .copy-btn:hover {{
            background: rgba(255, 255, 255, 0.2);
            color: #ffffff;
        }}
    </style>
</head>
<body>

<!-- Header Banner -->
<header class="doc-header">
    <div class="header-content">
        <span class="header-badge"><i class="fa-solid fa-code-commit"></i> Enterprise 3-Tier Architecture</span>
        <h1>Shop Management System</h1>
        <p>Complete Architecture, Active Source Code, 100% Stored Procedure Database Setup, and Deep Interactive Data Flow Guide.</p>
        <div class="meta-badges">
            <span class="meta-badge"><i class="fa-brands fa-microsoft"></i> ASP.NET Core MVC (.NET 10)</span>
            <span class="meta-badge"><i class="fa-solid fa-database"></i> MySQL 8.0 (19 Stored Procedures)</span>
            <span class="meta-badge"><i class="fa-solid fa-layer-group"></i> 3-Tier (DAL + BAL + Web)</span>
            <span class="meta-badge"><i class="fa-solid fa-file-excel"></i> ClosedXML Bulk Stream</span>
            <span class="meta-badge"><i class="fa-solid fa-bolt"></i> Pessimistic Locking (FOR UPDATE)</span>
            <span class="meta-badge"><i class="fa-solid fa-code"></i> Clean wwwroot/js/ Separation</span>
        </div>
    </div>
</header>

<div class="main-container">
    <!-- Sidebar Navigation -->
    <aside class="sidebar">
        <h4><i class="fa-solid fa-bars"></i> Documentation Index</h4>
        <ul>
            <li><a href="#interactive-workflow"><i class="fa-solid fa-diagram-project text-primary"></i> 1. Live Workflow Explorer</a></li>
            <li><a href="#database-setup"><i class="fa-solid fa-database text-warning"></i> 2. Master SQL & All 19 SPs</a></li>
            <li><a href="#layer-dal"><i class="fa-solid fa-cubes text-info"></i> 3. Data Access Layer (DAL)</a></li>
            <li><a href="#layer-bal"><i class="fa-solid fa-gears text-success"></i> 4. Business Access Layer (BAL)</a></li>
            <li><a href="#layer-controllers"><i class="fa-solid fa-gamepad text-danger"></i> 5. Web Controllers</a></li>
            <li><a href="#layer-js"><i class="fa-brands fa-js text-warning"></i> 6. Standalone Frontend JS</a></li>
            <li><a href="#layer-views"><i class="fa-solid fa-desktop text-primary"></i> 7. Razor Views</a></li>
            <li><a href="#architecture-decisions"><i class="fa-solid fa-brain text-info"></i> 8. Architectural Decisions</a></li>
            <li><a href="#setup-guide"><i class="fa-solid fa-play text-success"></i> 9. Build & Run Guide</a></li>
        </ul>
    </aside>

    <!-- Main Content Area -->
    <main class="content">

        <!-- Search Bar -->
        <div class="search-box-wrap">
            <i class="fa-solid fa-magnifying-glass search-icon"></i>
            <input type="text" id="docSearchInput" class="search-input" placeholder="Search methods, Stored Procedures (e.g. sp_CheckProductStock), classes, or files...">
        </div>

        <!-- 1. LIVE INTERACTIVE WORKFLOW EXPLORER -->
        <section id="interactive-workflow" class="workflow-card">
            <div class="workflow-header">
                <div class="workflow-title-wrap">
                    <span class="step-badge" style="background:#2563eb;"><i class="fa-solid fa-bolt"></i> Interactive Flow Inspector</span>
                    <h3 style="margin-top:6px;">Project Workflow & Deep Data Lifecycle Explorer</h3>
                    <p>Select any module below to inspect the step-by-step pipeline from Client UI to MySQL Stored Procedure and Table Commit.</p>
                </div>
                <div class="workflow-select-wrap">
                    <label for="flowSelector">Choose Feature Pipeline:</label>
                    <select id="flowSelector" class="form-select">
                        <option value="invoice_checkout">🛒 1. Invoice Checkout & Atomic Stock Deduction (POS)</option>
                        <option value="employee_management">👥 2. Staff / Cashier Onboarding & Store Assignment</option>
                        <option value="product_upsert">📦 3. Product Upsert with Auto-Stock Increment</option>
                    </select>
                </div>
            </div>

            <!-- Pipeline Stepper Nodes -->
            <div id="pipelineNodes" class="pipeline-stepper">
                <!-- Dynamically populated via JS -->
            </div>

            <!-- Detailed Step Inspector -->
            <div id="inspectorPanel" class="inspector-panel">
                <!-- Dynamically populated via JS -->
            </div>
        </section>

        <!-- 2. DATABASE DESIGN & MASTER SQL -->
        <section id="database-setup">
            <h2><i class="fa-solid fa-database text-warning"></i> 2. Master Database Setup (`ShopManagement_Full_Setup.sql`)</h2>
            <p>The entire database schema, relationship constraints, default administrator / branch seed records, and all <strong>19 production Stored Procedures</strong> are defined centrally in a single master script. Execute this script once in MySQL Workbench, CLI, or phpMyAdmin to initialize everything cleanly.</p>

            <div class="code-preview-wrap">
                <button class="copy-btn" onclick="copyCode(this)"><i class="fa-regular fa-copy"></i> Copy SQL</button>
                <pre><code class="language-sql">{esc(full_sql_code)}</code></pre>
            </div>
        </section>

        <!-- 3. DATA ACCESS LAYER -->
        <section id="layer-dal">
            <h2><i class="fa-solid fa-cubes text-info"></i> 3. Data Access Layer (ShopManagement.DataAccess)</h2>
            <p>Contains lightweight ADO.NET abstractions using <code>MySqlConnector</code>. All database interactions call compiled Stored Procedures with strongly typed parameters.</p>

            <h3>3.1 DbHelper.cs (Clean, High-Performance ADO.NET Helper)</h3>
            <p>Zero embedded Stored Procedure SQL strings. Clean execution overloads supporting transactions and Stored Procedures.</p>
            <pre><code class="language-csharp">{esc(db_helper_code)}</code></pre>

            <h3>3.2 InvoiceDAL.cs (ACID Billing Transaction & Pessimistic Lock)</h3>
            <p>Executes <code>sp_CheckProductStock</code> with <code>FOR UPDATE</code> lock, <code>sp_InsertInvoiceHeader</code>, <code>sp_InsertInvoiceDetail</code>, and <code>sp_DeductProductStock</code> within a shared C# database transaction.</p>
            <pre><code class="language-csharp">{esc(invoice_dal_code)}</code></pre>

            <h3>3.3 ProductDAL.cs</h3>
            <pre><code class="language-csharp">{esc(product_dal_code)}</code></pre>

            <h3>3.4 EmployeeDAL.cs</h3>
            <pre><code class="language-csharp">{esc(employee_dal_code)}</code></pre>

            <h3>3.5 StoreDAL.cs</h3>
            <pre><code class="language-csharp">{esc(store_dal_code)}</code></pre>

            <h3>3.6 AccountDAL.cs</h3>
            <pre><code class="language-csharp">{esc(account_dal_code)}</code></pre>
        </section>

        <!-- 4. BUSINESS ACCESS LAYER -->
        <section id="layer-bal">
            <h2><i class="fa-solid fa-gears text-success"></i> 4. Business Access Layer (ShopManagement.Business)</h2>
            <p>Validates data integrity, enforces security rules, handles upsert calculation logic, and streams ClosedXML Excel data.</p>

            <h3>4.1 InvoiceBAL.cs</h3>
            <pre><code class="language-csharp">{esc(invoice_bal_code)}</code></pre>

            <h3>4.2 ProductBAL.cs</h3>
            <pre><code class="language-csharp">{esc(product_bal_code)}</code></pre>

            <h3>4.3 EmployeeBAL.cs</h3>
            <pre><code class="language-csharp">{esc(employee_bal_code)}</code></pre>

            <h3>4.4 StoreBAL.cs</h3>
            <pre><code class="language-csharp">{esc(store_bal_code)}</code></pre>

            <h3>4.5 AccountBAL.cs</h3>
            <pre><code class="language-csharp">{esc(account_bal_code)}</code></pre>

            <h3>4.6 ExcelBAL.cs</h3>
            <pre><code class="language-csharp">{esc(excel_bal_code)}</code></pre>
        </section>

        <!-- 5. WEB CONTROLLERS -->
        <section id="layer-controllers">
            <h2><i class="fa-solid fa-gamepad text-danger"></i> 5. Presentation Layer Controllers (ShopManagement.Web)</h2>

            <h3>5.1 InvoiceController.cs</h3>
            <pre><code class="language-csharp">{esc(invoice_ctrl_code)}</code></pre>

            <h3>5.2 ProductController.cs</h3>
            <pre><code class="language-csharp">{esc(product_ctrl_code)}</code></pre>

            <h3>5.3 EmployeeController.cs</h3>
            <pre><code class="language-csharp">{esc(employee_ctrl_code)}</code></pre>

            <h3>5.4 StoreController.cs</h3>
            <pre><code class="language-csharp">{esc(store_ctrl_code)}</code></pre>

            <h3>5.5 DashboardController.cs</h3>
            <pre><code class="language-csharp">{esc(dashboard_ctrl_code)}</code></pre>

            <h3>5.6 AccountController.cs</h3>
            <pre><code class="language-csharp">{esc(account_ctrl_code)}</code></pre>
        </section>

        <!-- 6. STANDALONE FRONTEND JAVASCRIPT -->
        <section id="layer-js">
            <h2><i class="fa-brands fa-js text-warning"></i> 6. Standalone Frontend JavaScript (`wwwroot/js/`)</h2>
            <p>All page-specific JavaScript logic is decoupled into static modular files in <code>wwwroot/js/</code> for maximum performance and caching.</p>

            <h3>6.1 invoice-create.js (POS Billing & Cart Management)</h3>
            <pre><code class="language-javascript">{esc(invoice_create_js)}</code></pre>

            <h3>6.2 employee.js (Staff Grid & Modals)</h3>
            <pre><code class="language-javascript">{esc(employee_js)}</code></pre>

            <h3>6.3 product.js (Product Inventory Grid & Upsert)</h3>
            <pre><code class="language-javascript">{esc(product_js)}</code></pre>

            <h3>6.4 store.js (Store Branch Management)</h3>
            <pre><code class="language-javascript">{esc(store_js)}</code></pre>

            <h3>6.5 invoice-history.js (Invoice History & Printing)</h3>
            <pre><code class="language-javascript">{esc(invoice_history_js)}</code></pre>
        </section>

        <!-- 7. RAZOR VIEWS -->
        <section id="layer-views">
            <h2><i class="fa-solid fa-desktop text-primary"></i> 7. Razor Views & Script Integration</h2>

            <h3>7.1 Views/Invoice/Create.cshtml</h3>
            <pre><code class="language-html">{esc(invoice_create_view)}</code></pre>

            <h3>7.2 Views/Employee/Index.cshtml</h3>
            <pre><code class="language-html">{esc(employee_index_view)}</code></pre>

            <h3>7.3 Views/Product/Index.cshtml</h3>
            <pre><code class="language-html">{esc(product_index_view)}</code></pre>

            <h3>7.4 Views/Store/Index.cshtml</h3>
            <pre><code class="language-html">{esc(store_index_view)}</code></pre>

            <h3>7.5 Views/Dashboard/Index.cshtml</h3>
            <pre><code class="language-html">{esc(dashboard_index_view)}</code></pre>
        </section>

        <!-- 8. ARCHITECTURAL DECISIONS -->
        <section id="architecture-decisions">
            <h2><i class="fa-solid fa-brain text-info"></i> 8. Architectural Decisions & Concurrency Design</h2>
            <div class="exp-box">
                <h4>1. Why Stored Procedures Exclusively?</h4>
                <p>Centralized schema governance, pre-compiled execution plans in MySQL memory, and zero exposure to SQL injection vulnerabilities.</p>
            </div>
            <div class="exp-box">
                <h4>2. Why Pessimistic Locking (FOR UPDATE) in Invoicing?</h4>
                <p>Prevents negative inventory in busy retail environments when multiple cashiers sell the last units of an item simultaneously.</p>
            </div>
            <div class="exp-box">
                <h4>3. Why Modular JavaScript in wwwroot/js/?</h4>
                <p>Allows browser caching, complies with Content Security Policies (CSP), and keeps Razor views clean and focused on markup.</p>
            </div>
        </section>

        <!-- 9. BUILD & RUN GUIDE -->
        <section id="setup-guide">
            <h2><i class="fa-solid fa-play text-success"></i> 9. Step-by-Step Setup, Build & Run Guide</h2>
            <ol style="margin-left: 20px; line-height: 2;">
                <li><strong>Deploy Database:</strong> Open MySQL CLI or Workbench and run <code>ShopManagement_Full_Setup.sql</code>.</li>
                <li><strong>Verify Connection:</strong> Ensure <code>ShopManagement.Web/appsettings.json</code> has correct credentials.</li>
                <li><strong>Build Solution:</strong> Run <code>dotnet build ShopManagement.slnx -c Release</code>.</li>
                <li><strong>Start Web Application:</strong> Run <code>dotnet run --project ShopManagement.Web</code>.</li>
                <li><strong>Open Browser:</strong> Access <code>http://localhost:5200</code>.</li>
            </ol>
        </section>
    </main>
</div>

<!-- Scripts -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/csharp.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/sql.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/json.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/javascript.min.js"></script>

<script>
    const workflowsData = {workflows_json};
    let currentFlowKey = 'invoice_checkout';
    let currentStepIndex = 0;

    function renderPipeline() {{
        const flow = workflowsData[currentFlowKey];
        const nodesContainer = document.getElementById('pipelineNodes');
        nodesContainer.innerHTML = '';

        flow.steps.forEach((step, idx) => {{
            const node = document.createElement('div');
            node.className = 'pipe-node' + (idx === currentStepIndex ? ' active' : '');
            node.onclick = () => selectStep(idx);
            node.innerHTML = `
                <span class="node-num">${{step.num}}</span>
                <span class="node-label">${{step.layer.split('/')[0].trim()}}</span>
            `;
            nodesContainer.appendChild(node);
        }});

        renderInspector();
    }}

    function renderInspector() {{
        const flow = workflowsData[currentFlowKey];
        const step = flow.steps[currentStepIndex];
        const panel = document.getElementById('inspectorPanel');

        panel.innerHTML = `
            <div class="inspector-header">
                <div>
                    <span class="step-badge">Step ${{step.num}} of ${{flow.steps.length}}</span>
                    <span class="step-badge" style="background:#0891b2; margin-left:6px;">${{step.layer}}</span>
                </div>
                <span class="step-file-badge"><i class="fa-regular fa-file-code"></i> ${{step.file}}</span>
            </div>
            <div class="inspector-title">${{step.title}}</div>
            <div class="exp-box">
                <p><strong>English:</strong> ${{step.explanation_en}}</p>
                <p class="hi-text"><strong>Hinglish:</strong> ${{step.explanation_hi}}</p>
            </div>
            <div style="font-size:12px; font-weight:700; color:#475569; text-transform:uppercase; margin-bottom:4px;">
                <i class="fa-solid fa-arrows-split-up-and-left"></i> Data Payload / Signature:
            </div>
            <div class="payload-box">${{step.payload}}</div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:14px; margin-bottom:6px;">
                <span style="font-size:12px; font-weight:700; color:#475569; text-transform:uppercase;">
                    <i class="fa-solid fa-code"></i> Active Code Section:
                </span>
                <div>
                    <button class="copy-btn" style="color:#0f172a; border-color:#cbd5e1;" onclick="prevStep()" ${{currentStepIndex === 0 ? 'disabled' : ''}}>
                        <i class="fa-solid fa-arrow-left"></i> Prev
                    </button>
                    <button class="copy-btn" style="color:#0f172a; border-color:#cbd5e1; margin-left:6px;" onclick="nextStep()" ${{currentStepIndex === flow.steps.length - 1 ? 'disabled' : ''}}>
                        Next <i class="fa-solid fa-arrow-right"></i>
                    </button>
                </div>
            </div>
            <div class="code-preview-wrap">
                <pre><code class="language-csharp">${{step.code}}</code></pre>
            </div>
        `;

        panel.querySelectorAll('pre code').forEach((el) => {{
            hljs.highlightElement(el);
        }});
    }}

    function selectStep(idx) {{
        currentStepIndex = idx;
        renderPipeline();
    }}

    function prevStep() {{
        if (currentStepIndex > 0) {{
            currentStepIndex--;
            renderPipeline();
        }}
    }}

    function nextStep() {{
        const flow = workflowsData[currentFlowKey];
        if (currentStepIndex < flow.steps.length - 1) {{
            currentStepIndex++;
            renderPipeline();
        }}
    }}

    document.getElementById('flowSelector').addEventListener('change', function () {{
        currentFlowKey = this.value;
        currentStepIndex = 0;
        renderPipeline();
    }});

    function copyCode(btn) {{
        const code = btn.nextElementSibling.innerText;
        navigator.clipboard.writeText(code).then(() => {{
            btn.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
            setTimeout(() => {{ btn.innerHTML = '<i class="fa-regular fa-copy"></i> Copy'; }}, 2000);
        }});
    }}

    // Real-time documentation filter
    document.getElementById('docSearchInput').addEventListener('input', function() {{
        const term = this.value.toLowerCase().trim();
        const sections = document.querySelectorAll('main section');
        sections.forEach(sec => {{
            if (!term) {{
                sec.style.display = 'block';
            }} else {{
                const text = sec.innerText.toLowerCase();
                sec.style.display = text.includes(term) ? 'block' : 'none';
            }}
        }});
    }});

    document.addEventListener('DOMContentLoaded', () => {{
        renderPipeline();
        document.querySelectorAll('pre code').forEach((el) => {{
            hljs.highlightElement(el);
        }});
    }});
</script>
</body>
</html>
"""

html_path = os.path.join(workspace_root, "PROJECT_DOCUMENTATION.html")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"PROJECT_DOCUMENTATION.html written successfully! (Size: {os.path.getsize(html_path) / 1024:.1f} KB)")
