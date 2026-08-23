# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

import unittest
from unittest.mock import MagicMock, patch

import frappe

from claude_app.claude_app.customization.buying_grade_utils import (
    block_yellow_submit_without_approval,
    validate_supplier_grade_on_transaction,
)
from claude_app.claude_app.customization.supplier.supplier_grade_utils import (
    validate_grade_effective_dates,
    validate_grade_effective_from,
)


class TestSupplierGradeValidation(unittest.TestCase):
    """
    Unit tests for supplier grade field validation on the Supplier master.

    Tests cover: mandatory Grade Effective From, date range validation.
    """

    def _make_supplier_doc(self, grade=None, effective_from=None, effective_to=None):
        """
        Build a minimal mock Supplier document for testing.

        Parameters:
            grade (str, optional): The supplier_grade value.
            effective_from (str, optional): ISO date for grade_effective_from.
            effective_to (str, optional): ISO date for grade_effective_to.

        Returns:
            MagicMock: A mock Frappe Document with the specified field values.
        """
        doc = MagicMock()
        doc.get.side_effect = lambda key, default=None: {
            "supplier_grade": grade,
            "grade_effective_from": effective_from,
            "grade_effective_to": effective_to,
        }.get(key, default)
        doc.supplier_grade = grade
        doc.grade_effective_from = effective_from
        doc.grade_effective_to = effective_to
        return doc

    def test_tc01_grade_effective_from_mandatory_when_grade_set(self):
        """
        TC-01 [regression]: Grade Effective From is mandatory when grade is set.

        Given: supplier_grade = "Green" and grade_effective_from is blank.
        When:  validate_grade_effective_from is called.
        Then:  frappe.ValidationError is raised.
        """
        doc = self._make_supplier_doc(grade="Green", effective_from=None)
        with self.assertRaises(frappe.ValidationError):
            validate_grade_effective_from(doc)

    def test_tc02_grade_effective_from_not_required_when_no_grade(self):
        """
        TC-02 [happy_path]: No error when grade is blank and effective_from is blank.

        Given: supplier_grade is None and grade_effective_from is None.
        When:  validate_grade_effective_from is called.
        Then:  No exception is raised.
        """
        doc = self._make_supplier_doc(grade=None, effective_from=None)
        validate_grade_effective_from(doc)

    def test_tc03_effective_to_before_effective_from_raises_error(self):
        """
        TC-03 [negative]: Grade Effective To cannot precede Grade Effective From.

        Given: grade_effective_from = 2025-01-01, grade_effective_to = 2024-12-31.
        When:  validate_grade_effective_dates is called.
        Then:  frappe.ValidationError is raised.
        """
        doc = self._make_supplier_doc(
            grade="Green",
            effective_from="2025-01-01",
            effective_to="2024-12-31",
        )
        with self.assertRaises(frappe.ValidationError):
            validate_grade_effective_dates(doc)

    def test_tc04_effective_to_after_effective_from_passes(self):
        """
        TC-04 [happy_path]: No error when effective_to is after effective_from.

        Given: grade_effective_from = 2025-01-01, grade_effective_to = 2025-12-31.
        When:  validate_grade_effective_dates is called.
        Then:  No exception is raised.
        """
        doc = self._make_supplier_doc(
            grade="Green",
            effective_from="2025-01-01",
            effective_to="2025-12-31",
        )
        validate_grade_effective_dates(doc)


class TestBuyingGradeTransactionValidation(unittest.TestCase):
    """
    Unit tests for buying transaction grade enforcement (validate + before_submit).

    Tests cover: Red block, Yellow workflow gate, ungraded warning passthrough,
    Green passthrough.
    """

    def _make_transaction_doc(self, supplier="TEST-SUP", supplier_grade=None, workflow_state=None, doctype="Purchase Order"):
        """
        Build a minimal mock buying transaction document.

        Parameters:
            supplier (str, optional): The supplier name.
            supplier_grade (str, optional): Pre-set grade (bypasses DB fetch in some tests).
            workflow_state (str, optional): The current workflow_state.
            doctype (str, optional): The document type name.

        Returns:
            MagicMock: A mock Frappe Document.
        """
        doc = MagicMock()
        doc.supplier = supplier
        doc.supplier_grade = supplier_grade
        doc.workflow_state = workflow_state
        doc.doctype = doctype
        doc.get.side_effect = lambda key, default=None: {
            "supplier": supplier,
            "supplier_grade": supplier_grade,
            "workflow_state": workflow_state,
        }.get(key, default)
        return doc

    @patch("claude_app.claude_app.customization.buying_grade_utils.get_supplier_grade", return_value="Red")
    def test_tc05_red_supplier_blocks_save(self, _mock_get_grade):
        """
        TC-05 [regression]: Red supplier blocks save with correct error.

        Given: Supplier grade is Red.
        When:  validate_supplier_grade_on_transaction is called.
        Then:  frappe.ValidationError is raised.
        """
        doc = self._make_transaction_doc()
        with self.assertRaises(frappe.ValidationError):
            validate_supplier_grade_on_transaction(doc)

    @patch("claude_app.claude_app.customization.buying_grade_utils.get_supplier_grade", return_value="Green")
    def test_tc06_green_supplier_allows_save(self, _mock_get_grade):
        """
        TC-06 [happy_path]: Green supplier allows save without error.

        Given: Supplier grade is Green.
        When:  validate_supplier_grade_on_transaction is called.
        Then:  No exception is raised and doc.supplier_grade is set to "Green".
        """
        doc = self._make_transaction_doc()
        validate_supplier_grade_on_transaction(doc)
        self.assertEqual(doc.supplier_grade, "Green")

    def test_tc07_yellow_po_blocked_without_approval(self):
        """
        TC-07 [regression]: Yellow PO submit is blocked when not in Approved state.

        Given: supplier_grade = Yellow, workflow_state = Pending Approval.
        When:  block_yellow_submit_without_approval is called.
        Then:  frappe.ValidationError is raised.
        """
        doc = self._make_transaction_doc(
            supplier_grade="Yellow",
            workflow_state="Pending Approval",
        )
        with self.assertRaises(frappe.ValidationError):
            block_yellow_submit_without_approval(doc)

    def test_tc08_yellow_po_allowed_when_approved(self):
        """
        TC-08 [happy_path]: Yellow PO submit is allowed when workflow state is Approved.

        Given: supplier_grade = Yellow, workflow_state = Approved.
        When:  block_yellow_submit_without_approval is called.
        Then:  No exception is raised.
        """
        doc = self._make_transaction_doc(
            supplier_grade="Yellow",
            workflow_state="Approved",
        )
        block_yellow_submit_without_approval(doc)

    @patch("claude_app.claude_app.customization.buying_grade_utils.get_supplier_grade", return_value="")
    def test_tc09_ungraded_supplier_does_not_block_save(self, _mock_get_grade):
        """
        TC-09 [edge_case]: Ungraded supplier does not raise a ValidationError on save.

        Given: Supplier has no grade configured (empty string).
        When:  validate_supplier_grade_on_transaction is called.
        Then:  No exception is raised (warning is client-side only).
        """
        doc = self._make_transaction_doc()
        validate_supplier_grade_on_transaction(doc)


if __name__ == "__main__":
    unittest.main()
