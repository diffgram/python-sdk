import requests
from requests.auth import HTTPDigestAuth


def get_file_id():
    """
    Get Project file id

    Arguments
        project string id
        working directory?
        filename??

    Future
        How are we handling video with this?
        API method for this?

    """
    pass


def get_label_file_dict(self, use_session = True):
    """
    Get Project label file id dict for project

    Arguments
        self

    Expects
        self.project_string_id
        self.directory_id

    Returns
        sets self.name_to_file_id to the dict returned

    """
    if self.project_string_id is None:
        raise Exception("No project string." + \
                        "Set a project string using .auth()")

    if type(self.project_string_id) != str:
        raise Exception("project_string_id must be of type String")

    endpoint = "/api/v1/project/" + self.project_string_id + \
               "/labels/view/name_to_file_id"
    if use_session:
        response = self.session.get(self.host + endpoint)
    else:
        # Add Auth
        response = requests.get(self.host + endpoint,
                                headers = {'directory_id': str(self.directory_id)},
                                auth = HTTPDigestAuth(self.client_id, self.client_secret))

    self.handle_errors(response)

    data = response.json()
    if data["log"]["success"] == True:
        self.name_to_file_id = data["name_to_file_id"]
    else:
        raise Exception(data["log"]["errors"])
