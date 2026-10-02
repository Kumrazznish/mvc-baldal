using System;
using System.Data;
using MySqlConnector;

namespace ShopManagement.DataAccess
{
    public class EmployeeDAL
    {
        public DataTable GetAllEmployees()
        {
            return DbHelper.ExecuteDataTable("sp_GetAllEmployees", null, CommandType.StoredProcedure);
        }

        public DataTable GetEmployeeById(int userId)
        {
            var parameters = new[] { new MySqlParameter("@p_UserId", userId) };
            return DbHelper.ExecuteDataTable("sp_GetEmployeeById", parameters, CommandType.StoredProcedure);
        }

        public bool CreateEmployee(string name, string username, string password, int? storeId)
        {
            var parameters = new[]
            {
                new MySqlParameter("@p_Name",     name),
                new MySqlParameter("@p_Username", username),
                new MySqlParameter("@p_Password", password),
                new MySqlParameter("@p_StoreId",  storeId.HasValue ? (object)storeId.Value : DBNull.Value)
            };
            return DbHelper.ExecuteNonQuery("sp_CreateEmployee", parameters, CommandType.StoredProcedure) > 0;
        }

        public bool UpdateEmployee(int userId, string name, string password, bool isActive, int? storeId)
        {
            var parameters = new[]
            {
                new MySqlParameter("@p_UserId",   userId),
                new MySqlParameter("@p_Name",     name),
                new MySqlParameter("@p_Password", string.IsNullOrWhiteSpace(password) ? (object)DBNull.Value : password),
                new MySqlParameter("@p_IsActive", isActive ? 1 : 0),
                new MySqlParameter("@p_StoreId",  storeId.HasValue ? (object)storeId.Value : DBNull.Value)
            };
            return DbHelper.ExecuteNonQuery("sp_UpdateEmployee", parameters, CommandType.StoredProcedure) > 0;
        }

        public bool ResetPassword(int userId, string newPassword)
        {
            var parameters = new[]
            {
                new MySqlParameter("@p_UserId",   userId),
                new MySqlParameter("@p_Password", newPassword)
            };
            return DbHelper.ExecuteNonQuery("sp_ResetEmployeePassword", parameters, CommandType.StoredProcedure) > 0;
        }

        public bool ToggleStatus(int userId)
        {
            var parameters = new[] { new MySqlParameter("@p_UserId", userId) };
            return DbHelper.ExecuteNonQuery("sp_ToggleEmployeeStatus", parameters, CommandType.StoredProcedure) > 0;
        }

        public bool DeleteEmployee(int userId)
        {
            var parameters = new[] { new MySqlParameter("@p_UserId", userId) };
            return DbHelper.ExecuteNonQuery("sp_DeleteEmployee", parameters, CommandType.StoredProcedure) > 0;
        }
    }
}
