// store.js - Stores & Branch Management page logic

var createModal, editModal;

$(document).ready(function () {
    createModal = new bootstrap.Modal(document.getElementById('createStoreModal'));
    editModal   = new bootstrap.Modal(document.getElementById('editStoreModal'));
    loadStoresGrid();

    $("#createStoreForm").on("submit", function (e) {
        e.preventDefault();
        $.post("/Store/Create", $(this).serialize(), function (res) {
            if (res.success) {
                Swal.fire({ icon: 'success', title: 'Created', text: res.message, timer: 1500, showConfirmButton: false });
                createModal.hide();
                $("#createStoreForm")[0].reset();
                $("#storesGrid").data("kendoGrid").dataSource.read();
            } else {
                Swal.fire({ icon: 'error', title: 'Error', text: res.message });
            }
        });
    });

    $("#editStoreForm").on("submit", function (e) {
        e.preventDefault();
        $.post("/Store/Update", $(this).serialize(), function (res) {
            if (res.success) {
                Swal.fire({ icon: 'success', title: 'Updated', text: res.message, timer: 1500, showConfirmButton: false });
                editModal.hide();
                $("#storesGrid").data("kendoGrid").dataSource.read();
            } else {
                Swal.fire({ icon: 'error', title: 'Error', text: res.message });
            }
        });
    });
});

function loadStoresGrid() {
    $("#storesGrid").kendoGrid({
        dataSource: {
            transport: { read: { url: "/Store/GetStoresJson", dataType: "json" } },
            schema: {
                model: {
                    id: "StoreId",
                    fields: {
                        StoreId:   { type: "number" },
                        StoreCode: { type: "string" },
                        StoreName: { type: "string" },
                        Phone:     { type: "string" },
                        Address:   { type: "string" },
                        IsActive:  { type: "number" }
                    }
                }
            },
            pageSize: 10
        },
        pageable: true,
        sortable: true,
        filterable: true,
        columns: [
            { field: "StoreCode", title: "Code", width: 120 },
            { field: "StoreName", title: "Store Name" },
            { field: "Phone", title: "Phone", width: 140 },
            { field: "Address", title: "Address" },
            {
                field: "IsActive", title: "Status", width: 120,
                template: d => d.IsActive === 1 ? '<span class="badge bg-success">Active</span>' : '<span class="badge bg-secondary">Inactive</span>'
            },
            {
                title: "Actions", width: 160, filterable: false, sortable: false,
                template: d => `
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="openEditModal(${d.StoreId}, '${(d.StoreName||'').replace(/'/g,"\\'")}', '${(d.Phone||'').replace(/'/g,"\\'")}', '${(d.Address||'').replace(/'/g,"\\'")}', ${d.IsActive})">Edit</button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteStore(${d.StoreId})">Delete</button>
                `
            }
        ]
    });
}

function openCreateModal() {
    $("#createStoreForm")[0].reset();
    createModal.show();
}

function openEditModal(id, name, phone, address, isActive) {
    $("#edit_storeId").val(id);
    $("#edit_storeName").val(name);
    $("#edit_phone").val(phone);
    $("#edit_address").val(address);
    $("#edit_isActive").prop("checked", isActive === 1);
    editModal.show();
}

function deleteStore(storeId) {
    Swal.fire({
        title: 'Deactivate Store?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, Deactivate'
    }).then((res) => {
        if (res.isConfirmed) {
            $.post("/Store/Delete", { storeId: storeId }, function (r) {
                $("#storesGrid").data("kendoGrid").dataSource.read();
            });
        }
    });
}
