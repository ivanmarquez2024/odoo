# -*- coding: utf-8 -*-
import io

from odoo import _, models
from odoo.tools.misc import xlsxwriter


class AccountReport(models.AbstractModel):
    _inherit = 'account.coa.report'

    def _get_columns_name(self, options):
        cols = super()._get_columns_name(options)
        if not self.env.context.get('xlsx_mode'):
            return cols
        cols.insert(0, {'name': _('Account'), 'style': 'width:10%'})
        cols.append({
            'name': _('Account level')
        })
        cols.append({
            'name': _('Parent')
        })
        return cols

    def get_xlsx(self, options, response=None):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {
            'in_memory': True,
            'strings_to_formulas': False,
        })
        sheet = workbook.add_worksheet(self._get_report_name()[:31])

        date_default_col1_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2, 'num_format': 'yyyy-mm-dd'})
        date_default_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'num_format': 'yyyy-mm-dd'})
        default_col1_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2})
        default_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666'})
        title_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2})
        super_col_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'align': 'center'})
        level_0_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 13, 'bottom': 6, 'font_color': '#666666'})
        level_1_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 13, 'bottom': 1, 'font_color': '#666666'})
        level_2_col1_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666', 'indent': 1})
        level_2_col1_total_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666'})
        level_2_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666'})
        level_3_col1_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2})
        level_3_col1_total_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666', 'indent': 1})
        level_3_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666'})

        # Set the first column width to 50
        sheet.set_column(1, 1, 50)

        super_columns = self._get_super_columns(options)
        y_offset = bool(super_columns.get('columns')) and 1 or 0

        sheet.write(y_offset, 0, '', title_style)

        # Todo in master: Try to put this logic elsewhere
        x = 2
        for super_col in super_columns.get('columns', []):
            cell_content = super_col.get('string', '').replace('<br/>', ' ').replace('&nbsp;', ' ')
            x_merge = super_columns.get('merge')
            if x_merge and x_merge > 1:
                sheet.merge_range(0, x, 0, x + (x_merge - 1), cell_content, super_col_style)
                x += x_merge
            else:
                sheet.write(0, x, cell_content, super_col_style)
                x += 1
        for row in self.with_context(xlsx_mode=True).get_header(options):
            x = 0
            for column in row:
                colspan = column.get('colspan', 1)
                header_label = column.get('name', '').replace('<br/>', ' ').replace('&nbsp;', ' ')
                if colspan == 1:
                    sheet.write(y_offset, x, header_label, title_style)
                else:
                    sheet.merge_range(y_offset, x, y_offset, x + colspan - 1, header_label, title_style)
                x += colspan
            y_offset += 1
        ctx = self._set_context(options)
        ctx.update({'no_format': True, 'print_mode': True, 'prefetch_fields': False})
        # deactivating the prefetching saves ~35% on get_lines running time
        lines = self.with_context(ctx)._get_lines(options)

        if options.get('hierarchy'):
            lines = self.with_context(no_format=True)._create_hierarchy(lines, options)
        if options.get('selected_column'):
            lines = self._sort_lines(lines, options)
        # write all data rows
        for y in range(0, len(lines)):
            level = lines[y].get('level')
            if lines[y].get('caret_options'):
                style = level_3_style
                col1_style = level_3_col1_style
            elif level == 0:
                y_offset += 1
                style = level_0_style
                col1_style = style
            elif level == 1:
                style = level_1_style
                col1_style = style
            elif level == 2:
                style = level_2_style
                col1_style = 'total' in lines[y].get('class', '').split(
                    ' ') and level_2_col1_total_style or level_2_col1_style
            elif level == 3:
                style = level_3_style
                col1_style = 'total' in lines[y].get('class', '').split(
                    ' ') and level_3_col1_total_style or level_3_col1_style
            else:
                style = default_style
                col1_style = default_col1_style

            # write the first column, with a specific style to manage the indentation
            cell_type, cell_value = self._get_cell_type_value(lines[y])
            account_code, account_name = False, False
            if lines[y]['id'] == 'grouped_accounts_total':
                sheet.merge_range(y + y_offset, 0, y + y_offset, 1, cell_value, col1_style)
            elif cell_type == 'date':
                sheet.write_datetime(y + y_offset, 1, cell_value, date_default_col1_style)
            else:
                split_cell_value = cell_value.split(' ', 1)
                try:
                    account_code = split_cell_value[0]
                    account_name = split_cell_value[1]
                except IndexError:
                    account_name = split_cell_value[0]
                    account_code = False
                sheet.write(y + y_offset, 0, account_code or '', col1_style)
                sheet.write(y + y_offset, 1, account_name, col1_style)

            # write all the remaining cells
            last_x, last_y = 'no-x', 'no-y'
            for x in range(1, len(lines[y]['columns']) + 1):
                cell_type, cell_value = self._get_cell_type_value(lines[y]['columns'][x - 1])
                if cell_type == 'date':
                    sheet.write_datetime(y + y_offset, x + lines[y].get('colspan', 1), cell_value,
                                         date_default_style)
                else:
                    sheet.write(y + y_offset, x + lines[y].get('colspan', 1), cell_value or 0, style)
                last_y = y + y_offset
                last_x = x + lines[y].get('colspan', 1)
            account_id = lines[y]['id'] if isinstance(lines[y]['id'], int) else False
            if not account_id:
                domain = [
                    ('name', 'like', f'{account_name}%')
                ]
                if account_code:
                    domain.append(('code', '=', account_code))
                account_id = self.env['account.account'].search_read(
                    domain=domain,
                    fields=['id'],
                    limit=1
                )
                account_id = account_id[0]['id'] if account_id else False
            if last_x != 'no-x' or last_y != 'no-y':
                if account_code:
                    account_level = len(account_code.split('-')) - 1
                    sheet.write(last_y, last_x + 1, account_level, style)
                if account_id:
                    group_read = self.env['account.account'].search_read(
                        domain=[('id', '=', account_id), ('group_id', '!=', False)],
                        fields=['group_id']
                    )
                    group_id = group_read[0]['group_id'][0] if group_read else False
                    if group_id:
                        group_code = self.env['account.group'].search_read(
                            domain=[('id', '=', group_id), ('code_prefix', '!=', False)],
                            fields=['code_prefix']
                        )
                        group_code = group_code[0]['code_prefix'] if group_code else ''
                    else:
                        group_code = ''
                    sheet.write(last_y, last_x + 2, group_code, style)

        workbook.close()
        output.seek(0)
        generated_file = output.read()
        output.close()

        return generated_file
