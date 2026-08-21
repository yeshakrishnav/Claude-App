# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

import unittest
from unittest.mock import MagicMock, patch

import frappe

from claude_app.claude_app.customization.buying.grade_enforcement import (
    enforce_supplier_grade_on_before_submit,
    enforce_supplier_grade_on_validate,
    fetch_supplier_grade,
)
from claude_app.claude_app.customization.supplier.supplier_utils import (
    validate_grade_effective_dates,
)


class TestFetchSupplierGrade(unittest.TestCase):
    """Unit tests for the fetch_supplier_grade helper."""

    @patch("claude_app.claude_app.customization.buying.grade_enforcement.frappe.db.get_value")
    def test_returns_grade_for_valid_supplier(self, mock_get_value):
        """
        TC-HAP-001 [happy_path] Green supplier: fetch_supplier_grade returns
        the grade string from the Supplier master.
        """
        mock_get_value.return_value = "Green"
        result = fetch_supplier_grade("SUP-GREEN-001")
        self.assertEqual(result, "Green")
        mock_get_value.assert_called_once_with("Supplier", "SUP-GREEN-001", "supplier_grade")

    @patch("claude_app.claude_app.customization.buying.grade_enforcement.frappe.db.get_value")
    def test_returns_empty_string_for_ungraded_supplier(self, mock_get_value):
        """
        TC-EDGE-001 [edge_case] Ungraded supplier: fetch_supplier_grade returns
        an empty string when the Supplier master has no grade set.
        """
        mock_get_value.return_value = None
        result = fetch_supplier_grade("SUP-UNGRADED-001")
        self.assertEqual(result, "")

    def test_returns_empty_string_for_no_supplier_name(self):
        """
        TC-EDGE-002 [edge_case] No supplier name: fetch_supplier_grade returns
        an empty string without touching the database.
        """
        result = fetch_supplier_grade("")
        self.assertEqual(result, "")


class TestEnforceSupplierGradeOnValidate(unittest.TestCase):
    """Unit tests for enforce_supplier_grade_on_validate."""

    def _make_doc(self, supplier, grade_from_db):
        """
        Build a minimal mock document for a buying transaction.

        Parameters:
            supplier (str, required): The supplier name to set on the doc.
            grade_from_db (str, required): The grade that frappe.db.get_value will return.

        Returns:
            MagicMock: A mock Document object with get() and set attribute support.
        """
        doc = MagicMock()
        doc.get.side_effect = lambda key: {"supplier": supplier}.get(key, "")
        return doc

    @patch("claude_app.claude_app.customization.buying.grade_enforcement.frappe.db.get_value")
    @patch("claude_app.claude_app.customization.buying.grade_enforcement.frappe.throw")
    def test_red_supplier_raises_validation_error(self, mock_throw, mock_get_value):
        """
        TC-REG-001 [regression] Red supplier: validate hook calls frappe.throw,
        blocking the document save.
        """
        mock_get_value.return_value = "Red"
        doc = self._make_doc("SUP-RED-001", "Red")

        enforce_supplier_grade_on_validate(doc)

        mock_throw.assert_called_once()
        call_args = mock_throw.call_args[0][0]
        self.assertIn("not approved for procurement", call_args)

    @patch("claude_app.claude_app.customization.buying.grade_enforcement.frappe.db.get_value")
    @patch("claude_app.claude_app.customization.buying.grade_enforcement.frappe.throw")
    @patch("claude_app.claude_app.customization.buying.grade_enforcement.frappe.msgprint")
    def test_green_supplier_allows_save(self, mock_msgprint, mock_throw, mock_get_value):
        """
        TC-HAP-002 [happy_path] Green supplier: validate hook does not throw
        and does not show any message.
        """
        mock_get_value.return_value = "Green"
        doc = self._make_doc("SUP-GREEN-001", "Green")

        enforce_supplier_grade_on_validate(doc)

        mock_throw.assert_not_called()
        mock_msgprint.assert_not_called()

    @patch("claude_app.claude_app.customization.buying.grade_enforcement.frappe.db.get_value")
    @patch("claude_app.claude_app.customization.buying.grade_enforcement.frappe.throw")
    @patch("claude_app.claude_app.customization.buying.grade_enforcement.frappe.msgprint")
    def test_ungraded_supplier_shows_warning_not_blocked(self, mock_msgprint, mock_throw, mock_get_value):
        """
        TC-EDGE-003 [edge_case] Ungraded supplier: validate hook shows a warning
        via msgprint but does NOT call frappe.throw (user is not blocked).
        """
        mock_get_value.return_value = None
        doc = self._make_doc("SUP-UNGRADED-001", "")

        enforce_supplier_grade_on_validate(doc)

        mock_throw.assert_not_called()
        mock_msgprint.assert_called_once()


class TestEnforceSupplierGradeOnBeforeSubmit(unittest.TestCase):
    """Unit tests for enforce_supplier_grade_on_before_submit."""

    @patch("claude_app.claude_app.customization.buying.grade_enforcement.frappe.throw")
    def test_yellow_without_approval_blocks_submit(self, mock_throw):
        """
        TC-NEG-001 [negative] Yellow supplier without approval: before_submit
        calls frappe.throw, blocking submission.
        """
        doc = MagicMock()
        doc.get.side_effect = lambda key: {
            "supplier_grade": "Yellow",
            "workflow_state": "Pending Approval",
            "supplier": "SUP-YELLOW-001",
        }.get(key, "")
        doc.doctype = "Purchase Order"

        enforce_supplier_grade_on_before_submit(doc)

        mock_throw.assert_called_once()

    @patch("claude_app.claude_app.customization.buying.grade_enforcement.frappe.throw")
    def test_yellow_with_approval_allows_submit(self, mock_throw):
        """
        TC-HAP-003 [happy_path] Yellow supplier with Approved workflow state:
        before_submit does NOT block submission.
        """
        doc = MagicMock()
        doc.get.side_effect = lambda key: {
            "supplier_grade": "Yellow",
            "workflow_state": "Approved",
            "supplier": "SUP-YELLOW-001",
        }.get(key, "")
        doc.doctype = "Purchase Order"

        enforce_supplier_grade_on_before_submit(doc)

        mock_throw.assert_not_called()


class TestValidateGradeEffectiveDates(unittest.TestCase):
    """Unit tests for Supplier master date validation."""

    @patch("claude_app.claude_app.customization.supplier.supplier_utils.frappe.throw")
    def test_grade_without_effective_from_raises_error(self, mock_throw):
        """
        TC-EDGE-004 [edge_case] Grade Effective From missing when grade is set:
        validate raises a frappe.throw error.
        """
        doc = MagicMock()
        doc.get.side_effect = lambda key: {
            "supplier_grade": "Green",
            "grade_effective_from": "",
            "grade_effective_to": "",
        }.get(key, "")

        validate_grade_effective_dates(doc)

        mock_throw.assert_called_once()

    @patch("claude_app.claude_app.customization.supplier.supplier_utils.frappe.throw")
    def test_grade_effective_to_before_from_raises_error(self, mock_throw):
        """
        TC-EDGE-005 [edge_case] Grade Effective To earlier than Grade Effective From:
        validate raises a frappe.throw error.
        """
        doc = MagicMock()
        doc.get.side_effect = lambda key: {
            "supplier_grade": "Green",
            "grade_effective_from": "2025-06-01",
            "grade_effective_to": "2025-01-01",
        }.get(key, "")

        validate_grade_effective_dates(doc)

        mock_throw.assert_called_once()
        call_args = mock_throw.call_args[0][0]
        self.assertIn("Grade Effective To cannot be earlier", call_args)
