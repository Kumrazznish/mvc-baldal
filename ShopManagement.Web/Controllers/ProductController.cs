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
