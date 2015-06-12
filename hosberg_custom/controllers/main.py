# -*- coding: utf-8 -*-
import base64

from openerp import SUPERUSER_ID
from openerp import http
from openerp.tools.translate import _
from openerp.http import request

from openerp.addons.website.models.website import slug

class website_hr_recruitment(http.Controller):
    @http.route([
        '/jobs',
        '/jobs/country/<model("res.country"):country>',
        '/jobs/department/<model("hr.department"):department>',
        '/jobs/country/<model("res.country"):country>/department/<model("hr.department"):department>',
        '/jobs/office/<int:office_id>',
        '/jobs/country/<model("res.country"):country>/office/<int:office_id>',
        '/jobs/department/<model("hr.department"):department>/office/<int:office_id>',
        '/jobs/country/<model("res.country"):country>/department/<model("hr.department"):department>/office/<int:office_id>',
    ], type='http', auth="public", website=True)
    def jobs(self, country=None, department=None, office_id=None, **kwargs):
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
 
        Country = env['res.country']
        Jobs = env['hr.job']
 
        # List jobs available to current UID
        job_ids = Jobs.search([], order="website_published desc,no_of_recruitment desc").ids
        # Browse jobs as superuser, because address is restricted
        jobs = Jobs.sudo().browse(job_ids)
 
        # Deduce departments and offices of those jobs
        departments = set(j.department_id for j in jobs if j.department_id)
        offices = set(j.address_id for j in jobs if j.address_id)
        countries = set(o.country_id for o in offices if o.country_id)
 
        # Default search by user country
        if not (country or department or office_id or kwargs.get('all_countries')):
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                countries_ = Country.search([('code', '=', country_code)])
                country = countries_[0] if countries_ else None
                if not any(j for j in jobs if j.address_id and j.address_id.country_id == country):
                    country = False
 
        # Filter the matching one
        if country and not kwargs.get('all_countries'):
            jobs = (j for j in jobs if j.address_id is None or j.address_id.country_id and j.address_id.country_id.id == country.id)
        if department:
            jobs = (j for j in jobs if j.department_id and j.department_id.id == department.id)
        if office_id:
            jobs = (j for j in jobs if j.address_id and j.address_id.id == office_id)
 
        # Render page
        return request.website.render("website_hr_recruitment.index", {
            'jobs': jobs,
            'countries': countries,
            'departments': departments,
            'offices': offices,
            'country_id': country,
            'department_id': department,
            'office_id': office_id,
        })
        
    @http.route('/jobs/apply/<model("hr.job"):job>', type='http', auth="public", website=True)
    def jobs_apply(self, job):
        error = {}
        default = {}
        if 'website_hr_recruitment_error' in request.session:
            print '----'
            error = request.session.pop('website_hr_recruitment_error')
            default = request.session.pop('website_hr_recruitment_default')
        return request.render("website_hr_recruitment.apply", {
            'job': job,
            'error': error,
            'default': default,
        })

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
