// Copyright (c) 2026 8848 Digital LLP. All rights reserved.
// Proprietary and confidential. Unauthorized copying, distribution, or use
// of this file, via any medium, is strictly prohibited without prior
// written permission from 8848 Digital LLP.

frappe.ui.form.on("Supplier", {
    /**
     * Fires when the Supplier form is refreshed or first loaded.
     * Renders the colour badge for the current Supplier Grade value.
     *
     * @param {Object} frm - The current Frappe form instance.
     */
    refresh(frm) {
        renderSupplierGradeBadge(frm);
    },

    /**
     * Fires when the Supplier Grade field value changes.
     * Re-renders the colour badge and toggles the mandatory state of
     * Grade Effective From based on whether a grade is selected.
     *
     * @param {Object} frm - The current Frappe form instance.
     */
    supplier_grade(frm) {
        renderSupplierGradeBadge(frm);
        toggleGradeEffectiveFromMandatory(frm);
    },
});

/**
 * Renders a colour-coded indicator badge adjacent to the Supplier Grade field.
 * Uses Frappe's built-in indicator CSS classes for visual consistency.
 * Clears any existing badge before inserting the new one.
 *
 * @param {Object} frm - The current Frappe form instance.
 */
function renderSupplierGradeBadge(frm) {
    const grade = frm.doc.supplier_grade;
    const fieldWrapper = frm.get_field("supplier_grade").$wrapper;

    fieldWrapper.find(".supplier-grade-badge").remove();

    if (!grade) return;

    const config = getGradeBadgeConfig(grade);
    if (!config) return;

    const badge = $(
        `<span class="supplier-grade-badge indicator ${config.cssClass}" style="margin-left: 8px; font-size: 12px; padding: 2px 8px; border-radius: 4px; background: ${config.color}; color: #fff;">${config.label}</span>`
    );

    fieldWrapper.find(".control-value").append(badge);
}

/**
 * Returns the badge configuration object for a given Supplier Grade value.
 * Returns null for unrecognised grade strings.
 *
 * @param {string} grade - The Supplier Grade value ("Green", "Yellow", or "Red").
 * @returns {Object|null} Config with cssClass, color, and label properties, or null.
 */
function getGradeBadgeConfig(grade) {
    const configs = {
        Green:  { cssClass: "green",  color: "#28a745", label: "Approved" },
        Yellow: { cssClass: "orange", color: "#ffc107", label: "Conditional" },
        Red:    { cssClass: "red",    color: "#dc3545", label: "Restricted" },
    };
    return configs[grade] || null;
}

/**
 * Toggles the mandatory property of Grade Effective From.
 * The field becomes mandatory when any Supplier Grade is selected
 * and optional again when the grade is cleared.
 *
 * @param {Object} frm - The current Frappe form instance.
 */
function toggleGradeEffectiveFromMandatory(frm) {
    const isGradeSet = Boolean(frm.doc.supplier_grade);
    frm.set_df_property("grade_effective_from", "reqd", isGradeSet ? 1 : 0);
    frm.refresh_field("grade_effective_from");
}
