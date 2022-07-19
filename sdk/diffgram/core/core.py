import requests

from diffgram import __version__

from diffgram.file.view import get_label_file_dict
from diffgram.convert.convert import convert_label
from diffgram.label.label_new import label_new

from diffgram.core.directory import Directory
from diffgram.job.job import Job
from diffgram.job.guide import Guide
from diffgram.brain.brain import Brain
from diffgram.file.file_constructor import FileConstructor
from diffgram.file.file import File
from diffgram.brain.train import Train
from diffgram.export.export import Export
from diffgram.task.task import Task
from requests.auth import HTTPBasicAuth


class Project():
    default_directory: Directory

    def __init__(
            self,
            project_string_id,
            client_id = None,
            client_secret = None,
            debug = False,
            staging = False,
            host = None,
            init_default_directory = True,
            refresh_local_label_dict = True

    ):

        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections = 30, pool_maxsize = 30)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.project_string_id = None

        self.debug = debug
        self.staging = staging
        if host is None:
            if self.debug is True:
                self.host = "http://127.0.0.1:8085"
                print("Debug", __version__)
            elif self.staging is True:
                self.host = "https://20200110t142358-dot-walrus-dot-diffgram-001.appspot.com/"
            else:
                self.host = "https://diffgram.com"
        else:
            self.host = host

        self.auth(
            project_string_id = project_string_id,
            client_id = client_id,
            client_secret = client_secret)

        self.file = FileConstructor(self)
        #self.train = Train(self)
        self.job = Job(self)
        self.guide = Guide(self)
        self.directory = Directory(self, 
                                   init_file_ids = False,
                                   validate_ids = False)
        self.export = Export(self)
        self.task = Task(client = self)

        self.directory_id = None
        self.name_to_file_id = None

        self.client_id = client_id
        self.client_secret = client_secret

        if init_default_directory is True:
            self.set_default_directory(directory = self.directory)
            print("Default directory set:", self.directory_id)

        if refresh_local_label_dict is True:
            self.get_label_file_dict()

        self.label_schema_list = self.get_label_schema_list()

        self.directory_list = None


    def get_member_list(self):
        url = '/api/project/{}/view'.format(self.project_string_id)
        response = self.session.get(url = self.host + url)
        self.handle_errors(response)
        data = response.json()
        return data['project']['member_list']

    def get_label_schema_by_id(self, id):
        if self.label_schema_list is None or len(self.label_schema_list) == 0:
            self.label_schema_list = self.get_label_schema_list()
        for s in self.label_schema_list:
            if s['id'] == id:
                return s

    def get_label_schema_by_name(self, name):
        if self.label_schema_list is None or len(self.label_schema_list) == 0:
            self.label_schema_list = self.get_label_schema_list()
        for s in self.label_schema_list:
            if s['name'] == name:
                return s

    def get_default_label_schema(self):
        if self.label_schema_list is None or len(self.label_schema_list) == 0:
            self.label_schema_list = self.get_label_schema_list()

        return self.label_schema_list[0]

    def get_connection_list(self):
        url = f'/api/project/{self.project_string_id}/connections'
        response = self.session.get(url = self.host + url)
        self.handle_errors(response)
        data = response.json()
        return data.get('connection_list')

    def get_label_list(self, schema_id = None):
        url = f'/api/project/{self.project_string_id}/labels'
        if schema_id is None:
            schema = self.get_default_label_schema()
            if schema is not None:
                schema_id = schema.get('id')

        params = {'schema_id': schema_id}
        response = self.session.get(url = self.host + url, params=params)
        self.handle_errors(response)
        data = response.json()
        return data.get('labels_out')

    def get_label_schema_list(self):
        url = f'/api/v1/project/{self.project_string_id}/labels-schema'
        response = self.session.get(url = self.host + url)
        self.handle_errors(response)
        data = response.json()
        return data

    def get_attributes(self, schema_id = None):
        if schema_id is None:
            schema = self.get_default_label_schema()
            if schema is not None:
                schema_id = schema.get('id')
        url = f'/api/v1/project/{self.project_string_id}/attribute/template/list'
        data = {
            'schema_id': schema_id,
            'mode': "from_project",
        }
        response = self.session.post(url = self.host + url, json=data)
        self.handle_errors(response)
        data = response.json()
        return data.get('attribute_group_list')

    def get_http_auth(self):
        return HTTPBasicAuth(self.client_id, self.client_secret)

    def get_label(
            self,
            name = None,
            schema_id = None,
            name_list = None):
        """
        name, str
        name_list, list, optional

        Name must be an exact match to label name.

        If a name_list is provided it will construct a list of
        objects that match that name.

        Returns
            None if not found.
            File object of type Label if found.
            List of File objects if a proj is provided.
        """
        if self.name_to_file_id is None:
            self.get_label_file_dict()

        if name_list:
            out = []
            for name in name_list:
                out.append(self.get_label(name))
            return out

        id = self.name_to_file_id.get(name)

        if id is None:
            return None

        file = File(id = id)
        return file

    def get_model(
            self,
            name = None,
            local = False):

        brain = Brain(
            client = self,
            name = name,
            local = local
        )

        return brain

    def handle_errors(self,
                      response):

        """
        Upon a bad request (400), our error log contains
        good information to raise.

        We also catch a few more common codes to
        try and print simpler messages.

        Otherwise expects this to be caught by raise_for_status()
        if applicable
        https://2.python-requests.org/en/master/_modules/requests/models/#Response.raise_for_status

        This is under the assumption that we generaly call response.json()
        after this, and that fails in poor way if there is no json available.
        """

        # Default
        if response.status_code == 200:
            return

        # Errors
        if response.status_code == 400:
            try:
                raise Exception(response.json()["log"]["error"])
            except:
                raise Exception(response.text)

        if response.status_code == 403:
            raise Exception("Invalid Permission", response.text)

        if response.status_code == 404:
            raise (Exception("404 Not Found" + response.text))

        if response.status_code == 429:
            raise Exception(
                "Rate Limited. Please add buffer between calls eg time.sleep(1). Otherwise, please try again later. Else contact us if this persists.")

        if response.status_code == 500:
            raise Exception("Internal error, please try again later.")

        raise_for_status = response.raise_for_status()
        if raise_for_status:
            Exception(raise_for_status)

    def auth(self,
             project_string_id,
             client_id = None,
             client_secret = None
             ):
        """
        Define authorization configuration

        If no client_id / secret is provided it assumes project is public
        And if project isn't public it will return a 403 permission denied.

        Arguments
            client_id, string
            client_secret, string
            project_string_id, string

        Returns
            None

        Future
            More gracefully intial setup (ie validate upon setting)
        """
        self.project_string_id = project_string_id

        if client_id and client_secret:
            self.session.auth = (client_id, client_secret)


    def set_directory_by_name(self, name):
        """

        Arguments
            self
            name, string

        """

        if name is None:
            raise Exception("No name provided.")

        # Don't refresh by default, just set from existing

        names_attempted = []
        did_set = False

        if not self.directory_list:
            self.directory_list = self.directory.get_directory_list()

        for directory in self.directory_list:

            if directory.nickname == name:
                self.set_default_directory(directory = directory)
                did_set = True
                break
            else:
                names_attempted.append(directory.nickname)

        if did_set is False:
            raise Exception(name, " does not exist. Valid names are: " +
                            str(names_attempted))


    def set_default_directory(self,
                              directory_id = None,
                              directory = None):
        """
        -> If no id is provided fetch directory list for project
        and set first directory to default.
        -> Sets the headers of self.session

        """
        if directory_id:
            self.directory_id = directory_id
        if directory is not None:
            self.directory_id = directory.id
            self.default_directory = directory
        if not hasattr(self, 'directory_list'):
            self.directory_list = self.directory.get_directory_list()

        self.session.headers.update(
            {'directory_id': str(self.directory_id)})



    def new_schema(self,
                   name: str):

            endpoint = "/api/v1/project/" + self.project_string_id + \
                       "/labels-schema/new"

            request_json_body = {'name': name}

            response = self.session.post(self.host + endpoint,
                                         json = request_json_body)

            self.handle_errors(response)
            return response.json()


# TODO review not using this pattern anymore

setattr(Project, "get_label_file_dict", get_label_file_dict)
setattr(Project, "convert_label", convert_label)
setattr(Project, "label_new", label_new)
