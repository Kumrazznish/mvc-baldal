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
