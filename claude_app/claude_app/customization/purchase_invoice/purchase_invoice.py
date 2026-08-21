# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

from claude_app.claude_app.customization.buying.grade_enforcement import (
    enforce_supplier_grade_on_validate,
)


def validate(doc, method):
    """
    Hook fired on Purchase Invoice validate. Enforces supplier grade procurement rules.

    Fetches the supplier's current grade, persists it to the read-only
    supplier_grade field, blocks Red-grade suppliers, and warns for Yellow
    or ungraded suppliers.

    Parameters:
        doc (Document, required): The Purchase Invoice document being validated.
        method (str, required): The hook event name passed by Frappe.

    Returns:
        None
    """
    enforce_supplier_grade_on_validate(doc)
