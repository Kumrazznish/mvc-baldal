using System;
using System.Data;
using ShopManagement.DataAccess;

namespace ShopManagement.Business
{
    public class StoreBAL
    {
        private readonly StoreDAL _dal = new StoreDAL();

        public DataTable GetAllStores(bool activeOnly = false)
        {
            return _dal.GetAllStores(activeOnly);
        }

        public DataTable GetStoreById(int storeId)
        {
            return _dal.GetStoreById(storeId);
        }

        public DataTable GetStoreStats()
        {
            return _dal.GetStoreStats();
        }

        public bool CreateStore(string storeCode, string storeName, string address, string phone, string email, out string errorMessage)
        {
            errorMessage = string.Empty;

            if (string.IsNullOrWhiteSpace(storeCode) || string.IsNullOrWhiteSpace(storeName))
            {
                errorMessage = "Store Code and Store Name are required.";
                return false;
            }

            return _dal.CreateStore(storeCode.Trim().ToUpper(), storeName.Trim(), address, phone, email, out errorMessage);
        }

        public bool UpdateStore(int storeId, string storeName, string address, string phone, string email, bool isActive, out string errorMessage)
        {
            errorMessage = string.Empty;

            if (string.IsNullOrWhiteSpace(storeName))
            {
                errorMessage = "Store Name is required.";
                return false;
            }

            return _dal.UpdateStore(storeId, storeName.Trim(), address, phone, email, isActive);
        }

        public bool DeleteStore(int storeId)
        {
            return _dal.DeleteStore(storeId);
        }
    }
}
