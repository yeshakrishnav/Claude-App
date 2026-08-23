// Copyright (c) 2026 8848 Digital LLP. All rights reserved.
// Proprietary and confidential. Unauthorized copying, distribution, or use
// of this file, via any medium, is strictly prohibited without prior
// written permission from 8848 Digital LLP.

/**
 * Client script for the Purchase Invoice form.
 *
 * Fetches the supplier grade on supplier selection and renders the colour badge.
 */

frappe.ui.form.on("Purchase Invoice", {
    /**
     * Fired when the form is refreshed.
     *
     * @param {object} frm - The Frappe form instance.
     * @returns {void}
     */
    refresh(frm) {
        if (frm.doc.supplier) {
            renderSupplierGradeBadge(frm);
        }
    },

    /**
     * Fired when the supplier field changes.
     *
     * @param {object} frm - The Frappe form instance.
     * @returns {void}
     */
    supplier(frm) {
        if (!frm.doc.supplier) {
            clearSupplierGradeBadge(frm);
            return;
        }
        fetchAndApplySupplierGrade(frm);
    },
});

/**
 * Fetch the supplier_grade from the Supplier master and apply UI feedback.
 *
 * @param {object} frm - The Frappe form instance.
 * @returns {void}
 */
function fetchAndApplySupplierGrade(frm) {
    frappe.db.get_value(
        "Supplier",
        frm.doc.supplier,
        "supplier_grade",
        (data) => {
            const grade = (data && data.supplier_grade) || "";
            frm.set_value("supplier_grade", grade);
            renderSupplierGradeBadge(frm);
            showGradeMessage(frm, grade);
        }
    );
}

/**
 * Render the colour indicator badge next to the supplier_grade field.
 *
 * @param {object} frm - The Frappe form instance.
 * @returns {void}
 */
function renderSupplierGradeBadge(frm) {
    const gradeField = frm.get_field("supplier_grade");
    if (!gradeField) return;

    const $wrapper = gradeField.$wrapper;
    $wrapper.find(".grade-badge").remove();

    const grade = frm.doc.supplier_grade;
    if (!grade) return;

    const colourMap = {
        Green: { colour: "green", label: "Approved" },
        Yellow: { colour: "orange", label: "Conditional" },
        Red: { colour: "red", label: "Restricted" },
    };

    const config = colourMap[grade];
    if (!config) return;

    const badge = $(
        `<span class="grade-badge indicator ${config.colour}" style="margin-left:8px;font-size:12px;">${config.label}</span>`
    );
    $wrapper.find(".control-label").append(badge);
}

/**
 * Remove the grade badge when the supplier field is cleared.
 *
 * @param {object} frm - The Frappe form instance.
 * @returns {void}
 */
function clearSupplierGradeBadge(frm) {
    const gradeField = frm.get_field("supplier_grade");
    if (gradeField) {
        gradeField.$wrapper.find(".grade-badge").remove();
    }
}

/**
 * Display the appropriate UX message based on the fetched supplier grade.
 *
 * @param {object} frm   - The Frappe form instance.
 * @param {string} grade - The fetched supplier grade value.
 * @returns {void}
 */
function showGradeMessage(frm, grade) {
    if (grade === "Red") {
        frappe.msgprint({
            title: __("Supplier Not Approved"),
            indicator: "red",
            message: __(
                "This supplier is not approved for procurement. Please select an approved supplier to proceed."
            ),
        });
    } else if (grade === "Yellow") {
        frappe.msgprint({
            title: __("Management Approval Required"),
            indicator: "orange",
            message: __(
                "This supplier requires management approval. The transaction will be routed for approval before it can be submitted."
            ),
        });
    } else if (!grade) {
        frappe.msgprint({
            title: __("Supplier Grade Not Set"),
            indicator: "orange",
            message: __(
                "No procurement grade is assigned to this supplier. Please configure the supplier grade before proceeding."
            ),
        });
    }
}
