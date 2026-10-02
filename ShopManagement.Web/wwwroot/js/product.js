// product.js - Product Inventory page logic

var upsertModal, editModal;

$(document).ready(function () {
    upsertModal = new bootstrap.Modal(document.getElementById('upsertProductModal'));
    editModal   = new bootstrap.Modal(document.getElementById('editProductModal'));
    loadProductsGrid();

    $("#upsertProductForm").on("submit", function (e) {
        e.preventDefault();
        var formData = new FormData(this);
        $.ajax({
            url: "/Product/Add",
            type: "POST",
            data: formData,
            contentType: false,
            processData: false,
            success: function (res) {
                if (res.success) {
                    Swal.fire({ icon: 'success', title: 'Saved', text: res.message, timer: 1500, showConfirmButton: false });
                    upsertModal.hide();
                    $("#upsertProductForm")[0].reset();
                    $("#productsGrid").data("kendoGrid").dataSource.read();
                } else {
                    Swal.fire({ icon: 'error', title: 'Error', text: res.message });
                }
            }
        });
    });

    $("#editProductForm").on("submit", function (e) {
        e.preventDefault();
        var formData = new FormData(this);
        $.ajax({
            url: "/Product/Edit",
            type: "POST",
            data: formData,
            contentType: false,
            processData: false,
            success: function (res) {
                if (res.success) {
                    Swal.fire({ icon: 'success', title: 'Updated', text: res.message, timer: 1500, showConfirmButton: false });
                    editModal.hide();
                    $("#productsGrid").data("kendoGrid").dataSource.read();
                } else {
                    Swal.fire({ icon: 'error', title: 'Error', text: res.message });
                }
            }
        });
    });
});

function loadProductsGrid() {
    $("#productsGrid").kendoGrid({
        dataSource: {
            transport: { read: { url: "/Product/GetProductsJson", dataType: "json" } },
            schema: {
                model: {
                    id: "ProductId",
                    fields: {
                        ProductId:   { type: "number" },
                        ProductCode: { type: "string" },
                        ProductName: { type: "string" },
                        Quantity:    { type: "number" },
                        Price:       { type: "number" },
                        ImagePath:   { type: "string" }
                    }
                }
            },
            pageSize: 10
        },
        pageable: true,
        sortable: true,
        filterable: true,
        columns: [
            {
                field: "ImagePath", title: "Image", width: 80, filterable: false, sortable: false,
                template: d => `<img src="${d.ImagePath || '/images/products/default-product.svg'}" style="width:40px;height:40px;object-fit:cover;border:1px solid #ccc;" />`
            },
            { field: "ProductCode", title: "Code", width: 120 },
            { field: "ProductName", title: "Product Name" },
            {
                field: "Quantity", title: "Stock", width: 100,
                template: d => `<strong>${d.Quantity}</strong>`
            },
            {
                field: "Price", title: "Price (Rs.)", width: 120,
                template: d => `Rs.${parseFloat(d.Price).toFixed(2)}`
            },
            {
                title: "Actions", width: 160, filterable: false, sortable: false,
                template: d => `
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="openEditModal(${d.ProductId})">Edit</button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteProduct(${d.ProductId}, '${(d.ProductName||'').replace(/'/g,"\\'")}')">Delete</button>
                `
            }
        ]
    });
}

function openUpsertModal() {
    $("#upsertProductForm")[0].reset();
    $("#upsert_imgPreview").attr("src", "/images/products/default-product.svg");
    upsertModal.show();
}

function openEditModal(productId) {
    $.getJSON("/Product/GetProductByIdJson?id=" + productId, function (data) {
        if (data && data.length > 0) {
            var item = data[0];
            $("#edit_productId").val(item.ProductId);
            $("#edit_productCode").val(item.ProductCode);
            $("#edit_productName").val(item.ProductName);
            $("#edit_quantity").val(item.Quantity);
            $("#edit_price").val(item.Price);
            $("#edit_imgPreview").attr("src", item.ImagePath || "/images/products/default-product.svg");
            editModal.show();
        }
    });
}

function deleteProduct(productId, name) {
    Swal.fire({
        title: 'Delete ' + name + '?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, Delete'
    }).then((res) => {
        if (res.isConfirmed) {
            $.post("/Product/Delete", { productId: productId }, function (r) {
                if (r.success) {
                    $("#productsGrid").data("kendoGrid").dataSource.read();
                } else {
                    Swal.fire('Error', r.message, 'error');
                }
            });
        }
    });
}

function previewImage(input, imgId) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = e => { document.getElementById(imgId).src = e.target.result; };
        reader.readAsDataURL(input.files[0]);
    }
}
