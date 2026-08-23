# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

from claude_app.claude_app.customization.buying_grade_utils import (
    block_yellow_submit_without_approval,
    validate_supplier_grade_on_transaction,
)


def validate(doc, method):
    """
    doc_events validate hook for Supplier Quotation.

    Fetches the supplier's current grade and blocks save if the grade is Red.

    Parameters:
        doc (Document, required): The Supplier Quotation document being validated.
        method (str, required): The Frappe hook event name.

    Returns:
        None
    """
    validate_supplier_grade_on_transaction(doc)


def before_submit(doc, method):
    """
    doc_events before_submit hook for Supplier Quotation.

    Blocks submission of a Yellow-grade supplier SQ that has not been
    approved through the configured workflow.

    Parameters:
        doc (Document, required): The Supplier Quotation document being submitted.
        method (str, required): The Frappe hook event name.

    Returns:
        None
    """
    block_yellow_submit_without_approval(doc)
