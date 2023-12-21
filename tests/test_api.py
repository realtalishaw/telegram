from api.project import create_project
project_data = {
  "id": "string",
  "moonID": "string",
  "name": "string",
  "description": "string",
  "status": "ACTIVE",
  "projectLead": "string",
}
print(create_project(project_data))