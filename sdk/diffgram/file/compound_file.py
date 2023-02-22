from diffgram.core.core import Project
from typing import List
from diffgram.file.file import File
from diffgram.job.job import Job
from uuid import uuid4


class CompoundChildFile:
    id: int
    path: str
    url: str
    blob_path: str
    file_name: str
    bucket_name: str
    child_file_type: str
    connection_id: int
    media_type: str
    job: Job
    job_id: int
    directory_id: int
    instance_list: list
    frame_packet_map: dict
    assume_new_instances_machine_made: bool
    convert_names_to_label_files: bool
    video_split_duration: int
    local_id: str
    ordinal: int
    root_file: 'CompoundFile'

    def __init__(self,
                 root_file: 'CompoundFile',
                 child_file_type: str,
                 path: str = None,
                 url: str = None,
                 blob_path: str = None,
                 file_name: str = None,
                 bucket_name: str = None,
                 connection_id: int = None,
                 media_type: str = None,
                 job: Job = None,
                 job_id: int = None,
                 directory_id: int = None,
                 instance_list: list = None,
                 frame_packet_map: dict = None,
                 assume_new_instances_machine_made: bool = None,
                 convert_names_to_label_files: bool = None,
                 video_split_duration: int = None,
                 ordinal: int = 0,
                 id: int = None):
        self.root_file = root_file
        self.child_file_type = child_file_type
        self.path = path
        self.url = url
        self.blob_path = blob_path
        self.file_name = file_name
        self.bucket_name = bucket_name
        self.connection_id = connection_id
        self.media_type = media_type
        self.job = job
        self.job_id = job_id
        self.directory_id = directory_id
        self.instance_list = instance_list
        self.frame_packet_map = frame_packet_map
        self.assume_new_instances_machine_made = assume_new_instances_machine_made
        self.convert_names_to_label_files = convert_names_to_label_files
        self.video_split_duration = video_split_duration
        self.local_id = str(uuid4())
        self.ordinal = ordinal
        self.id = None

    def __str__(self):
        return f'<CompoundChildFile id={self.id} ordinal={self.ordinal} file_name={self.file_name} child_file_type={self.child_file_type}>'
    def refresh_from_data_dict(self, data: dict):
        if not data:
            return
        for key in data:
            setattr(self, key, data[key])

    def update(self):
        """
            Syncs child file data with backend API
        :return:
        """
        payload = {
            'ordinal': self.ordinal,
        }
        client = self.root_file.project
        endpoint = f"/api/v1/project/{self.root_file.project.project_string_id}/file/{self.id}/update-metadata"

        response = client.session.put(
            client.host + endpoint,
            json = payload)

        client.handle_errors(response)

        data = response.json()
        new_file_data = data['file']

        self.refresh_from_data_dict(data = new_file_data)
        return self

    def set_ordinal(self, value: int):
        self.ordinal = value


class CompoundFile:
    project: Project
    parent_file_data: dict
    child_files: List[CompoundChildFile]
    instance_list: List[dict]

    def __init__(self, project: Project, name: str, directory_id: int, instance_list: List[dict] = [], file_type: str = 'compound'):
        self.project = project
        self.name = name
        self.directory_id = directory_id
        self.child_files = []
        self.instance_list = instance_list
        self.type = file_type

    @staticmethod
    def from_dict(project: Project, dir_id: int, dict_data: dict):
        result = CompoundFile(project = project, name = dict_data.get('original_filename'), directory_id = dir_id)
        result.__refresh_compound_file_from_data_dict(data = dict_data)
        child_files = result.fetch_child_files()
        result.child_files = child_files
        return result

    def fetch_child_files(self, with_instances: bool = False) -> List[CompoundChildFile]:
        client = self.project
        endpoint = f"/api/v1/project/{self.project.project_string_id}/file/{self.id}/child-files"

        response = client.session.get(client.host + endpoint, params = {'with_instances': with_instances})

        client.handle_errors(response)

        data = response.json()
        child_files_data = data['child_files']
        print('child_files_data', child_files_data)
        result = []
        for elm in child_files_data:
            child_file = CompoundChildFile(root_file = self, child_file_type = elm.get('type'))
            child_file.refresh_from_data_dict(data = elm)
            result.append(child_file)
        return result

    def update_all(self) -> bool:
        """
            Syncs parent and child metadata with backend API.
        :return: True/False
        """
        for child in self.child_files:
            child.update()
        return True

    def __refresh_compound_file_from_data_dict(self, data: dict):
        if not data:
            return
        for key in data:
            setattr(self, key, data[key])

    def remove_child_file(self, child_file: CompoundChildFile) -> List[CompoundChildFile]:
        self.child_files.remove(child_file)
        return self.child_files

    def __create_compound_parent_file(self):
        url = f'/api/v1/project/{self.project.project_string_id}/file/new-compound'
        data = {
            'name': self.name,
            'directory_id': self.directory_id,
            'instance_list': self.instance_list,
            'type': self.type
        }
        response = self.project.session.post(url = self.project.host + url,
                                             json = data)
        self.project.handle_errors(response)
        data = response.json()
        self.parent_file_data = data.get('file')
        self.__refresh_compound_file_from_data_dict(data.get('file'))
        return data.get('file')

    def __create_child_file(self, child_file: CompoundChildFile):
        if child_file.child_file_type == 'from_local':
            return self.project.file.from_local(
                path = child_file.path,
                directory_id = self.directory_id,
                instance_list = child_file.instance_list,
                frame_packet_map = child_file.frame_packet_map,
                assume_new_instances_machine_made = child_file.assume_new_instances_machine_made,
                convert_names_to_label_files = child_file.convert_names_to_label_files,
                parent_file_id = self.parent_file_data.get('id'),
                ordinal = child_file.ordinal,
            )
        elif child_file.child_file_type == 'from_url':
            return self.project.file.from_url(
                url = child_file.path,
                media_type = child_file.media_type,
                job_id = child_file.job_id,
                job = child_file.job,
                video_split_duration = child_file.video_split_duration,
                instance_list = child_file.instance_list,
                frame_packet_map = child_file.frame_packet_map,
                parent_file_id = self.parent_file_data.get('id'),
                ordinal = child_file.ordinal,
            )
        elif child_file.child_file_type == 'from_blob_path':
            return self.project.file.from_blob_path(
                blob_path = child_file.blob_path,
                bucket_name = child_file.bucket_name,
                connection_id = child_file.connection_id,
                media_type = child_file.media_type,
                instance_list = child_file.instance_list,
                file_name = child_file.file_name,
                frame_packet_map = child_file.frame_packet_map,
                parent_file_id = self.parent_file_data.get('id'),
                ordinal = child_file.ordinal,
            )

    def add_child_from_local(self,
                             path: str,
                             instance_list: list = None,
                             frame_packet_map: dict = None,
                             assume_new_instances_machine_made: bool = True,
                             convert_names_to_label_files: bool = True,
                             ordinal: int = None):
        if ordinal is None:
            ordinal = len(self.child_files)
        new_child_file = CompoundChildFile(
            root_file = self,
            child_file_type = "from_local",
            path = path,
            directory_id = self.directory_id,
            instance_list = instance_list,
            frame_packet_map = frame_packet_map,
            assume_new_instances_machine_made = assume_new_instances_machine_made,
            convert_names_to_label_files = convert_names_to_label_files,
            ordinal = ordinal
        )
        self.child_files.append(new_child_file)
        return new_child_file

    def add_child_file_from_url(self,
                                url: str,
                                media_type: str = "image",
                                job: Job = None,
                                job_id: int = None,
                                video_split_duration: int = None,
                                instance_list: list = None,
                                frame_packet_map: dict = None,
                                ordinal: int = None):
        if ordinal is None:
            ordinal = len(self.child_files)
        new_child_file = CompoundChildFile(
            root_file = self,
            child_file_type = "from_url",
            url = url,
            media_type = media_type,
            job = job,
            directory_id = self.directory_id,
            job_id = job_id,
            video_split_duration = video_split_duration,
            instance_list = instance_list,
            frame_packet_map = frame_packet_map,
            ordinal = ordinal
        )
        self.child_files.append(new_child_file)
        return new_child_file

    def add_child_from_blob_path(self,
                                 blob_path: str,
                                 bucket_name: str,
                                 connection_id: int,
                                 media_type: str = 'image',
                                 instance_list: list = None,
                                 file_name: str = None,
                                 frame_packet_map: dict = None,
                                 ordinal: int = None
                                 ):
        if ordinal is None:
            ordinal = len(self.child_files)
        new_child_file = CompoundChildFile(
            root_file = self,
            child_file_type = "from_blob_path",
            blob_path = blob_path,
            bucket_name = bucket_name,
            connection_id = connection_id,
            directory_id = self.directory_id,
            media_type = media_type,
            instance_list = instance_list,
            file_name = file_name,
            frame_packet_map = frame_packet_map,
            ordinal = ordinal
        )
        self.child_files.append(new_child_file)
        return new_child_file

    def upload(self):
        if len(self.child_files) == 0:
            raise AssertionError('Need to add at least one child file to the compound file before calling upload()')
        parent_file_data: dict = self.__create_compound_parent_file()

        for child_file in self.child_files:
            self.__create_child_file(child_file)
        return parent_file_data
