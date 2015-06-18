# -*- coding: utf-8 -*-

from openerp.osv import osv, fields

class hr_job(osv.osv):
    _inherit = ['hr.applicant']

    _columns = {
        'salutation':fields.char('salutation (mr. or mrs.)'),
        'first_name': fields.text('First Name', size=250),
        'last_name': fields.text('Last Name', size=250),
        'partner_address': fields.char('Address', length=250),
        'place': fields.text('Place', size=250),
        'cover_letter': fields.binary('Cover Letter'),
        'curriculum_vitae': fields.binary('Curriculum Vitae'),
        'diploma_certificates': fields.binary('Diploma Certificates'),
        'possible_join_date':fields.char('Possible Join Date')
    }
