using System;
using System.Data;
using MySqlConnector;

namespace ShopManagement.DataAccess
{
    public class ProductDAL
    {
        public DataTable GetAllProducts(bool activeOnly = true)
        {
            var parameters = new[] { new MySqlParameter("@p_ActiveOnly", activeOnly) };
            return DbHelper.ExecuteDataTable("sp_GetAllProducts", parameters, CommandType.StoredProcedure);
        }

        public DataTable GetProductById(int productId)
        {
            var parameters = new[] { new MySqlParameter("@p_ProductId", productId) };
            return DbHelper.ExecuteDataTable("sp_GetProductById", parameters, CommandType.StoredProcedure);
        }

        public DataTable CheckProductExists(string productCode, string productName)
        {
            var parameters = new[]
            {
                new MySqlParameter("@p_ProductCode", productCode ?? string.Empty),
                new MySqlParameter("@p_ProductName", productName ?? string.Empty)
            };
            return DbHelper.ExecuteDataTable("sp_CheckProductExists", parameters, CommandType.StoredProcedure);
        }

        public bool UpsertProduct(string productCode, string productName, int quantity, decimal price, string imagePath, out string operation)
        {
            var dtExisting = CheckProductExists(productCode, productName);

            if (dtExisting != null && dtExisting.Rows.Count > 0)
            {
                int existingId = Convert.ToInt32(dtExisting.Rows[0]["ProductId"]);
                string existingImage = Convert.ToString(dtExisting.Rows[0]["ImagePath"]);
                int currentQty = Convert.ToInt32(dtExisting.Rows[0]["Quantity"]);

                string resolvedImage = string.IsNullOrWhiteSpace(imagePath) ? existingImage : imagePath;

                var updateParams = new[]
                {
                    new MySqlParameter("@p_ProductId",   existingId),
                    new MySqlParameter("@p_ProductName", productName),
                    new MySqlParameter("@p_Quantity",    currentQty + quantity),
                    new MySqlParameter("@p_Price",       price),
                    new MySqlParameter("@p_ImagePath",   resolvedImage ?? "/images/products/default-product.svg")
                };

                int rows = DbHelper.ExecuteNonQuery("sp_UpdateProduct", updateParams, CommandType.StoredProcedure);
                operation = "Updated (Stock Incremented)";
                return rows > 0;
            }
            else
            {
                string defaultImage = string.IsNullOrWhiteSpace(imagePath)
                    ? "/images/products/default-product.svg"
                    : imagePath;

                var insertParams = new[]
                {
                    new MySqlParameter("@p_ProductCode", productCode),
                    new MySqlParameter("@p_ProductName", productName),
                    new MySqlParameter("@p_Quantity",    quantity),
                    new MySqlParameter("@p_Price",       price),
                    new MySqlParameter("@p_ImagePath",   defaultImage)
                };

                int rows = DbHelper.ExecuteNonQuery("sp_CreateProduct", insertParams, CommandType.StoredProcedure);
                operation = "Created New Product";
                return rows > 0;
            }
        }

        public bool UpdateProduct(int productId, string productName, int quantity, decimal price, string newImagePath, out string errorMessage)
        {
            errorMessage = string.Empty;
            try
            {
                var parameters = new[]
                {
                    new MySqlParameter("@p_ProductId",   productId),
                    new MySqlParameter("@p_ProductName", productName),
                    new MySqlParameter("@p_Quantity",    quantity),
                    new MySqlParameter("@p_Price",       price),
                    new MySqlParameter("@p_ImagePath",   string.IsNullOrWhiteSpace(newImagePath) ? (object)DBNull.Value : newImagePath)
                };

                return DbHelper.ExecuteNonQuery("sp_UpdateProduct", parameters, CommandType.StoredProcedure) > 0;
            }
            catch (Exception ex)
            {
                errorMessage = ex.Message;
                return false;
            }
        }

        public bool DeleteProduct(int productId)
        {
            var parameters = new[] { new MySqlParameter("@p_ProductId", productId) };
            return DbHelper.ExecuteNonQuery("sp_DeleteProduct", parameters, CommandType.StoredProcedure) > 0;
        }

        public DataTable SearchAvailableProducts(string term)
        {
            var parameters = new[] { new MySqlParameter("@p_Term", term ?? string.Empty) };
            return DbHelper.ExecuteDataTable("sp_SearchAvailableProducts", parameters, CommandType.StoredProcedure);
        }
    }
}
