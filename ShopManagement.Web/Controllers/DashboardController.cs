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
