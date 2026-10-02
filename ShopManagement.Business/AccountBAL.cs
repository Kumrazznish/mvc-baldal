using System;
using System.Data;
using ShopManagement.DataAccess;

namespace ShopManagement.Business
{
    public class AccountBAL
    {
        private readonly AccountDAL _dal = new AccountDAL();

        public DataTable Login(string username, string password)
        {
            if (string.IsNullOrWhiteSpace(username) || string.IsNullOrWhiteSpace(password))
            {
                return new DataTable();
            }

            return _dal.ValidateUser(username.Trim(), password.Trim());
        }
    }
}
