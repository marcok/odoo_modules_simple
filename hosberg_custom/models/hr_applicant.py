# -*- coding: utf-8 -*-

from openerp.osv import osv, fields

class hr_job(osv.osv):
    _inherit = ['hr.applicant']

    _columns = {
        'salutation':fields.char('salutation (mr. or mrs.)', required=True),
        'first_name': fields.text('First Name', size=250, required=True),
        'last_name': fields.text('Last Name', size=250, required=True),
        'partner_address': fields.char('Address', length=250, required=True ),
        'place': fields.text('Place', size=250, required=True),
        'cover_letter': fields.binary('Cover Letter', required=True),
        'curriculum_vitae': fields.binary('Curriculum Vitae', required=True),
        'diploma_certificates': fields.binary('Diploma Certificates'),
        'possible_join_date':fields.char('Possible Join Date')
    }
