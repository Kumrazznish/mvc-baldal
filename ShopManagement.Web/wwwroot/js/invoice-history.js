// invoice-history.js - Invoice History page logic

var detailsModal;

$(document).ready(function () {
    detailsModal = new bootstrap.Modal(document.getElementById('invoiceDetailsModal'));
    loadInvoicesGrid();
});

function loadInvoicesGrid() {
    $("#invoicesGrid").kendoGrid({
        dataSource: {
            transport: { read: { url: "/Invoice/GetInvoicesJson", dataType: "json" } },
            schema: {
                model: {
                    id: "InvoiceId",
                    fields: {
                        InvoiceId:     { type: "number" },
                        InvoiceNo:     { type: "string" },
                        CustomerName:  { type: "string" },
                        CustomerPhone: { type: "string" },
                        TotalAmount:   { type: "number" },
                        InvoiceDate:   { type: "date" },
                        CreatedByName: { type: "string" }
                    }
                }
            },
            pageSize: 10
        },
        pageable: true,
        sortable: true,
        filterable: true,
        columns: [
            { field: "InvoiceNo", title: "Invoice No", width: 160 },
            { field: "CustomerName", title: "Customer Name" },
            { field: "CustomerPhone", title: "Phone", width: 140 },
            { field: "CreatedByName", title: "Cashier", width: 140 },
            {
                field: "InvoiceDate", title: "Date", width: 170,
                template: d => kendo.toString(kendo.parseDate(d.InvoiceDate), 'dd-MMM-yyyy hh:mm tt')
            },
            {
                field: "TotalAmount", title: "Total (Rs.)", width: 130,
                template: d => `Rs.${parseFloat(d.TotalAmount).toFixed(2)}`
            },
            {
                title: "Actions", width: 110, filterable: false, sortable: false,
                template: d => `<button class="btn btn-sm btn-outline-primary" onclick="viewDetails(${d.InvoiceId})">Details</button>`
            }
        ]
    });
}

function viewDetails(invoiceId) {
    $.getJSON("/Invoice/GetInvoiceDetailsJson?id=" + invoiceId, function (res) {
        if (res.success && res.header.length > 0) {
            var h = res.header[0];
            $("#modalInvoiceNo, #infoInvNo").text(h.InvoiceNo);
            $("#infoInvDate").text(kendo.toString(kendo.parseDate(h.InvoiceDate), 'dd-MMM-yyyy hh:mm tt'));
            $("#infoCustName").text(h.CustomerName);
            $("#infoCustPhone").text(h.CustomerPhone || "N/A");
            $("#infoBilledBy").text(h.CreatedByName);
            $("#modalGrandTotal").text("Rs." + parseFloat(h.TotalAmount).toFixed(2));

            var $tbody = $("#modalInvoiceDetailsBody");
            $tbody.empty();

            res.details.forEach((d, idx) => {
                $tbody.append(`
                    <tr>
                        <td>${idx + 1}</td>
                        <td>${d.ProductName} <span class="text-muted small">(${d.ProductCode || ''})</span></td>
                        <td class="text-center">${d.Quantity}</td>
                        <td class="text-end">Rs.${parseFloat(d.UnitPrice).toFixed(2)}</td>
                        <td class="text-end">Rs.${parseFloat(d.TotalAmount).toFixed(2)}</td>
                    </tr>
                `);
            });

            detailsModal.show();
        }
    });
}

function printInvoiceModal() {
    var printContents = document.getElementById("printableInvoiceArea").innerHTML;
    var win = window.open('', '', 'height=650,width=800');
    win.document.write('<html><head><title>Print Bill</title>');
    win.document.write('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">');
    win.document.write('</head><body class="p-4">');
    win.document.write(printContents);
    win.document.write('</body></html>');
    win.document.close();
    win.focus();
    setTimeout(() => { win.print(); win.close(); }, 500);
}
