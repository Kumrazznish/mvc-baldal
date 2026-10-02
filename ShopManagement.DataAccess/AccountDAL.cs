using System.Data;
using MySqlConnector;

namespace ShopManagement.DataAccess
{
    public class AccountDAL
    {
        public DataTable ValidateUser(string username, string password)
        {
            var parameters = new[]
            {
                new MySqlParameter("@p_Username", username),
                new MySqlParameter("@p_Password", password)
            };

            return DbHelper.ExecuteDataTable("sp_ValidateUser", parameters, CommandType.StoredProcedure);
        }
    }
}
