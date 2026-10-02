// invoice-create.js - New Invoice (POS) page logic

var cart = [];
var selectedProduct = null;

$(document).ready(function () {
    initProductDropdown();
});

function initProductDropdown() {
    $("#productDropdown").kendoDropDownList({
        dataTextField: "ProductName",
        dataValueField: "ProductId",
        filter: "contains",
        optionLabel: "-- Choose a product --",
        template: d => d.ProductId ? `${d.ProductName} [Code: ${d.ProductCode}] - Rs.${parseFloat(d.Price).toFixed(2)} (Stock: ${d.Quantity})` : d.ProductName,
        dataSource: {
            transport: { read: { url: "/Product/GetProductsJson", dataType: "json" } },
            schema: {
                parse: function (response) {
                    return response.filter(x => x.Quantity > 0);
                }
            }
        },
        change: function (e) {
            var item = this.dataItem();
            if (item && item.ProductId) {
                selectedProduct = item;
                $("#txtPrice").val(parseFloat(item.Price).toFixed(2));
                $("#numQty").attr("max", item.Quantity).val(1);
            } else {
                selectedProduct = null;
                $("#txtPrice").val("0.00");
            }
        }
    });
}

function addItemToCart() {
    if (!selectedProduct) {
        Swal.fire({ icon: 'warning', title: 'Select Product', text: 'Please select a product first.' });
        return;
    }

    var qty = parseInt($("#numQty").val()) || 1;
    if (qty <= 0) {
        Swal.fire({ icon: 'warning', title: 'Invalid Qty', text: 'Quantity must be at least 1.' });
        return;
    }

    var existing = cart.find(x => x.productId === selectedProduct.ProductId);
    var maxStock = selectedProduct.Quantity;

    if (existing) {
        if (existing.quantity + qty > maxStock) {
            Swal.fire({ icon: 'warning', title: 'Stock Limit', text: `Cannot add more. Available stock: ${maxStock}` });
            return;
        }
        existing.quantity += qty;
    } else {
        if (qty > maxStock) {
            Swal.fire({ icon: 'warning', title: 'Stock Limit', text: `Only ${maxStock} units available.` });
            return;
        }
        cart.push({
            productId: selectedProduct.ProductId,
            productName: selectedProduct.ProductName,
            unitPrice: parseFloat(selectedProduct.Price),
            quantity: qty,
            maxStock: maxStock
        });
    }

    renderCart();
    // Reset dropdown
    $("#productDropdown").data("kendoDropDownList").value("");
    selectedProduct = null;
    $("#txtPrice").val("0.00");
    $("#numQty").val(1);
}

function renderCart() {
    var $tbody = $("#cartTableBody");
    $tbody.empty();

    if (cart.length === 0) {
        $tbody.html('<tr id="emptyCartRow"><td colspan="6" class="text-center text-muted py-4">No items added yet. Select a product and click Add to Cart.</td></tr>');
        $("#lblTotalItems").text("0");
        $("#lblGrandTotal").text("Rs.0.00");
        return;
    }

    var grandTotal = 0;
    var totalItems = 0;

    cart.forEach((item, index) => {
        var lineTotal = item.quantity * item.unitPrice;
        grandTotal += lineTotal;
        totalItems += item.quantity;

        $tbody.append(`
            <tr>
                <td>${index + 1}</td>
                <td>${item.productName}</td>
                <td class="text-center">${item.quantity}</td>
                <td class="text-end">Rs.${item.unitPrice.toFixed(2)}</td>
                <td class="text-end">Rs.${lineTotal.toFixed(2)}</td>
                <td class="text-center">
                    <button type="button" class="btn btn-sm btn-outline-danger py-0 px-2" onclick="removeItem(${index})">&times;</button>
                </td>
            </tr>
        `);
    });

    $("#lblTotalItems").text(totalItems);
    $("#lblGrandTotal").text("Rs." + grandTotal.toFixed(2));
}

function removeItem(index) {
    cart.splice(index, 1);
    renderCart();
}

function clearCart() {
    cart = [];
    renderCart();
}

function submitInvoice() {
    var custName = $("#txtCustName").val().trim();
    var custPhone = $("#txtCustPhone").val().trim();

    if (!custName) {
        Swal.fire({ icon: 'warning', title: 'Missing Info', text: 'Please enter customer name.' });
        return;
    }

    if (cart.length === 0) {
        Swal.fire({ icon: 'warning', title: 'Empty Cart', text: 'Please add at least one product to the bill.' });
        return;
    }

    $.post("/Invoice/Create", {
        customerName: custName,
        customerPhone: custPhone,
        itemsJson: JSON.stringify(cart)
    }, function (res) {
        if (res.success) {
            Swal.fire({
                icon: 'success',
                title: 'Invoice Created!',
                text: 'Bill No: ' + res.invoiceNo,
                confirmButtonText: 'View History'
            }).then(() => {
                window.location.href = "/Invoice/History";
            });
        } else {
            Swal.fire({ icon: 'error', title: 'Billing Error', text: res.message });
        }
    });
}
