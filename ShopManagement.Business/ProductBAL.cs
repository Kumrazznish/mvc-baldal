using System;
using System.Data;
using ShopManagement.DataAccess;

namespace ShopManagement.Business
{
    public class ProductBAL
    {
        private readonly ProductDAL _dal = new ProductDAL();

        public DataTable GetAllProducts(bool activeOnly = true)
        {
            return _dal.GetAllProducts(activeOnly);
        }

        public DataTable GetProductById(int productId)
        {
            return _dal.GetProductById(productId);
        }

        /// <summary>
        /// Upsert: If product already exists (by code OR name), increment its stock.
        /// If not found, create a new product. Missing image defaults to default-product.svg.
        /// </summary>
        public bool UpsertProduct(string productCode, string productName, int quantity, decimal price, string imagePath, out string operation)
        {
            if (string.IsNullOrWhiteSpace(productCode) || string.IsNullOrWhiteSpace(productName))
            {
                operation = "Product code and name are required.";
                return false;
            }

            if (quantity < 0) quantity = 0;
            if (price < 0) price = 0;

            return _dal.UpsertProduct(productCode.Trim(), productName.Trim(), quantity, price, imagePath, out operation);
        }

        /// <summary>
        /// Edit existing product: sets exact quantity, price, name, and optionally updates image.
        /// </summary>
        public bool UpdateProduct(int productId, string productName, int quantity, decimal price, string newImagePath, out string errorMessage)
        {
            errorMessage = string.Empty;

            if (string.IsNullOrWhiteSpace(productName))
            {
                errorMessage = "Product Name is required.";
                return false;
            }

            if (quantity < 0) quantity = 0;
            if (price < 0) price = 0;

            return _dal.UpdateProduct(productId, productName.Trim(), quantity, price, newImagePath, out errorMessage);
        }

        public bool DeleteProduct(int productId)
        {
            return _dal.DeleteProduct(productId);
        }

        public DataTable SearchAvailableProducts(string term)
        {
            return _dal.SearchAvailableProducts(term);
        }
    }
}
