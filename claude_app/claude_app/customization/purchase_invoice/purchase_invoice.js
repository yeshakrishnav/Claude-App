// Copyright (c) 2026 8848 Digital LLP. All rights reserved.
// Proprietary and confidential. Unauthorized copying, distribution, or use
// of this file, via any medium, is strictly prohibited without prior
// written permission from 8848 Digital LLP.

frappe.ui.form.on("Purchase Invoice", {
    /**
     * Fires when the Purchase Invoice form refreshes.
     * Renders the supplier grade colour badge if a supplier is already selected.
     *
     * @param {Object} frm - The current Frappe form instance.
     */
    refresh(frm) {
        if (frm.doc.supplier) {
            renderTransactionGradeBadge(frm, frm.doc.supplier_grade);
        }
    },

    /**
     * Fires when the Supplier field changes on a Purchase Invoice.
     * Fetches the supplier's current grade and applies UX effects.
     *
     * @param {Object} frm - The current Frappe form instance.
     */
    supplier(frm) {
        if (!frm.doc.supplier) {
            frm.set_value("supplier_grade", "");
            clearTransactionGradeBadge(frm);
            return;
        }
        fetchAndApplySupplierGrade(frm);
    },
});

/**
 * Fetches supplier_grade from Supplier master and applies badge and messages.
 *
 * @param {Object} frm - The current Frappe form instance.
 */
function fetchAndApplySupplierGrade(frm) {
    frappe.db.get_value(
        "Supplier",
        frm.doc.supplier,
        "supplier_grade",
        (result) => {
            const grade = (result && result.supplier_grade) ? result.supplier_grade : "";
            frm.set_value("supplier_grade", grade);
            renderTransactionGradeBadge(frm, grade);
            showGradeMessage(grade);
        }
    );
}

/**
 * Renders a colour-coded grade badge adjacent to the Supplier field.
 *
 * @param {Object} frm   - The current Frappe form instance.
 * @param {string} grade - The Supplier Grade value.
 */
function renderTransactionGradeBadge(frm, grade) {
    const fieldWrapper = frm.get_field("supplier").$wrapper;
    fieldWrapper.find(".supplier-grade-badge").remove();
    if (!grade) return;
    const config = getGradeBadgeConfig(grade);
    if (!config) return;
    const badge = $(
        `<span class="supplier-grade-badge" style="margin-left: 8px; font-size: 12px; padding: 2px 8px; border-radius: 4px; background: ${config.color}; color: #fff; display: inline-block;">${config.label}</span>`
    );
    fieldWrapper.find(".control-value").append(badge);
}

/**
 * Removes the grade badge from the supplier field wrapper.
 *
 * @param {Object} frm - The current Frappe form instance.
 */
function clearTransactionGradeBadge(frm) {
    frm.get_field("supplier").$wrapper.find(".supplier-grade-badge").remove();
}

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

/**
 * Returns badge display configuration for a given Supplier Grade value.
 *
 * @param {string} grade - The Supplier Grade value.
 * @returns {Object|null} Config with color and label properties, or null.
 */
function getGradeBadgeConfig(grade) {
    const configs = {
        Green:  { color: "#28a745", label: __("Approved") },
        Yellow: { color: "#ffc107", label: __("Conditional") },
        Red:    { color: "#dc3545", label: __("Restricted") },
    };
    return configs[grade] || null;
}
