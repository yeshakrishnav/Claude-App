# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

from claude_app.claude_app.customization.buying.grade_enforcement import (
    enforce_supplier_grade_on_validate,
)


def validate(doc, method):
    """
    Hook fired on Request for Quotation validate. Enforces supplier grade procurement rules.

    Fetches the supplier's current grade from the first supplier row in the
    suppliers child table, persists it, blocks Red-grade suppliers, and warns
    for Yellow or ungraded suppliers.

    Note: RFQ uses a Supplier child table (rfq_suppliers) rather than a direct
    supplier field. Grade is evaluated against the first supplier in the list;
    multi-supplier RFQs may be extended in a future CR.

    Parameters:
        doc (Document, required): The Request for Quotation document being validated.
        method (str, required): The hook event name passed by Frappe.

    Returns:
        None
    """
    enforce_supplier_grade_on_validate(doc)
