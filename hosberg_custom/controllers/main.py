# -*- coding: utf-8 -*-
import base64

from openerp import SUPERUSER_ID
from openerp import http
from openerp.tools.translate import _
from openerp.http import request

from openerp.addons.website.models.website import slug

class website_hr_recruitment(http.Controller):

    @http.route('/jobs/thankyou', methods=['POST'], type='http', auth="public", website=True)
    def jobs_thankyou(self, **post):
        error = {}
        for field_name in ["salutation", "first_name", "last_name", "partner_address", "place", "partner_phone", "email_from", "cover_letter", "curriculum_vitae"]:
            if not post.get(field_name):
                error[field_name] = 'missing'
        if error:
            request.session['website_hr_recruitment_error'] = error
            cover_letter = post.pop('cover_letter')
            curriculum_vitae = post.pop('curriculum_vitae')
            diploma_certificates = post.pop('diploma_certificates')
            
            if cover_letter:
                error['cover_letter'] = 'reset'
            if curriculum_vitae:
                error['curriculum_vitae'] = 'reset'   
            if diploma_certificates:
                error['diploma_certificates'] = 'reset'    
            
            request.session['website_hr_recruitment_default'] = post
            return request.redirect('/jobs/apply/%s' % post.get("job_id"))
 
        # public user can't create applicants (duh)
        env = request.env(user=SUPERUSER_ID)
        value = {
            'source_id' : env.ref('hr_recruitment.source_website_company').id,
            'name': '%s\'s Application' % post.get('first_name'), 
        }
        
        for f in ['salutation', 'first_name', 'last_name', 'partner_address', 'place', 'partner_phone', 'email_from', 'possible_join_date', 'description']:
            value[f] = post.get(f)
        for f in ['department_id', 'job_id']:
            value[f] = int(post.get(f) or 0)
        # Retro-compatibility for saas-3. "phone" field should be replace by "partner_phone" in the template in trunk.
        value['partner_name'] = post.pop('first_name', False) + ' ' + post.pop('last_name', False)
        
        applicant_id = env['hr.applicant'].create(value).id
        if post['cover_letter']:
            attachment_value = {
                'name': post['cover_letter'].filename,
                'res_name': value['first_name'],
                'res_model': 'hr.applicant',
                'res_id': applicant_id,
                'datas': base64.encodestring(post['cover_letter'].read()),
                'datas_fname': post['cover_letter'].filename,
            }
            env['ir.attachment'].create(attachment_value)
            
        if post['curriculum_vitae']:
            attachment_value = {
                'name': post['curriculum_vitae'].filename,
                'res_name': value['first_name'],
                'res_model': 'hr.applicant',
                'res_id': applicant_id,
                'datas': base64.encodestring(post['curriculum_vitae'].read()),
                'datas_fname': post['curriculum_vitae'].filename,
            }
            env['ir.attachment'].create(attachment_value)
            
        if post['diploma_certificates']:
            attachment_value = {
                'name': post['diploma_certificates'].filename,
                'res_name': value['first_name'],
                'res_model': 'hr.applicant',
                'res_id': applicant_id,
                'datas': base64.encodestring(post['diploma_certificates'].read()),
                'datas_fname': post['diploma_certificates'].filename,
            }
            env['ir.attachment'].create(attachment_value)   
        return request.render("website_hr_recruitment.thankyou", {})

# vim :et:
