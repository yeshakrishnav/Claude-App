# Copyright (c) 2026, yeshakrishnav and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class NewUser(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		address_line_1: DF.Data | None
		address_line_2: DF.Data | None
		city: DF.Data | None
		country: DF.Link | None
		date_of_birth: DF.Date | None
		email: DF.Data
		full_name: DF.Data
		gender: DF.Literal["", "Male", "Female", "Non-Binary", "Prefer not to say"]
		phone: DF.Data | None
		pincode: DF.Data | None
		state: DF.Data | None
	# end: auto-generated types

	def validate(self):
		self.validate_email()

	def validate_email(self):
		"""Ensure the email address is in a valid format."""
		if self.email:
			frappe.utils.validate_email_address(self.email, throw=True)
