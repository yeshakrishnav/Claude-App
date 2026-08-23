# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

"""
Shared procurement grade enforcement helpers used by all five buying
transaction doc_events customisation files.

Enforcement layers:
- validate_supplier_grade_on_transaction: blocks Red suppliers on save
  (server-side authoritative gate for all 5 DocTypes).
- block_yellow_submit_without_approval: blocks Yellow PO/SQ submit when
  the workflow has not yet reached the Approved state.
"""

import frappe

from claude_app.claude_app.customization.supplier.supplier_grade_utils import (
    SUPPLIER_GRADE_RED,
    SUPPLIER_GRADE_YELLOW,
    get_supplier_grade,
)

APPROVED_WORKFLOW_STATE = "Approved"


def validate_supplier_grade_on_transaction(doc):
    """
    Server-side validate hook shared by all five buying transaction DocTypes.

    Fetches the current supplier grade and:
    - Throws a ValidationError if the grade is Red (blocks save and submit).
    - Stores the fetched grade into doc.supplier_grade (read-only field).
    - Does nothing if no supplier is set yet.

    Parameters:
        doc (Document, required): The buying transaction document being validated.

    Returns:
        None
    """
    if not doc.get("supplier"):
        return

    grade = get_supplier_grade(doc.supplier)
    doc.supplier_grade = grade

    if grade == SUPPLIER_GRADE_RED:
        frappe.throw(
            frappe._(
                "This supplier is not approved for procurement. "
                "Please select an approved supplier to proceed."
            ),
            frappe.ValidationError,
        )


def block_yellow_submit_without_approval(doc):
    """
    Server-side before_submit hook for Purchase Order and Supplier Quotation.

    Prevents submission when the supplier grade is Yellow and the document
    workflow has not yet reached the Approved state, directing the user to
    route for approval first.

    Parameters:
        doc (Document, required): The PO or SQ document being submitted.

    Returns:
        None
    """
    if doc.get("supplier_grade") != SUPPLIER_GRADE_YELLOW:
        return

    workflow_state = doc.get("workflow_state") or ""
    if workflow_state != APPROVED_WORKFLOW_STATE:
        frappe.throw(
            frappe._(
                "This {0} cannot be submitted without management approval. "
                "Please route for approval."
            ).format(doc.doctype),
            frappe.ValidationError,
        )
