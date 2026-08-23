# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

import frappe


SUPPLIER_GRADE_GREEN = "Green"
SUPPLIER_GRADE_YELLOW = "Yellow"
SUPPLIER_GRADE_RED = "Red"


def validate_grade_effective_from(doc):
    """
    Enforce that Grade Effective From is mandatory when Supplier Grade is set.

    Raises frappe.ValidationError if supplier_grade is set but
    grade_effective_from is blank.

    Parameters:
        doc (Document, required): The Supplier document being saved.

    Returns:
        None
    """
    if doc.get("supplier_grade") and not doc.get("grade_effective_from"):
        frappe.throw(
            frappe._("Grade Effective From is mandatory when Supplier Grade is set."),
            frappe.ValidationError,
        )


def validate_grade_effective_dates(doc):
    """
    Ensure Grade Effective To is not earlier than Grade Effective From.

    Only validates when both date fields are populated on the Supplier master.

    Parameters:
        doc (Document, required): The Supplier document being saved.

    Returns:
        None
    """
    if not doc.get("grade_effective_from") or not doc.get("grade_effective_to"):
        return

    if doc.grade_effective_to < doc.grade_effective_from:
        frappe.throw(
            frappe._("Grade Effective To cannot be earlier than Grade Effective From."),
            frappe.ValidationError,
        )


def get_supplier_grade(supplier_name):
    """
    Fetch the current Supplier Grade for a given supplier from the database.

    Returns an empty string if the supplier has no grade configured.

    Parameters:
        supplier_name (str, required): The name (primary key) of the Supplier document.

    Returns:
        str: The supplier_grade value ("Green", "Yellow", "Red", or "").
    """
    return (
        frappe.db.get_value("Supplier", supplier_name, "supplier_grade") or ""
    )
