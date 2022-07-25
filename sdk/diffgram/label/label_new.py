import warnings


def label_new(self,
              label: dict,
              schema_id: int = None):
    """

    Arguments
        self,
        label_list, a list of label strings

    Expects

    Returns

    """
    if schema_id is None:
        schema = self.get_default_label_schema()
        if schema is not None:
            schema_id = schema.get('id')

    # Check if already exists
    name = label.get('name', None)
    if not name:
        raise Exception("Please provide a key of name with a value of label")
    label['schema_id'] = schema_id

    endpoint = "/api/v1/project/" + self.project_string_id + \
               "/label/new"

    response = self.session.post(self.host + endpoint,
                                 json = label)

    data = response.json()
    self.get_label_file_dict()

    if data["log"]["success"] == True:
        return data['label']
    else:
        raise Exception(data["log"]["error"])
