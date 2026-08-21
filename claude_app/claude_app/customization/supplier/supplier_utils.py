# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

import frappe
from frappe import _
from frappe.utils import getdate


def validate_grade_effective_dates(doc):
    """
    Validate supplier grade effective date constraints on the Supplier master.

    Raises frappe.ValidationError if:
      - A Supplier Grade is set but Grade Effective From is blank.
      - Grade Effective To is earlier than Grade Effective From.

    Parameters:
        doc (Document, required): The Supplier document being validated.

    Returns:
        None
    """
    supplier_grade = doc.get("supplier_grade")
    grade_effective_from = doc.get("grade_effective_from")
    grade_effective_to = doc.get("grade_effective_to")

    if supplier_grade and not grade_effective_from:
        frappe.throw(
            _("Grade Effective From is mandatory when Supplier Grade is set."),
            title=_("Missing Required Field"),
        )

    if grade_effective_from and grade_effective_to:
        if getdate(grade_effective_to) < getdate(grade_effective_from):
            frappe.throw(
                _("Grade Effective To cannot be earlier than Grade Effective From."),
                title=_("Invalid Date Range"),
            )
