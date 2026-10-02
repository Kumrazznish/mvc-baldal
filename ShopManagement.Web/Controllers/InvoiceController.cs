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
