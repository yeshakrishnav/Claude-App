# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

from claude_app.claude_app.customization.buying_grade_utils import (
    validate_supplier_grade_on_transaction,
)


def validate(doc, method):
    """
    doc_events validate hook for Request for Quotation.

    Fetches the supplier's current grade and blocks save if the grade is Red.
    Note: RFQ stores suppliers in a child table (rfq_suppliers); this hook
    checks doc.supplier if present (single-supplier mode) and is a no-op
    when no supplier field exists at root level.

    Parameters:
        doc (Document, required): The Request for Quotation document being validated.
        method (str, required): The Frappe hook event name.

    Returns:
        None
    """
    validate_supplier_grade_on_transaction(doc)
