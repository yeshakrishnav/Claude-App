// Copyright (c) 2026 8848 Digital LLP. All rights reserved.
// Proprietary and confidential. Unauthorized copying, distribution, or use
// of this file, via any medium, is strictly prohibited without prior
// written permission from 8848 Digital LLP.

/**
 * Client script for the Supplier master form.
 *
 * Responsibilities:
 * - Render a colour badge adjacent to the Supplier Grade field on load and change.
 * - Toggle grade_effective_from as mandatory when a grade is selected.
 */

frappe.ui.form.on("Supplier", {
    /**
     * Fired when the Supplier form is refreshed / loaded.
     *
     * @param {object} frm - The Frappe form instance.
     * @returns {void}
     */
    refresh(frm) {
        renderGradeBadge(frm);
        setGradeEffectiveFromMandatory(frm);
    },

    /**
     * Fired when the supplier_grade field value changes.
     *
     * @param {object} frm - The Frappe form instance.
     * @returns {void}
     */
    supplier_grade(frm) {
        renderGradeBadge(frm);
        setGradeEffectiveFromMandatory(frm);
    },
});

/**
 * Inject a Frappe indicator badge next to the Supplier Grade field.
 *
 * Uses Frappe's built-in indicator CSS classes for theme consistency.
 * Green → green, Yellow → orange, Red → red.
 * Clears any existing badge before inserting a new one.
 *
 * @param {object} frm - The Frappe form instance.
 * @returns {void}
 */
function renderGradeBadge(frm) {
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
 * Toggle the mandatory state of the grade_effective_from field.
 *
 * Makes the field required when a Supplier Grade is selected,
 * and removes the mandatory constraint when the grade is cleared.
 *
 * @param {object} frm - The Frappe form instance.
 * @returns {void}
 */
function setGradeEffectiveFromMandatory(frm) {
    const isMandatory = Boolean(frm.doc.supplier_grade);
    frm.set_df_property("grade_effective_from", "reqd", isMandatory ? 1 : 0);
}
