odoo.define('contabilidad_cfdi.client_action', function (require) {
"use strict";

var ReportAction = require('report.client_action');

ReportAction.include({
	start: function () {
		var self = this;
		var res = this._super.apply(this, arguments);
		if (this.report_name=="contabilidad_cfdi.trial_balance" || this.report_name=="contabilidad_cfdi.catalogo_cuentas" ) {
            return res.then(function () {
                if (self.$buttons.find(".o_report_print").length){
					var $export_xml_button = $("<button type='button' style='margin-left: 10px;' class='btn btn-primary o_list_button_generar_xml' accesskey='xm'>Generar XML</button>");
					self.$buttons.find(".o_report_print").after($export_xml_button);
					self.$buttons.on('click', '.o_list_button_generar_xml', self._onGenerarXMLAccount.bind(self));
				}
            });
        }
        return res;
	},
	_onGenerarXMLAccount: function (event) {
        event.stopPropagation();
		this.context['data']=this.data
		this.context['default_fecha_mes']= this.data.month
		this.context['default_fecha_ano']= this.data.year
		this.context['default_procesa_nivel']= this.data.show_hierarchy_level
        return this.do_action({
            name: "Generar XML",
            type: 'ir.actions.act_window',
            views: [[false, 'form']],
            target: 'new',
            res_model: 'generar.xml.hirarchy.wizard',
			context: this.context,
        });
	
	}
});

});