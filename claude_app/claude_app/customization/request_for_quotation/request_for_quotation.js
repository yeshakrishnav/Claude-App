// Copyright (c) 2026 8848 Digital LLP. All rights reserved.
// Proprietary and confidential. Unauthorized copying, distribution, or use
// of this file, via any medium, is strictly prohibited without prior
// written permission from 8848 Digital LLP.

// Note: Request for Quotation uses a child table (rfq_suppliers) for suppliers.
// The supplier_grade field on the parent form is populated from the first
// supplier row. Client-side grade events are wired to the child table row.

frappe.ui.form.on("Purchase Order Supplier", {
    /**
     * Fires when the Supplier field changes inside an RFQ Supplier child row.
     * Fetches the supplier's current grade and applies UX effects on the parent form.
     *
     * @param {Object} frm  - The parent RFQ Frappe form instance.
     * @param {string} cdt  - Child doctype name.
     * @param {string} cdn  - Child document name (row identifier).
     */
    supplier(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (!row || !row.supplier) {
            frm.set_value("supplier_grade", "");
            return;
        }
        frappe.db.get_value(
            "Supplier",
            row.supplier,
            "supplier_grade",
            (result) => {
                const grade = (result && result.supplier_grade) ? result.supplier_grade : "";
                frm.set_value("supplier_grade", grade);
                showGradeMessage(grade);
            }
        );
    },
});

frappe.ui.form.on("Request for Quotation", {
    /**
     * Fires when the RFQ form refreshes.
     * Shows the grade message for the current supplier_grade value if set.
     *
     * @param {Object} frm - The current Frappe form instance.
     */
    refresh(frm) {
        if (frm.doc.supplier_grade) {
            showGradeMessage(frm.doc.supplier_grade);
        }
    },
});

/**
 * Shows an inline grade message appropriate to the supplier's grade.
 *
 * @param {string} grade - The Supplier Grade value.
 */
function showGradeMessage(grade) {
    if (grade === "Red") {
        frappe.msgprint({ title: __("Restricted Supplier"), message: __("This supplier is not approved for procurement. Please select an approved supplier to proceed."), indicator: "red" });
    } else if (grade === "Yellow") {
        frappe.msgprint({ title: __("Conditional Supplier"), message: __("This supplier requires management approval. The transaction will be routed for approval before it can be submitted."), indicator: "orange" });
    } else if (!grade) {
        frappe.msgprint({ title: __("Ungraded Supplier"), message: __("No procurement grade is assigned to this supplier. Please configure the supplier grade before proceeding."), indicator: "yellow" });
    }
}
