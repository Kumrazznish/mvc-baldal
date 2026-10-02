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
