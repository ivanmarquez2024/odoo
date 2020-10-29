# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import base64
from codecs import BOM_UTF8

from odoo import _, api, models,fields

BOM_UTF8U = BOM_UTF8.decode('UTF-8')
CFDI_SAT_QR_STATE = {
    'No Encontrado': 'not_found',
    'Cancelado': 'cancelled',
    'Vigente': 'valid',
}
# mapping invoice type to journal type
TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale',
    'in_refund': 'purchase',
}

# mapping invoice type to refund type
TYPE2REFUND = {
    'out_invoice': 'out_refund',        # Customer Invoice
    'in_invoice': 'in_refund',          # Vendor Bill
    'out_refund': 'out_invoice',        # Customer Credit Note
    'in_refund': 'in_invoice',          # Vendor Credit Note
}

MAGIC_COLUMNS = ('id', 'create_uid', 'create_date', 'write_uid', 'write_date')


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    move_name = fields.Char(string='Journal Entry Name', readonly=True,default=False, copy=False)

    def generate_xml_attachment(self):
        version = self.l10n_mx_edi_get_pac_version()
        for inv in self:
            cfdi_values = inv._l10n_mx_edi_create_cfdi()
            error = cfdi_values.pop('error', None)
            cfdi = cfdi_values.pop('cfdi', None)
            if error:
                # cfdi failed to be generated
                inv.l10n_mx_edi_pac_status = 'retry'
                inv.message_post(body=error, subtype='account.mt_invoice_validated')
                continue
            # cfdi has been successfully generated
            inv.l10n_mx_edi_pac_status = 'to_sign'
            filename = ('%s-%s-MX-Invoice-%s.xml' % (
                inv.journal_id.code, inv.name, version.replace('.', '-'))).replace('/', '')
            ctx = self.env.context.copy()
            ctx.pop('default_type', False)
            inv.l10n_mx_edi_cfdi_name = filename
            attachment_id = self.env['ir.attachment'].with_context(ctx).create({
                'name': filename,
                'res_id': inv.id,
                'res_model': inv._name,
                'datas': base64.encodestring(cfdi),
                'description': 'Mexican invoice',
                })
            inv.message_post(
                body=_('CFDI document generated (may be not signed)'),
                attachment_ids=[attachment_id.id],
                subtype='account.mt_invoice_validated')
            inv._l10n_mx_edi_sign()

    def create_adjustment_line(self, xml_amount):
        """If the invoice has difference with the total in the CFDI is
        generated a new line with that adjustment if is found the account to
        assign in this lines. The account is assigned in a system parameter
        called 'adjustment_line_account_MX'"""
        account_id = self.env['ir.config_parameter'].sudo().get_param(
            'adjustment_line_account_MX', '')
        if not account_id:
            return False
        self.invoice_line_ids.create({
            'account_id': account_id,
            'name': _('Adjustment line'),
            'quantity': 1,
            'price_unit': xml_amount - self.amount_total,
            'invoice_id': self.id,
        })
        return True

    def action_invoice_open(self):
        """Sync SAT status if not set yet"""
        res = super(AccountInvoice, self).action_invoice_open()
        vendor_bills = self.filtered(
            lambda inv:
            inv.type in ('in_invoice', 'in_refund')
            and inv.l10n_mx_edi_cfdi_name)
        vendor_bills.l10n_mx_edi_update_sat_status()
        return res

    def action_invoice_draft(self):
        """Reset SAT status when a vendor bill is reset to draft"""
        res = super(AccountInvoice, self).action_invoice_draft()
        # not using is_required since it doesn't take into account vendor bills
        vendor_bills = self.filtered(
            lambda x:
            x.type in ('in_invoice', 'in_refund')
            and x.l10n_mx_edi_sat_status != 'undefined')
        vendor_bills.write({'l10n_mx_edi_sat_status': 'undefined'})
        return res

    @api.model
    def _default_journal(self):
        if self._context.get('default_journal_id', False):
            return self.env['account.journal'].browse(self._context.get('default_journal_id'))
        inv_type = self._context.get('type', 'out_invoice')
        inv_types = inv_type if isinstance(inv_type, list) else [inv_type]
        company_id = self._context.get('company_id', self.env.user.company_id.id)
        domain = [
            ('type', 'in', [TYPE2JOURNAL[ty] for ty in inv_types if ty in TYPE2JOURNAL]),
            ('company_id', '=', company_id),
        ]
        return self.env['account.journal'].search(domain, limit=1)

class AccountInvoice(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def _default_account(self):
        if self._context.get('journal_id'):
            journal = self.env['account.journal'].browse(self._context.get('journal_id'))
            if self._context.get('type') in ('out_invoice', 'in_refund'):
                return journal.default_credit_account_id.id
            return journal.default_debit_account_id.id