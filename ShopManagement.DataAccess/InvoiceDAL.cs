using System;
using System.Data;
using MySqlConnector;

namespace ShopManagement.DataAccess
{
    public class InvoiceDAL
    {
        public bool CreateInvoice(string customerName, string customerPhone, int createdBy, DataTable items, out string invoiceNo, out string errorMessage)
        {
            invoiceNo    = "INV-" + DateTime.Now.ToString("yyyyMMddHHmmss");
            errorMessage = string.Empty;

            using (var conn = DbHelper.GetConnection())
            using (var trans = conn.BeginTransaction())
            {
                try
                {
                    decimal grandTotal = 0;

                    // ── Step 1: Validate stock availability for every item (FOR UPDATE lock) ──
                    foreach (DataRow row in items.Rows)
                    {
                        int     productId = Convert.ToInt32(row["ProductId"]);
                        int     qty       = Convert.ToInt32(row["Quantity"]);
                        decimal unitPrice = Convert.ToDecimal(row["UnitPrice"]);
                        grandTotal += qty * unitPrice;

                        using (var cmd = new MySqlCommand("sp_CheckProductStock", conn, trans))
                        {
                            cmd.CommandType = CommandType.StoredProcedure;
                            cmd.Parameters.AddWithValue("p_ProductId", productId);

                            using (var reader = cmd.ExecuteReader())
                            {
                                if (!reader.Read())
                                {
                                    reader.Close();
                                    errorMessage = $"Product ID {productId} does not exist or is inactive.";
                                    trans.Rollback();
                                    return false;
                                }

                                string prodName    = reader["ProductName"].ToString();
                                int    stockOnHand = Convert.ToInt32(reader["Quantity"]);
                                reader.Close();

                                if (stockOnHand < qty)
                                {
                                    errorMessage = $"Insufficient stock for '{prodName}'. Available: {stockOnHand}, Requested: {qty}.";
                                    trans.Rollback();
                                    return false;
                                }
                            }
                        }
                    }

                    // ── Step 2: Insert Invoice Header → get new InvoiceId ──
                    int invoiceId;
                    using (var cmd = new MySqlCommand("sp_InsertInvoiceHeader", conn, trans))
                    {
                        cmd.CommandType = CommandType.StoredProcedure;
                        cmd.Parameters.AddWithValue("p_InvoiceNo",     invoiceNo);
                        cmd.Parameters.AddWithValue("p_CustomerName",  customerName);
                        cmd.Parameters.AddWithValue("p_CustomerPhone", string.IsNullOrWhiteSpace(customerPhone) ? (object)DBNull.Value : customerPhone);
                        cmd.Parameters.AddWithValue("p_CreatedBy",     createdBy);
                        cmd.Parameters.AddWithValue("p_TotalAmount",   grandTotal);

                        using (var reader = cmd.ExecuteReader())
                        {
                            reader.Read();
                            invoiceId = Convert.ToInt32(reader["NewInvoiceId"]);
                        }
                    }

                    // ── Step 3: Insert each detail row and deduct stock ──
                    foreach (DataRow row in items.Rows)
                    {
                        int     productId = Convert.ToInt32(row["ProductId"]);
                        string  prodName  = Convert.ToString(row["ProductName"]) ?? "";
                        int     qty       = Convert.ToInt32(row["Quantity"]);
                        decimal unitPrice = Convert.ToDecimal(row["UnitPrice"]);
                        decimal lineTotal = qty * unitPrice;

                        // 3a. Insert detail line
                        using (var cmd = new MySqlCommand("sp_InsertInvoiceDetail", conn, trans))
                        {
                            cmd.CommandType = CommandType.StoredProcedure;
                            cmd.Parameters.AddWithValue("p_InvoiceId",   invoiceId);
                            cmd.Parameters.AddWithValue("p_ProductId",   productId);
                            cmd.Parameters.AddWithValue("p_ProductName", prodName);
                            cmd.Parameters.AddWithValue("p_Quantity",    qty);
                            cmd.Parameters.AddWithValue("p_UnitPrice",   unitPrice);
                            cmd.Parameters.AddWithValue("p_TotalAmount", lineTotal);
                            cmd.ExecuteNonQuery();
                        }

                        // 3b. Deduct stock
                        using (var cmd = new MySqlCommand("sp_DeductProductStock", conn, trans))
                        {
                            cmd.CommandType = CommandType.StoredProcedure;
                            cmd.Parameters.AddWithValue("p_ProductId", productId);
                            cmd.Parameters.AddWithValue("p_Quantity",  qty);
                            cmd.ExecuteNonQuery();
                        }
                    }

                    trans.Commit();
                    return true;
                }
                catch (Exception ex)
                {
                    trans.Rollback();
                    errorMessage = ex.Message;
                    return false;
                }
            }
        }


        public DataTable GetInvoiceHistory(int? createdBy = null)
        {
            var parameters = new[]
            {
                new MySqlParameter("@p_CreatedBy", createdBy.HasValue ? (object)createdBy.Value : DBNull.Value)
            };
            return DbHelper.ExecuteDataTable("sp_GetInvoiceHistory", parameters, CommandType.StoredProcedure);
        }

        public DataTable GetInvoiceHeader(int invoiceId)
        {
            var parameters = new[] { new MySqlParameter("@p_InvoiceId", invoiceId) };
            return DbHelper.ExecuteDataTable("sp_GetInvoiceHeader", parameters, CommandType.StoredProcedure);
        }

        public DataTable GetInvoiceDetails(int invoiceId)
        {
            var parameters = new[] { new MySqlParameter("@p_InvoiceId", invoiceId) };
            return DbHelper.ExecuteDataTable("sp_GetInvoiceDetails", parameters, CommandType.StoredProcedure);
        }

        public DataTable GetDashboardMetrics()
        {
            return DbHelper.ExecuteDataTable("sp_GetDashboardMetrics", null, CommandType.StoredProcedure);
        }
    }
}
