# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

from claude_app.claude_app.customization.supplier.supplier_utils import (
    validate_grade_effective_dates,
)


def validate(doc, method):
    """
    Hook fired on Supplier save. Enforces procurement grade field constraints.

    Validates that Grade Effective From is populated when a Supplier Grade
    is set, and that Grade Effective To is not earlier than Grade Effective From.

    Parameters:
        doc (Document, required): The Supplier document being validated.
        method (str, required): The hook event name passed by Frappe.

    Returns:
        None
    """
    validate_grade_effective_dates(doc)
