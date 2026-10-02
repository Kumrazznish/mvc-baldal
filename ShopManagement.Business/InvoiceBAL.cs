using System;
using System.Data;
using ShopManagement.DataAccess;

namespace ShopManagement.Business
{
    public class InvoiceBAL
    {
        private readonly InvoiceDAL _dal = new InvoiceDAL();

        public bool CreateInvoice(string customerName, string customerPhone, int createdBy, DataTable items, out string invoiceNo, out string errorMessage)
        {
            invoiceNo = string.Empty;
            errorMessage = string.Empty;

            if (string.IsNullOrWhiteSpace(customerName))
            {
                errorMessage = "Customer Name is required.";
                return false;
            }

            if (items == null || items.Rows.Count == 0)
            {
                errorMessage = "Invoice must contain at least one product item.";
                return false;
            }

            return _dal.CreateInvoice(customerName.Trim(), customerPhone?.Trim(), createdBy, items, out invoiceNo, out errorMessage);
        }

        public DataTable GetInvoiceHistory(int? createdBy = null)
        {
            return _dal.GetInvoiceHistory(createdBy);
        }

        public DataTable GetInvoiceHeader(int invoiceId)
        {
            return _dal.GetInvoiceHeader(invoiceId);
        }

        public DataTable GetInvoiceDetails(int invoiceId)
        {
            return _dal.GetInvoiceDetails(invoiceId);
        }

        public DataTable GetDashboardMetrics()
        {
            return _dal.GetDashboardMetrics();
        }
    }
}
