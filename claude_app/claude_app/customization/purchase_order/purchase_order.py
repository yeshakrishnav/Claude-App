# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

from claude_app.claude_app.customization.buying.grade_enforcement import (
    enforce_supplier_grade_on_before_submit,
    enforce_supplier_grade_on_validate,
)


def validate(doc, method):
    """
    Hook fired on Purchase Order validate. Enforces supplier grade procurement rules.

    Fetches the supplier's current grade, persists it to the read-only
    supplier_grade field, blocks Red-grade suppliers with a ValidationError,
    and warns for Yellow or ungraded suppliers.

    Parameters:
        doc (Document, required): The Purchase Order document being validated.
        method (str, required): The hook event name passed by Frappe.

    Returns:
        None
    """
    enforce_supplier_grade_on_validate(doc)


def before_submit(doc, method):
    """
    Hook fired before Purchase Order submission. Enforces Yellow-supplier workflow gate.

    Blocks submission when the supplier grade is Yellow and the document has not
    been approved through the configured Yellow Supplier PO Approval workflow.

    Parameters:
        doc (Document, required): The Purchase Order document being submitted.
        method (str, required): The hook event name passed by Frappe.

    Returns:
        None
    """
    enforce_supplier_grade_on_before_submit(doc)
