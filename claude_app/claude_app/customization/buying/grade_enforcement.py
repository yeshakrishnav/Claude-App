# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

import frappe
from frappe import _

# Workflow states that indicate Yellow-supplier approval has been granted.
APPROVED_WORKFLOW_STATES = {"Approved"}

# Buying transaction DocTypes that carry a supplier_grade field.
BUYING_TRANSACTION_DOCTYPES = {
    "Purchase Order",
    "Purchase Invoice",
    "Purchase Receipt",
    "Request for Quotation",
    "Supplier Quotation",
}


def fetch_supplier_grade(supplier_name):
    """
    Fetch the current Supplier Grade from the Supplier master.

    Returns an empty string when the supplier does not exist or has no grade
    configured, so callers can treat it as the "ungraded" case without
    raising an exception.

    Parameters:
        supplier_name (str, required): The Supplier document name.

    Returns:
        str: The Supplier Grade value ("Green", "Yellow", "Red") or "".
    """
    if not supplier_name:
        return ""

    grade = frappe.db.get_value("Supplier", supplier_name, "supplier_grade")
    return grade or ""


def enforce_supplier_grade_on_validate(doc):
    """
    Enforce Supplier Grade procurement rules during document validation.

    - Fetches the current grade from the Supplier master and stores it on the
      document's read-only supplier_grade field.
    - Raises frappe.ValidationError if the grade is Red, blocking save and submit.
    - Shows a non-blocking warning message for Yellow or ungraded suppliers.

    This function is the authoritative server-side gate and must be called from
    every buying transaction DocType's validate hook.

    Parameters:
        doc (Document, required): The buying transaction document being validated.

    Returns:
        None
    """
    supplier_name = doc.get("supplier")
    if not supplier_name:
        return

    grade = fetch_supplier_grade(supplier_name)

    # Persist grade on the transaction (read-only field, set server-side).
    doc.supplier_grade = grade

    if grade == "Red":
        frappe.throw(
            _(
                "This supplier is not approved for procurement. "
                "Please select an approved supplier to proceed."
            ),
            title=_("Restricted Supplier"),
        )

    elif grade == "Yellow":
        frappe.msgprint(
            _(
                "This supplier requires management approval. "
                "The transaction will be routed for approval before it can be submitted."
            ),
            title=_("Conditional Supplier — Approval Required"),
            indicator="orange",
            alert=True,
        )

    elif not grade:
        frappe.msgprint(
            _(
                "No procurement grade is assigned to this supplier. "
                "Please configure the supplier grade before proceeding."
            ),
            title=_("Ungraded Supplier"),
            indicator="yellow",
            alert=True,
        )


def enforce_supplier_grade_on_before_submit(doc):
    """
    Enforce Yellow-supplier workflow approval gate before document submission.

    Raises frappe.ValidationError if the supplier grade is Yellow and the
    document's workflow_state is not one of the APPROVED_WORKFLOW_STATES.
    This function should only be called from DocTypes that have the Yellow
    Supplier approval workflow configured (Purchase Order, Supplier Quotation).

    Parameters:
        doc (Document, required): The buying transaction document being submitted.

    Returns:
        None
    """
    grade = doc.get("supplier_grade") or fetch_supplier_grade(doc.get("supplier"))

    if grade == "Yellow":
        workflow_state = doc.get("workflow_state") or ""
        if workflow_state not in APPROVED_WORKFLOW_STATES:
            frappe.throw(
                _(
                    "This {0} cannot be submitted without management approval. "
                    "Please route for approval."
                ).format(doc.doctype),
                title=_("Approval Required"),
            )
