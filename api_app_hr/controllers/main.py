import requests
import json

from odoo import models
from odoo import http, _, exceptions
from odoo.http import request

version = "v1"
# clave api test
# 51b6d9c8b094f1ada742753691936798d01ff838


class User(http.Controller):

    @classmethod
    def auth_method_my_api_key(self):
        api_key = request.httprequest.headers.get("Authorization")
        if not api_key:
            return '{"status": 400, "response": "Error", "message": "Authorization header with API key missing"}'
        user_id = request.env["res.users.apikeys"]._check_credentials(scope="rpc", key=api_key)
        if not user_id:
            return '{"status": 400, "response": "Error", "message": "API key invalid"}'
        else:
            return '{"status": 200, "response": "Success", "message": "API key valid"}'

    # /hr_app/api/v1/users/search
    @http.route('/hr_app/api/' + version + '/users/search', auth="public", methods=['GET'], csrf=False, type='http', cors="*")
    def search(self, **kw):
        try:
            # Validación de la api-key
            # api_key_valid = User.auth_method_my_api_key()
            # api_key_valid = json.loads(api_key_valid)
            # if api_key_valid["status"] != 200:
            #     return json.dumps(api_key_valid)
            # else:
            # Query
            query = [('active', '=', True)]
            get_users = http.request.env["res.users"].sudo().search(query)
            if not get_users:
                return {"status": 404, "response": [], "message": "No existe el usuario"}
            users = []
            for user in get_users:
                vals = {
                    "Id": user.id,
                    "Login": user.login,
                    "Partner": user.partner_id.id,
                    "Nombre Partner": user.partner_id.name,
                    "Ciudad": user.partner_id.city,
                    "Provincia": user.partner_id.state_id.name,
                    "Telefono": user.partner_id.mobile,
                    "Notification": user.notification_type,
                }
            users.append(vals)
        except Exception as e:
            raise Exception(e)
        return {'status': 200, 'response': users, 'message': 'Usuarios recuperados correctamente'}

    # /hr_app/api/v1/user/get
    @http.route('/hr_app/api/' + version + '/user/get', auth="public", methods=['GET'], csrf=False, type='json', cors="*")
    def get(self, **kw):
        try:
            # api_key_valid = User.auth_method_my_api_key()
            # api_key_valid = json.loads(api_key_valid)
            # if api_key_valid["status"] != 200:
            #     return json.dumps(api_key_valid)
            # else:
            data = {
                "status": "",
                "response": [],
                "message": "",
            }
            vals = {
                "Id": "",
                "Login": "",
                "Partner": "",
                "Nombre": "",
                "Genero": "",
                "Ciudad": "",
                "Provincia": "",
                "Telefono": "",
                "Notification": "",
                "Nivel": "",
                "Campo": "",
                "Study": "",
                "Experiencia": [],
                "Habilidades": [],
            }
            email = request.jsonrequest['params']['login']
            # Query
            query = [('login', '=', email), ('active', '=', True)]
            get_user = http.request.env["res.users"].sudo().search(query)
            if not get_user:
                data['status'] = 404
                data['message'] = 'No existe usuario'
                return data
            users = []
            experiences = []
            skills = []
            for user in get_user:
                # add employee
                get_employee = http.request.env["hr.employee"].sudo().search([('user_id', '=', user.id)])
                if get_employee:
                    for employee in get_employee:
                        vals["Genero"] = employee.gender
                        vals["Campo"] = employee.study_field
                        vals["Study"] = employee.study_school
                        vals["Nivel"] = employee.certificate
                        if employee.resume_line_ids:
                            for experience in employee.resume_line_ids:
                                val_exp = {
                                    "Sitio": experience.name,
                                    "Descripcion": experience.description,
                                }
                                experiences.append(val_exp)
                            vals["Experiencia"] = experiences
                        if employee.employee_skill_ids:
                            for skill in employee.employee_skill_ids:
                                val_skill = {
                                    "Skill": skill.skill_id.name,
                                    "Nivel": skill.skill_level_id.name,
                                }
                                skills.append(val_skill)
                            vals["Habilidades"] = skills
                vals["Id"] = user.id
                vals["Login"] = user.login
                vals["Partner"] = user.partner_id.id
                vals["Nombre"] = user.partner_id.name
                vals["Ciudad"] = user.partner_id.city
                vals["Provincia"] = user.partner_id.state_id.name
                vals["Telefono"] = user.partner_id.mobile
                vals["Notification"] = user.notification_type
            users.append(vals)
            data['status'] = 200
            data['response'] = users
            data['message'] = 'Usuario recuperado correctamente'
        except Exception as e:
            raise Exception(e)
        return data
