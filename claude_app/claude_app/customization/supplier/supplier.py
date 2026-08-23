# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

from claude_app.claude_app.customization.supplier.supplier_grade_utils import (
    validate_grade_effective_dates,
    validate_grade_effective_from,
)


def validate(doc, method):
    """
    doc_events hook fired on Supplier validate.

    Delegates grade field validation to supplier_grade_utils:
    1. Grade Effective From is mandatory when grade is set.
    2. Grade Effective To must not precede Grade Effective From.

    Parameters:
        doc (Document, required): The Supplier document being validated.
        method (str, required): The Frappe hook event name.

    Returns:
        None
    """
    validate_grade_effective_from(doc)
    validate_grade_effective_dates(doc)
