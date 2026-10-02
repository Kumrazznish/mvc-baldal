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
