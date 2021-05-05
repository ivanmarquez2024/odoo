# See LICENSE file for full copyright and licensing details.

from datetime import date, timedelta
from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange('debit', 'credit', 'currency_id')
    def _onchange_debit_credit(self):
        """
        Method to change amount currency from credit or debit's currency
        to amount's currency .
        """
        for move_line in self:
            context = self._context
            # Trigger onchange when currency selected but amount currency has
            # no value.
            if move_line.currency_id and move_line.move_id.company_id:
                converted_amount = move_line.move_id.company_id.\
                    currency_id.with_context({'date': move_line.date}).\
                    compute(move_line.debit or move_line.credit,
                            move_line.currency_id)
                if move_line.debit:
                    move_line.amount_currency = move_line.currency_id. \
                        round(abs(converted_amount))
                else:
                    if converted_amount > 0:
                        converted_amount = (converted_amount * -1)
                    move_line.amount_currency = move_line.currency_id. \
                        round(converted_amount)


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.depends('amount_residual','invoice_date')
    def _compute_base_residual(self):
        for inv in self:
            if inv.company_id and inv.currency_id and \
               inv.currency_id != inv.company_id.currency_id:
                inv.base_residual = inv.currency_id. \
                    with_context(date=inv.invoice_date or \
                                 fields.Date.context_today(self)). \
                                 compute(inv.amount_residual,
                                         inv.company_id.currency_id)

    forex_entry_id = fields.Many2one('account.move', 'Unrealised Forex Entry',
                                     copy=False, ondelete='restrict')
    forex_rev_entry_id = fields.Many2one('account.move',
                                         'Unrealised Forex Reversal Entry',
                                         copy=False, ondelete='restrict')
    base_residual = fields.Float(string='Base Amount Due',
                                 digits=(16,3),
                                 compute='_compute_base_residual',
                                 store=True)


    def auto_reconcile_entries(self, src_mv, dest_mv):
        '''
            Make Auto Reconciliation for Journal Entries.
        '''
        if src_mv and dest_mv:
            move_concile_ids = [mv_line.id for mv_line in src_mv.line_ids \
                                if mv_line.account_id.internal_type in \
                                ['payable', 'receivable']]
            move_concile_ids += [mv_line.id for mv_line in dest_mv.line_ids \
                                 if mv_line.account_id.internal_type in \
                                 ['payable', 'receivable']]
            if move_concile_ids:
                manual_rec_lines = self.env['account.move.line'].search([
                    ('id', 'in', move_concile_ids)])
                manual_rec_lines and manual_rec_lines.auto_reconcile_lines()

    def invoice_move_entry_create(self, src_ac, dest_ac, move_ref_field,
                                  taken_amount=False, take_amt_cur=True,
                                  entry_date=False, journal=False, rent=False):
        """
            Method to Create Move Entry based on given Accounts.
        """
        if not (src_ac or dest_ac):
            return False
        account_move = self.env['account.move']
        for inv in self:
            ctx = dict(self._context, lang=inv.partner_id.lang)
            invoice_date = entry_date or fields.Date.context_today(self)
            company_currency = inv.company_id.currency_id
            iml = []
            diff_currency = inv.currency_id != company_currency
            price = taken_amount or inv.amount_total
            diff_currency = diff_currency
            if diff_currency:
                converted_amount = company_currency.with_context(
                    {'date': invoice_date}).compute(price, inv.currency_id)

            name = inv.name or '/'
            iml.append({
                'type': 'src',
                'name': name,
                'price': price or 0.0,
                'account_id': src_ac,
                'amount_currency': diff_currency and converted_amount,
                'currency_id': diff_currency and inv.currency_id.id,
                'invoice_id': inv.id
            })
            iml.append({
                'type': 'dest',
                'name': name,
                'price': (-price) or 0.0,
                'account_id': dest_ac,
                'amount_currency': diff_currency and converted_amount,
                'currency_id': diff_currency and inv.currency_id.id,
                'invoice_id': inv.id
            })
            part = self.env['res.partner']._find_accounting_partner(
                inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            journal = journal or inv.journal_id.with_context(ctx)
            move_vals = {
                'ref': inv.invoice_payment_ref or inv.name,
                'line_ids': line,
                'journal_id': journal.id,
                'date': invoice_date,
                'narration': inv.narration,
                'company_id': inv.company_id.id,
                'partner_id': part.id,
            }
            ctx['company_id'] = inv.company_id.id
            ctx['invoice'] = inv
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)
            # make the invoice point to that move
            if move_ref_field:
                inv.with_context(ctx).write({move_ref_field: move.id})
            move.post()
        return True

    def button_cancel(self):
        if self._context.get('default_type') in ('out_invoice', 'in_invoice'):
            moves = self.env['account.move']
            for rec in self:
                if rec.forex_entry_id:
                    moves += rec.forex_entry_id
                    rec.forex_entry_id = False
                if rec.forex_rev_entry_id:
                    moves += rec.forex_rev_entry_id
                    rec.forex_rev_entry_id = False
            res = super(AccountMove, self).button_cancel()
            moves.button_draft()
            moves.with_context(force_delete=True).unlink()
        else:
            res = super(AccountMove, self).button_cancel()
        return res

    def forex_move_entry_create(self, partner_ac, move_ref_field, forex_date):
        """
            Method to Create Forex Move Entry based on given Accounts.
        """
        daily_rate_obj = self.env['res.currency.rate']
        for inv in self:
            for_gain_ac = inv.company_id.unrealised_inc_curr_account_id
            for_loss_ac = inv.company_id.unrealised_exp_curr_account_id

            if not (partner_ac and for_gain_ac and for_loss_ac and forex_date):
                continue
            company_currency = inv.company_id.currency_id
            date1 = forex_date.strftime('%Y-%m-%d')
            forex_date = self._context.get('date') or fields.Date.today()
            comp_cur = daily_rate_obj.search(
                [('name', '=', date1),
                 ('currency_id', '=', company_currency.id)], limit=1)
            inv_cur = daily_rate_obj.search(
                [('name', '<=', date1),
                 ('currency_id', '=', inv.currency_id.id)], limit=1)

            comp_cur_rate = comp_cur and comp_cur.rate or 1
            inv_cur_rate = inv_cur and inv_cur.rate or 1
            # Calculating new price as per forex date.
            new_price = inv.amount_residual * (comp_cur_rate / inv_cur_rate)
            exchage_amt = new_price - inv.base_residual

            src_ac = dest_ac = False
            if partner_ac.internal_type == 'receivable':
                if exchage_amt > 0:
                    src_ac = partner_ac.id
                    dest_ac = for_gain_ac.id
                else:
                    src_ac = for_loss_ac.id
                    dest_ac = partner_ac.id
            elif partner_ac.internal_type == 'payable':
                if exchage_amt > 0:
                    src_ac = for_gain_ac.id
                    dest_ac = partner_ac.id
                else:
                    src_ac = partner_ac.id
                    dest_ac = for_loss_ac.id
            # Find Forex Journal for move entries.
            forex_dom = [('code', '=', 'FOREX'),
                         ('company_id', '=', inv.company_id.id)]
            forex_jrnl = self.env['account.journal'].search(forex_dom, limit=1)
            if src_ac and dest_ac and move_ref_field and exchage_amt:
                inv.invoice_move_entry_create(src_ac, dest_ac, move_ref_field,
                                              abs(exchage_amt), False,
                                              forex_date, forex_jrnl or False,
                                              False)
        return True

    def forex_entry_reversal(self):
        """
            This Method is used to proceed Forex Entry Reversal
        """
        # Reversal of existing Forex entry.
        src_ac = dest_ac = False
        exchage_amt = 0.0
        today = date.today().replace(day=1)

        for mv_line in self.forex_entry_id.line_ids:
            if mv_line.credit:
                src_ac = mv_line.account_id.id
            else:
                dest_ac = mv_line.account_id.id
            exchage_amt = abs(mv_line.debit or mv_line.credit)
        if src_ac and dest_ac and exchage_amt:
            # Find Forex Journal for move entries.
            forex_dom = [('code', '=', 'FOREX'),
                         ('company_id', '=', self.company_id.id)]
            forex_jrnl = self.env['account.journal'].search(forex_dom, limit=1)

            self.invoice_move_entry_create(src_ac, dest_ac,
                                           'forex_rev_entry_id',
                                           exchage_amt, False,
                                           today, forex_jrnl or False,
                                           False)
        return True

    @api.model
    def _cron_forex_entry(self):
        """
            Automated Method for Forex Entry Creation.
        """
        today = date.today().replace(day=1) - timedelta(days=1)
        for inv in self.search([('invoice_payment_state', '=', 'not_paid'),
                                ('invoice_date', '<=', today),
                                ('type', 'not in', ['entry', 'out_receipt', 'in_receipt']),
                                ]):
            # compute the number of invoices to consider for the Forex Entry.
            if inv.company_id.currency_id == inv.currency_id:
                continue
            if inv.forex_entry_id:
                inv.forex_entry_id = inv.forex_rev_entry_id = False
            if inv.partner_id.property_account_receivable_id:
                inv.forex_move_entry_create(inv.partner_id.property_account_receivable_id, 'forex_entry_id',
                                            today)
                inv.forex_entry_reversal()
                inv.auto_reconcile_entries(inv.forex_entry_id,
                                           inv.forex_rev_entry_id)
        return True

    @api.model
    def line_get_convert(self, line, partner):
        '''
            Get invoice line of move
        '''
        return {
            'date_maturity': line.get('date_maturity', False),
            'partner_id': partner,
            'name': line['name'],
            'debit': line['price'] > 0 and line['price'],
            'credit': line['price'] < 0 and -line['price'],
            'account_id': line['account_id'],
            'analytic_line_ids': line.get('analytic_line_ids', []),
            'amount_currency': line['price'] > 0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
            'currency_id': line.get('currency_id', False),
            'quantity': line.get('quantity', 1.00),
            'product_id': line.get('product_id', False),
            'product_uom_id': line.get('uom_id', False),
            'analytic_account_id': line.get('account_analytic_id', False),
            'tax_ids': line.get('tax_ids', False),
            'tax_line_id': line.get('tax_line_id', False),
            'analytic_tag_ids': line.get('analytic_tag_ids', False),
        }
