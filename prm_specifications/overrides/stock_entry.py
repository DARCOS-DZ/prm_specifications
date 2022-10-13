from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry
import frappe
from erpnext.stock.utils import get_or_make_bin


class CustomStockEntry(StockEntry):
    def validate_finished_goods(self):
        """
        1. Check if FG exists (mfg, repack)
        2. Check if Multiple FG Items are present (mfg)
        3. Check FG Item and Qty against WO if present (mfg)
        """
        production_item, wo_qty, finished_items = None, 0, []

        wo_details = frappe.db.get_value("Work Order", self.work_order, ["production_item", "qty"])
        if wo_details:
            production_item, wo_qty = wo_details

        for d in self.get("items"):
            if d.is_finished_item:
                if not self.work_order:
					# Independent MFG Entry/ Repack Entry, no WO to match against
                    finished_items.append(d.item_code)
                    continue

                if d.item_code != production_item:
                    frappe.throw(
                        ("Finished Item {0} does not match with Work Order {1}").format(
                            d.item_code, self.work_order
                        )
                    )
                elif flt(d.transfer_qty) > flt(self.fg_completed_qty):
                    frappe.throw(
                        _("Quantity in row {0} ({1}) must be same as manufactured quantity {2}").format(
                            d.idx, d.transfer_qty, self.fg_completed_qty
                        )
                    )

                finished_items.append(d.item_code)

        if not finished_items:
            frappe.throw(
                msg=_("There must be atleast 1 Finished Good in this Stock Entry").format(self.name),
                title=_("Missing Finished Good"),
                exc=FinishedGoodError,
            )
            # remove multiple finished items restriction
            # if self.purpose == "Manufacture":
            # 	if len(set(finished_items)) > 1:
            # 		frappe.throw(
            # 			msg=_("Multiple items cannot be marked as finished item"),
            # 			title=_("Note"),
            # 			exc=FinishedGoodError,
            # 		)

            allowance_percentage = flt(
                frappe.db.get_single_value(
                    "Manufacturing Settings", "overproduction_percentage_for_work_order"
                )
            )
            allowed_qty = wo_qty + ((allowance_percentage / 100) * wo_qty)

            # No work order could mean independent Manufacture entry, if so skip validation
            if self.work_order and self.fg_completed_qty > allowed_qty:
                frappe.throw(
                    _("For quantity {0} should not be greater than allowed quantity {1}").format(
                        flt(self.fg_completed_qty), allowed_qty
                    )
                )
