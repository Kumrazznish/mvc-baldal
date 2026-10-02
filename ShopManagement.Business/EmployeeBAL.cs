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
