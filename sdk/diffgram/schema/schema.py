class Schema:
   def __init__(self, project):
      self.project = project
    
   def list(self):
      url = f'/api/v1/project/{self.project.project_string_id}/labels-schema'
      response = self.project.session.get(url = self.project.host + url)
      self.project.handle_errors(response)
      data = response.json()

      return data
   
   def default_schema(self):
      url = f'/api/v1/project/{self.project.project_string_id}/labels-schema'
      response = self.project.session.get(url = self.project.host + url)
      self.project.handle_errors(response)
      data = response.json()

      default_schema = None

      for schema in data:
         if schema['is_default'] == True:
            default_schema = schema

      return default_schema
    
   
   def new(self, name):
      url = f'/api/v1/project/{self.project.project_string_id}/labels-schema/new'
      payload = {
         "name": name
      }

      response = self.project.session.post(url = self.project.host + url, json=payload)
      
      self.project.handle_errors(response)
      data = response.json()

      return data
    
   def update(self, name):
       #Todo
       pass
    
   def archive(self, name):
       #Todo
       pass
       