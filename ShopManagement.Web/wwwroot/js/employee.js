// employee.js - Desk Logins (Staff Accounts) page logic

var addModal, editModal;

$(document).ready(function () {
    addModal  = new bootstrap.Modal(document.getElementById('addEmployeeModal'));
    editModal = new bootstrap.Modal(document.getElementById('editEmployeeModal'));
    loadEmployeesGrid();

    $("#addEmployeeForm").on("submit", function (e) {
        e.preventDefault();
        $.post("/Employee/Add", $(this).serialize(), function (res) {
            if (res.success) {
                Swal.fire({ icon: 'success', title: 'Created', text: res.message, timer: 1500, showConfirmButton: false });
                addModal.hide();
                $("#addEmployeeForm")[0].reset();
                $("#employeesGrid").data("kendoGrid").dataSource.read();
            } else {
                Swal.fire({ icon: 'error', title: 'Error', text: res.message });
            }
        });
    });

    $("#editEmployeeForm").on("submit", function (e) {
        e.preventDefault();
        $.post("/Employee/Update", $(this).serialize(), function (res) {
            if (res.success) {
                Swal.fire({ icon: 'success', title: 'Updated', text: res.message, timer: 1500, showConfirmButton: false });
                editModal.hide();
                $("#employeesGrid").data("kendoGrid").dataSource.read();
            } else {
                Swal.fire({ icon: 'error', title: 'Error', text: res.message });
            }
        });
    });
});

function loadEmployeesGrid() {
    $("#employeesGrid").kendoGrid({
        dataSource: {
            transport: { read: { url: "/Employee/GetEmployeesJson", dataType: "json" } },
            schema: {
                model: {
                    id: "UserId",
                    fields: {
                        UserId:     { type: "number" },
                        Name:       { type: "string" },
                        Username:   { type: "string" },
                        Role:       { type: "string" },
                        StoreName:  { type: "string" },
                        IsActive:   { type: "number" },
                        CreatedDate:{ type: "date" }
                    }
                }
            },
            pageSize: 10
        },
        pageable: true,
        sortable: true,
        filterable: true,
        columns: [
            { field: "Name", title: "Full Name" },
            { field: "Username", title: "Username", width: 150 },
            { field: "StoreName", title: "Branch / Store", width: 160 },
            {
                field: "IsActive", title: "Status", width: 120,
                template: d => d.IsActive === 1 ? '<span class="badge bg-success">Active</span>' : '<span class="badge bg-secondary">Disabled</span>'
            },
            {
                title: "Actions", width: 220, filterable: false, sortable: false,
                template: d => `
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="openEditModal(${d.UserId}, '${(d.Name||'').replace(/'/g,"\\'")}', ${d.IsActive})">Edit</button>
                    <button class="btn btn-sm btn-outline-secondary me-1" onclick="toggleStatus(${d.UserId})">Toggle</button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteEmployee(${d.UserId})">Deactivate</button>
                `
            }
        ]
    });
}

function openAddModal() {
    $("#addEmployeeForm")[0].reset();
    addModal.show();
}

function openEditModal(userId, name, isActive) {
    $("#edit_userId").val(userId);
    $("#edit_name").val(name);
    $("#edit_isActive").prop("checked", isActive === 1);
    editModal.show();
}

function toggleStatus(userId) {
    $.post("/Employee/ToggleStatus", { userId: userId }, function (res) {
        $("#employeesGrid").data("kendoGrid").dataSource.read();
    });
}

function deleteEmployee(userId) {
    Swal.fire({
        title: 'Deactivate Login?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, Deactivate'
    }).then((res) => {
        if (res.isConfirmed) {
            $.post("/Employee/Delete", { userId: userId }, function (r) {
                $("#employeesGrid").data("kendoGrid").dataSource.read();
            });
        }
    });
}
