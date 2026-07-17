# Copyright (c) 2026, yeshakrishnav and contributors
# For license information, please see license.txt

"""Sales Invoice override for claude_app.

Applies the custom field ``custom_additional_discount`` to the invoice
``grand_total`` during validation so that the stored total reflects the
additional discount entered by the user.
"""

import frappe


def apply_custom_discount(doc, method=None):
    """Subtract ``custom_additional_discount`` from ``grand_total``.

    Called on the ``validate`` event of Sales Invoice.  If the custom
    field is absent or zero the function is a no-op, so existing invoices
    are unaffected.

    Args:
        doc:    The Sales Invoice document being validated.
        method: Event name passed by Frappe (unused, kept for signature
                compatibility).
    """
    discount = frappe.utils.flt(doc.get("custom_additional_discount"))
    if not discount:
        return

    doc.grand_total = frappe.utils.flt(doc.grand_total) - discount
    doc.rounded_total = frappe.utils.flt(
        doc.get("rounded_total") or doc.grand_total
    ) - discount
    doc.base_grand_total = frappe.utils.flt(
        doc.get("base_grand_total") or doc.grand_total
    ) - discount
    doc.base_rounded_total = frappe.utils.flt(
        doc.get("base_rounded_total") or doc.base_grand_total
    ) - discount
    doc.outstanding_amount = frappe.utils.flt(
        doc.get("outstanding_amount") or doc.grand_total
    ) - discount
