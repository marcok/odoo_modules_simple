# -*- coding: utf-8 -*-

from openerp import api, fields, models, _


class hr_job(models.Model):
    _inherit = ['hr.applicant']

    salutation = fields.Char(string='salutation (mr. or mrs.)')
    first_name = fields.Text(string='First Name', size=250)
    last_name = fields.Text(string='Last Name', size=250)
    partner_address = fields.Char(string='Address', length=250)
    place = fields.Text(string='Place', size=250)
    cover_letter = fields.Binary(string='Cover Letter')
    curriculum_vitae = fields.Binary(string='Curriculum Vitae')
    diploma_certificates = fields.Binary(string='Diploma Certificates')
    possible_join_date = fields.Char(string='Possible Join Date')
