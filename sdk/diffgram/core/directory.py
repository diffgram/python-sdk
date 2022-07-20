from diffgram.file.file import File
from ..regular.regular import refresh_from_dict
import logging
from diffgram.core.diffgram_dataset_iterator import DiffgramDatasetIterator
from multiprocessing.pool import ThreadPool as Pool


class Directory(DiffgramDatasetIterator):

    def __init__(self,
                 client,
                 file_id_list_sliced = None,
                 init_file_ids = True,
                 validate_ids = True):

        self.client = client
        self.id = None
        self.file_list_metadata = {}
        self.nickname = None
        if file_id_list_sliced is None and init_file_ids:
            self.init_files()
        elif not init_file_ids:
            self.file_id_list = []
        elif file_id_list_sliced is not None:
            self.file_id_list = file_id_list_sliced
        super(Directory, self).__init__(self.client, self.file_id_list, validate_ids)

    def init_files(self):
        self.file_id_list = self.all_file_ids()
    def get_directory_list(self):
        """
        Get a list of available directories for a project
        """

        if self.client.project_string_id is None:
            raise Exception("No project string." + \
                            "Set a project string using .auth()")

        if type(self.client.project_string_id) != str:
            raise Exception("project_string_id must be of type String")

        endpoint = "/api/v1/project/" + self.client.project_string_id + \
                   "/directory/list"

        response = self.client.session.get(self.client.host + endpoint)

        self.client.handle_errors(response)

        data = response.json()

        directory_list_json = data.get('directory_list')
        default_directory_json = data.get('default_directory')

        if default_directory_json:
            self.client.directory_id = default_directory_json.get('id')

        directory_list = self.convert_json_to_sdk_object(directory_list_json)

        return directory_list

    def convert_json_to_sdk_object(self, directory_list_json):

        directory_list = []

        for directory_json in directory_list_json:
            new_directory = Directory(
                client = self.client,
                init_file_ids = False,
                validate_ids = False
            )
            refresh_from_dict(new_directory, directory_json)

            new_directory.id = new_directory.directory_id

            # note timing issue, this needs to happen after id is refreshed
            new_directory.init_files()
            new_directory.start_iterator(
                project = new_directory.project,
                diffgram_file_id_list = new_directory.file_id_list,
                validate_ids = True
            )

            directory_list.append(new_directory)

        return directory_list

    def all_files(self):
        """
            Get all the files of the directoy.
            Warning! This can be an expensive function and take a long time.
        :return:
        """
        page_num = 1
        result = []
        while page_num is not None:
            diffgram_files = self.list_files(
                limit = 1000,
                page_num = page_num,
                file_view_mode = 'base')
            page_num = self.file_list_metadata['next_page']
            result = result + diffgram_files
        return result

    def all_file_ids(self, query = None):
        page_num = 1
        result = []

        diffgram_ids = self.list_files(
            limit = 5000,
            page_num = page_num,
            file_view_mode = 'ids_only',
            query = query)

        if diffgram_ids is False:
            raise Exception('Error Fetching Files: Please check you are providing a valid query.')
        result = result + diffgram_ids
        page_num = self.file_list_metadata['next_page']
        total_pages = self.file_list_metadata['total_pages']
        pool = Pool(20)

        pool_results = []
        if page_num is not None:
            for i in range(page_num, total_pages + 1):
                result_async = pool.apply_async(self.list_files, (i, 5000, None, 'ids_only', None))
                pool_results.append(result_async)

        for pool_result in pool_results:
            file_ids = pool_result.get()
            result = result + file_ids

        return result

    def explore(self):
        message = '{}/studio/annotate/{}/explorer?dataset_id={}'.format(
            self.client.host,
            self.project.project_string_id,
            self.id
        )
        print('\033[92m' + 'To Explore your dataset visit:' + '\033[0m')
        print('\033[96m' + message + '\033[0m')

    def slice(self, query):
        from diffgram.core.sliced_directory import SlicedDirectory
        # Get the first page to validate syntax.
        self.list_files(
            limit = 25,
            page_num = 1,
            file_view_mode = 'ids_only',
            query = query,
        )
        sliced_dataset = SlicedDirectory(
            client = self.client,
            query = query,
            original_directory = self
        )
        return sliced_dataset

    def to_pytorch(self, transform = None):
        """
            Transforms the file list inside the dataset into a pytorch dataset.
        :return:
        """
        from diffgram.pytorch_diffgram.diffgram_pytorch_dataset import DiffgramPytorchDataset
        file_id_list = self.file_id_list
        pytorch_dataset = DiffgramPytorchDataset(
            project = self.client,
            diffgram_file_id_list = file_id_list,
            transform = transform,
            validate_ids = False

        )
        return pytorch_dataset

    def to_tensorflow(self):
        from diffgram.tensorflow_diffgram.diffgram_tensorflow_dataset import DiffgramTensorflowDataset
        file_id_list = self.file_id_list
        diffgram_tensorflow_dataset = DiffgramTensorflowDataset(
            project = self.client,
            diffgram_file_id_list = file_id_list,
            validate_ids = False
        )
        return diffgram_tensorflow_dataset

    def new(self, name: str):
        """
        Create a new directory and update directory list.

        We include name in exception message since this may
        be included in larger functions in which
        the name may be unclear

        """
        if name is None:
            raise Exception("No name provided.")

        # Confirm not in existing
        # generator expression returns True if the directory
        # is not found. this is a bit awkward.
        if self.client.directory_list:
            if next((dir for dir in self.client.directory_list
                     if dir.nickname == name), True) is not True:
                raise Exception(name, "Already exists")

        packet = {'nickname': name}

        endpoint = "/api/v1/project/" + \
                   self.client.project_string_id + "/directory/new"

        response = self.client.session.post(
            self.client.host + endpoint,
            json = packet)

        self.client.handle_errors(response)

        data = response.json()

        project = data.get('project')
        if project:
            directory_list_json = project.get('directory_list')
            if directory_list_json:
                self.client.directory_list = self.convert_json_to_sdk_object(directory_list_json)

        new_directory = None
        # TODO the route about should return the newly created dataset directly
        for directory in self.client.directory_list:
            if directory.nickname == name:
                new_directory = directory

        return new_directory

    def list_files(
            self,
            page_num = 1,
            limit = 100,
            search_term: str = None,
            file_view_mode: str = 'annotation',
            query: str = None):
        """
        """
        if self.id:
            logging.info("Using Dataset ID " + str(self.id))
            directory_id = self.id
        else:
            logging.info("Using Default Dataset ID " + str(self.client.directory_id))
            directory_id = self.client.directory_id

        metadata = {'metadata':
            {
                'directory_id': directory_id,
                'annotations_are_machine_made_setting': "All",
                'annotation_status': "All",
                'limit': limit,
                'media_type': "All",
                'page': page_num,
                'file_view_mode': file_view_mode,
                'search_term': search_term,
                'query': query
            }
        }

        # User concept, in this context, is deprecated
        # 'sdk' is a placeholder value

        endpoint = "/api/project/" + \
                   self.client.project_string_id + \
                   "/user/sdk" + "/file/list"

        response = self.client.session.post(
            self.client.host + endpoint,
            json = metadata)

        self.client.handle_errors(response)

        # Success
        data = response.json()
        file_list_json = data.get('file_list')
        self.file_list_metadata = data.get('metadata')
        # TODO would like this to perhaps be a seperate function
        # ie part of File_Constructor perhaps
        if file_view_mode == 'ids_only':
            return file_list_json
        else:
            file_list = []
            for file_json in file_list_json:
                file = File.new(
                    client = self.client,
                    file_json = file_json)
                file_list.append(file)

            return file_list

    def get(self,
            name: str):

        """

        Returns Dataset Object for given name.
        Uses existing dir list from project.

         "NEW" version of set_directory_by_name()
         TODO refactor set_directory_by_name() to use this

        """
        if name is None:
            raise Exception("No name provided.")

        names_attempted = []
        did_set = False

        if not self.client.directory_list:
            self.client.directory_list = self.get_directory_list()

        for directory in self.client.directory_list:

            if directory.nickname == name:
                directory.init_files()
                return directory

            else:
                names_attempted.append(directory.nickname)

        if did_set is False:
            raise Exception(name, " does not exist. Valid names are: " +
                            str(names_attempted))

    def add(self,
            file_list: list = None,
            file_id_list: list = None):
        """
        Add links from file_ids to the dataset.
        Does not modify existing links

        file_id_list expects ints of file_ids
        file_list is a list of Diffgram file objects
        """
        if not file_id_list and not file_list:
            raise "Must have either file_id_list or file_list (File class objects)"

        file_list_formated_as_dicts = []

        if file_id_list:
            for file_id in file_id_list:
                file_list_formated_as_dicts.append(
                    {'id': file_id})

        if file_list:
            for file in file_list:
                file_list_formated_as_dicts.append(
                    {'id': file.id})

        endpoint = "/api/v1/project/" + \
                   self.client.project_string_id + \
                   "/file/transfer"

        spec_dict = {
            'file_list': file_list_formated_as_dicts,
            'destination_directory_id': self.id,
            'mode': 'TRANSFER',
            'transfer_action': 'mirror'
        }

        response = self.client.session.post(
            self.client.host + endpoint,
            json = spec_dict)

        self.client.handle_errors(response)

        response_json = response.json()

        return response_json
