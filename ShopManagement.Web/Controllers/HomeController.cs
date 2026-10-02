using System.Diagnostics;
using Microsoft.AspNetCore.Mvc;
using ShopManagement.Web.Models;

namespace ShopManagement.Web.Controllers;

public class HomeController : Controller
{
    public IActionResult Index()
    {
        string? role = HttpContext.Session.GetString("Role");
        if (string.IsNullOrEmpty(role))
        {
            return RedirectToAction("Login", "Account");
        }
        return role.Equals("Admin", StringComparison.OrdinalIgnoreCase)
            ? RedirectToAction("Index", "Product")
            : RedirectToAction("Create", "Invoice");
    }

    public IActionResult Privacy()
    {
        return View();
    }

    [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
    public IActionResult Error()
    {
        return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
    }
}
