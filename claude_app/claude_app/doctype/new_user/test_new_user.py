# Copyright (c) 2026, yeshakrishnav and Contributors
# See license.txt for license information

import frappe
from frappe.tests.utils import FrappeTestCase


class TestNewUser(FrappeTestCase):
	"""Tests for the New User DocType."""

	def setUp(self):
		"""Clean up any leftover test records before each test."""
		frappe.db.delete("New User", {"email": "testuser@example.com"})
		frappe.db.commit()

	def _make_user(self, **kwargs):
		"""Helper: create and insert a New User document."""
		defaults = {
			"doctype": "New User",
			"full_name": "Test User",
			"email": "testuser@example.com",
			"phone": "9876543210",
			"gender": "Male",
		}
		defaults.update(kwargs)
		doc = frappe.get_doc(defaults)
		doc.insert(ignore_permissions=True)
		return doc

	def test_create_new_user(self):
		"""A New User record can be created with required fields."""
		doc = self._make_user()
		self.assertEqual(doc.full_name, "Test User")
		self.assertEqual(doc.email, "testuser@example.com")

	def test_email_is_required(self):
		"""Creating a New User without an email must raise a MandatoryError."""
		with self.assertRaises(frappe.exceptions.MandatoryError):
			self._make_user(email="")

	def test_invalid_email_raises(self):
		"""An invalid email address must be rejected during validate."""
		with self.assertRaises(frappe.exceptions.ValidationError):
			self._make_user(email="not-an-email")

	def test_full_name_is_required(self):
		"""Creating a New User without a full name must raise a MandatoryError."""
		with self.assertRaises(frappe.exceptions.MandatoryError):
			self._make_user(full_name="")

	def tearDown(self):
		"""Remove any records created during the test."""
		frappe.db.delete("New User", {"email": "testuser@example.com"})
		frappe.db.commit()
