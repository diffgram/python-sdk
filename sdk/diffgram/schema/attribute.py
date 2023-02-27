class Attribute:
  def __init__(self, project):
    self.project = project

  def list(self, schema):
    url = f'/api/v1/project/{self.project.project_string_id}/attribute/template/list'
    payload = {
      "schema_id": schema['id'],
      "mode": "from_project"
    }

    response = self.project.session.post(url = self.project.host + url, json=payload)
      
    self.project.handle_errors(response)
    data = response.json()

    return data

  def new(self, schema):
    url = f'/api/v1/project/{self.project.project_string_id}/attribute/group/new'
    payload = {
      "schema_id": schema['id']
    }

    response = self.project.session.post(url = self.project.host + url, json=payload)
      
    self.project.handle_errors(response)
    data = response.json()

    return data['attribute_template_group']
  
  def update(self, 
             attribute,
             prompt,
             kind,
             name = None,
             is_global = False,
             label_file_list = None,
             is_read_only = False,
             global_type = 'file',
            ):
    url = f'/api/v1/project/{self.project.project_string_id}/attribute/group/update'
    payload = {
      "group_id": attribute['id'],
      "mode": "UPDATE",
      "prompt": prompt,
      "name": name,
      "kind": kind,
      "is_global": is_global,
      "label_file_list": label_file_list,
      "global_type": global_type,
      "is_read_only": is_read_only
    }

    response = self.project.session.post(url = self.project.host + url, json=payload)
      
    self.project.handle_errors(response)
    data = response.json()

    return data
  
  def add_options(self, attribute, options):
    pass

    