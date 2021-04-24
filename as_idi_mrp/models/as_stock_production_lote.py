from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import time
import datetime
from time import mktime
from dateutil import parser
from datetime import datetime, timedelta, date
#QR
import qrcode
from bs4 import BeautifulSoup
import tempfile
import base64
from io import StringIO
import io
import logging
_logger = logging.getLogger(__name__)

class StockProduction(models.Model):
    _inherit = "stock.production.lot"    

    def get_qrcode(self,cadena_qr): 
        try:
            qr_img = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L,box_size=10,border=0)
            qr_img.add_data(cadena_qr)
            qr_img.make(fit=True)
            img = qr_img.make_image()
            # buffer = StringIO()
            buffer = io.BytesIO()
            img.save(buffer)
            qr_img = base64.b64encode(buffer.getvalue())
            return qr_img
        except:
            raise UserError(_('No se puedo generar el codigo QR'))     

    ####Funcion para quitar elementos de texto enriquecido en reportes
    def get_pobs(self,text):
        textstr = ''
        if text:
            textstr = BeautifulSoup(text,"html.parser").text
        return textstr


