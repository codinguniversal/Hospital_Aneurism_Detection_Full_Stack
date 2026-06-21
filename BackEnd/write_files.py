import os

register_content = """$kind: http-request
name: Register
method: POST
url: '{{baseUrl}}/auth/register'
order: 2000
headers:
  - key: Content-Type
    value: application/json
body:
  type: json
  content: |-
    {
      "email": "johndoe@example.com",
      "password": "securepassword",
      "gender": "male"
    }
description: 'Register a new user (email, password, gender). Returns 201 with user_id on success, 400 on validation error.'
"""

admin_content = """$kind: http-request
name: Update Admin Settings
method: PUT
url: '{{baseUrl}}/admin/settings'
order: 1000
headers:
  - key: Content-Type
    value: application/json
body:
  type: json
  content: |-
    {
      "ai_api_url": "http://localhost:8001/analyze",
      "ai_timeout_limit": 30,
      "automatic_scan_start_hour": 8,
      "automatic_scan_end_hour": 18,
      "automatic_scan_interval": 60,
      "aneurysm_high_risk_threshold": 0.85,
      "aneurysm_medium_risk_threshold": 0.60
    }
description: 'Update admin settings. Fields: ai_api_url, ai_timeout_limit, automatic_scan_start_hour (0-23), automatic_scan_end_hour (0-23), automatic_scan_interval, aneurysm_high_risk_threshold (0-1), aneurysm_medium_risk_threshold (0-1). High threshold must be > medium threshold. Start hour must be < end hour.'
"""

register_path = r'postman/collections/Hospital Aneurysm Detection API/Authentication/Register.request.yaml'
admin_path = r'postman/collections/Hospital Aneurysm Detection API/admin/New Request.request.yaml'

with open(register_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(register_content)
print('Register written')

with open(admin_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(admin_content)
print('Admin written')
