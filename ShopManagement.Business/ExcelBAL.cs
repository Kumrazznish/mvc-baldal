using System;
using System.Data;
using System.IO;
using ClosedXML.Excel;

namespace ShopManagement.Business
{
    public class ExcelBAL
    {
        private readonly ProductBAL _productBAL = new ProductBAL();

        public DataTable ProcessExcelProductImport(Stream fileStream, out int totalCount, out int insertedCount, out int updatedCount, out int failedCount)
        {
            totalCount = 0;
            insertedCount = 0;
            updatedCount = 0;
            failedCount = 0;

            var resultDt = new DataTable("ImportResults");
            resultDt.Columns.Add("RowNumber", typeof(int));
            resultDt.Columns.Add("ProductCode", typeof(string));
            resultDt.Columns.Add("ProductName", typeof(string));
            resultDt.Columns.Add("Quantity", typeof(int));
            resultDt.Columns.Add("Price", typeof(decimal));
            resultDt.Columns.Add("Status", typeof(string));
            resultDt.Columns.Add("Message", typeof(string));

            using (var workbook = new XLWorkbook(fileStream))
            {
                var worksheet = workbook.Worksheet(1);
                var rows = worksheet.RangeUsed().RowsUsed();

                bool isFirstRow = true;
                int rowNum = 1;

                foreach (var row in rows)
                {
                    if (isFirstRow)
                    {
                        // Header row: ProductCode | ProductName | Quantity | Price | ImagePath
                        isFirstRow = false;
                        rowNum++;
                        continue;
                    }

                    totalCount++;
                    string productCode = row.Cell(1).GetString()?.Trim();
                    string productName = row.Cell(2).GetString()?.Trim();
                    string qtyStr = row.Cell(3).GetString()?.Trim();
                    string priceStr = row.Cell(4).GetString()?.Trim();
                    string imagePath = row.Cell(5).GetString()?.Trim();

                    if (string.IsNullOrWhiteSpace(productCode) && string.IsNullOrWhiteSpace(productName))
                    {
                        // empty row
                        continue;
                    }

                    int qty = 0;
                    decimal price = 0;
                    bool isQtyValid = int.TryParse(qtyStr, out qty);
                    bool isPriceValid = decimal.TryParse(priceStr, out price);

                    if (string.IsNullOrWhiteSpace(productCode) || string.IsNullOrWhiteSpace(productName) || !isQtyValid || !isPriceValid)
                    {
                        failedCount++;
                        resultDt.Rows.Add(rowNum, productCode, productName, qty, price, "Failed", "Invalid data format or missing required fields.");
                        rowNum++;
                        continue;
                    }

                    string operation;
                    bool success = _productBAL.UpsertProduct(productCode, productName, qty, price, imagePath, out operation);

                    if (success)
                    {
                        if (operation.Contains("Updated"))
                            updatedCount++;
                        else
                            insertedCount++;

                        resultDt.Rows.Add(rowNum, productCode, productName, qty, price, "Success", operation);
                    }
                    else
                    {
                        failedCount++;
                        resultDt.Rows.Add(rowNum, productCode, productName, qty, price, "Failed", operation);
                    }

                    rowNum++;
                }
            }

            return resultDt;
        }

        public byte[] GenerateSampleExcelTemplate()
        {
            using (var workbook = new XLWorkbook())
            {
                var ws = workbook.Worksheets.Add("Products");

                // Headers
                ws.Cell(1, 1).Value = "ProductCode";
                ws.Cell(1, 2).Value = "ProductName";
                ws.Cell(1, 3).Value = "Quantity";
                ws.Cell(1, 4).Value = "Price";
                ws.Cell(1, 5).Value = "ImagePath";

                // Header styling
                var headerRange = ws.Range("A1:E1");
                headerRange.Style.Font.Bold = true;
                headerRange.Style.Fill.BackgroundColor = XLColor.FromHtml("#2563EB");
                headerRange.Style.Font.FontColor = XLColor.White;

                // Sample data rows
                ws.Cell(2, 1).Value = "P101";
                ws.Cell(2, 2).Value = "Wireless Optical Mouse";
                ws.Cell(2, 3).Value = 25;
                ws.Cell(2, 4).Value = 499.00;
                ws.Cell(2, 5).Value = "/images/products/mouse.png";

                ws.Cell(3, 1).Value = "P102";
                ws.Cell(3, 2).Value = "Mechanical Gaming Keyboard";
                ws.Cell(3, 3).Value = 15;
                ws.Cell(3, 4).Value = 1899.00;
                ws.Cell(3, 5).Value = "/images/products/keyboard.png";

                ws.Cell(4, 1).Value = "P001"; // Test existing upsert
                ws.Cell(4, 2).Value = "Parker Roller Ball Pen";
                ws.Cell(4, 3).Value = 50; // Will be added to existing stock
                ws.Cell(4, 4).Value = 150.00;
                ws.Cell(4, 5).Value = "/images/products/pen.png";

                ws.Columns().AdjustToContents();

                using (var ms = new MemoryStream())
                {
                    workbook.SaveAs(ms);
                    return ms.ToArray();
                }
            }
        }
    }
}
