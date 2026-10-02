using System;
using System.Data;
using MySqlConnector;

namespace ShopManagement.DataAccess
{
    public class StoreDAL
    {
        public DataTable GetAllStores(bool activeOnly = false)
        {
            var parameters = new[] { new MySqlParameter("@p_ActiveOnly", activeOnly) };
            return DbHelper.ExecuteDataTable("sp_GetAllStores", parameters, CommandType.StoredProcedure);
        }

        public DataTable GetStoreById(int storeId)
        {
            var parameters = new[] { new MySqlParameter("@p_StoreId", storeId) };
            return DbHelper.ExecuteDataTable("sp_GetStoreById", parameters, CommandType.StoredProcedure);
        }

        public bool CreateStore(string storeCode, string storeName, string address, string phone, string email, out string errorMessage)
        {
            errorMessage = string.Empty;
            try
            {
                var parameters = new[]
                {
                    new MySqlParameter("@p_StoreCode", storeCode),
                    new MySqlParameter("@p_StoreName", storeName),
                    new MySqlParameter("@p_Address",   string.IsNullOrWhiteSpace(address) ? (object)DBNull.Value : address),
                    new MySqlParameter("@p_Phone",     string.IsNullOrWhiteSpace(phone) ? (object)DBNull.Value : phone),
                    new MySqlParameter("@p_Email",     string.IsNullOrWhiteSpace(email) ? (object)DBNull.Value : email)
                };
                return DbHelper.ExecuteNonQuery("sp_CreateStore", parameters, CommandType.StoredProcedure) > 0;
            }
            catch (Exception ex)
            {
                errorMessage = ex.Message.Contains("Duplicate") ? "Store code already exists." : ex.Message;
                return false;
            }
        }

        public bool UpdateStore(int storeId, string storeName, string address, string phone, string email, bool isActive)
        {
            var parameters = new[]
            {
                new MySqlParameter("@p_StoreId",   storeId),
                new MySqlParameter("@p_StoreName", storeName),
                new MySqlParameter("@p_Address",   string.IsNullOrWhiteSpace(address) ? (object)DBNull.Value : address),
                new MySqlParameter("@p_Phone",     string.IsNullOrWhiteSpace(phone) ? (object)DBNull.Value : phone),
                new MySqlParameter("@p_Email",     string.IsNullOrWhiteSpace(email) ? (object)DBNull.Value : email),
                new MySqlParameter("@p_IsActive",  isActive ? 1 : 0)
            };
            return DbHelper.ExecuteNonQuery("sp_UpdateStore", parameters, CommandType.StoredProcedure) > 0;
        }

        public bool DeleteStore(int storeId)
        {
            var parameters = new[] { new MySqlParameter("@p_StoreId", storeId) };
            return DbHelper.ExecuteNonQuery("sp_DeleteStore", parameters, CommandType.StoredProcedure) > 0;
        }

        public DataTable GetStoreStats()
        {
            return DbHelper.ExecuteDataTable("sp_GetStoreStats", null, CommandType.StoredProcedure);
        }
    }
}
