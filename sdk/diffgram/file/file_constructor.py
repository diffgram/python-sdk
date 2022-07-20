from ..regular.regular import refresh_from_dict
from diffgram.file.file import File
from diffgram.convert.convert import convert_label
from diffgram.job.job import Job
import json
import os
import requests


class FileConstructor():
    """

    Construct files and communicate with client

    Caution class needs client in order to do effective communication
    with server


    """

    def __init__(self, client):

        self.client = client

    def file_from_response(
            self,
            file_dict):
        """
        file_dict, dict, file information from Project

        returns file, class File object
        """

        file = File(client = self.client)
        refresh_from_dict(file, file_dict)

        return file

    def from_local(
            self,
            path: str,
            directory_id: int = None,
            instance_list: list = None,
            frame_packet_map: dict = None,
            assume_new_instances_machine_made: bool = True,
            convert_names_to_label_files: bool = True
    ):
        """
        Create a Project file from local path

        path, string, file path

        returns file, class File object
        """

        files = {'file': (os.path.basename(path), open(path, 'rb'), 'application/octet-stream')}

        json_payload = {}

        if directory_id is None:
            directory_id = self.client.directory_id

        json_payload['directory_id'] = directory_id

        if instance_list:
            json_payload['instance_list'] = self.__validate_and_format_instance_list(
                instance_list = instance_list,
                assume_new_instances_machine_made = assume_new_instances_machine_made,
                convert_names_to_label_files = convert_names_to_label_files
            )

        if frame_packet_map:
            json_payload['frame_packet_map'] = self.__validate_and_format_frame_packet_map(
                frame_packet_map = frame_packet_map,
                assume_new_instances_machine_made = assume_new_instances_machine_made,
                convert_names_to_label_files = convert_names_to_label_files
            )

        files['json'] = (None, json.dumps(json_payload), 'application/json')

        endpoint = "/api/walrus/v1/project/" + self.client.project_string_id \
                   + "/input/from_local"

        response = self.client.session.post(
            self.client.host + endpoint,
            files = files)

        self.client.handle_errors(response)

        data = response.json()

        if data["log"]["success"] is True:
            file = self.file_from_response(file_dict = data['file'])
            return file

    def __build_packet_payload(self,
                               url: str = None,
                               media_type: str = None,
                               instance_list: list = None,
                               frame_packet_map: dict = None,
                               video_split_duration: int = None,
                               job_id: int = None,
                               job: Job = None,
                               type: str = None,
                               connection_id: int = None,
                               directory_id: int = None,
                               bucket_name: str = None,
                               file_name: str = None,
                               blob_path: str = None):
        packet = {'media': {}}
        packet['media']['url'] = url
        packet['media']['type'] = media_type

        # Existing Instances
        packet['frame_packet_map'] = frame_packet_map
        packet['type'] = type
        packet['connection_id'] = connection_id
        packet['directory_id'] = directory_id
        packet['original_filename'] = file_name
        packet['bucket_name'] = bucket_name
        packet['raw_data_blob_path'] = blob_path
        packet['instance_list'] = instance_list

        if job:
            packet["job_id"] = job.id
        else:
            packet["job_id"] = job_id

        if video_split_duration:
            packet["video_split_duration"] = video_split_duration
        return packet

    def from_blob_path(self,
                       blob_path: str,
                       bucket_name: str,
                       connection_id: int,
                       media_type: str = 'image',
                       instance_list: list = None,
                       file_name: str = None,
                       frame_packet_map: dict = None):
        """
          Bind a blob path in the given connection ID into Diffgram
        :param blob_path:
        :param bucket_name:
        :param connection_id:
        :param media_type:
        :param instance_list:
        :param frame_packet_map:
        :return:
        """
        if self.client.default_directory:
            raise Exception("Directory not set. call set_default_directory() to set upload directory.")
        directory_id = self.client.directory_id
        name = file_name
        if file_name is None:
            name = blob_path.split('/')[len(blob_path.split('/')) - 1]
        packet = self.__build_packet_payload(
            media_type = media_type,
            instance_list = instance_list,
            frame_packet_map = frame_packet_map,
            blob_path = blob_path,
            bucket_name = bucket_name,
            connection_id = connection_id,
            file_name = name,
            directory_id = directory_id,
            type = "from_blob_path"
        )
        self.from_packet(packet = packet)
        return True

    def from_url(
            self,
            url: str,
            media_type: str = "image",
            job: Job = None,
            job_id: int = None,
            video_split_duration: int = None,
            instance_list: list = None,  # for Images
            frame_packet_map: dict = None  # for Video
    ):
        """

        {'frame_packet_map' : {
            0 : instance_list,    # Where the key is the integer of the frame of the video, 0 indexed.
            6 : instance_list,
            9 : instance_list
        },

        instance_example
        {  'type': 'box', # options ['tag', 'box', 'polygon']
            label_file_id:, Integer   # Project label_file id.
                                accessible through diffgram.get_label_file_dict() See sample
            'x_max': 128, Integer
            'x_min': 1,
            'y_min': 1,
            'y_max': 128,
            'points': [] # Required for polygon more on this coming soon
            'number': 0  # A number is optional, and only relates to video instances
        }


        """

        packet = self.__build_packet_payload(
            url = url,
            media_type = media_type,
            job = job,
            job_id = job_id,
            video_split_duration = video_split_duration,
            instance_list = instance_list,
            frame_packet_map = frame_packet_map
        )
        self.from_packet(packet = packet)

        return True

    def format_packet(self):
        raise NotImplementedError

    @staticmethod
    def __media_packet_sanity_checks(packet) -> None:
        """
        Relevant to new media, ie not existing media
        """

        if type(packet) != dict:
            raise Exception("packet is not a dict")

        if "media" not in packet:
            raise Exception(" 'media' key is not defined in packet.")

        if "url" not in packet["media"]:
            raise Exception(" 'url' key is not defined in packet['media'] .")

        media_type = packet["media"].get("type", None)
        if not media_type:
            raise Exception(" 'type' key is not defined in packet['media'] use one of ['image', 'video']")

    def __validate_existing_instances(self):
        pass

    def from_packet(
            self,
            packet,
            job = None,
            convert_names_to_label_files = True,
            assume_new_instances_machine_made = True
    ):
        """
        Import single packet of data of the form:

        image_packet_example
        {'instance_list' :
            [instance_alpha,    # Array of instance dicts as defined below
                instance_bravo,
                ... n instances],
        'media' : {
            'url' : "https://something",
            'type' : 'image'   # ['image', 'video']
            }
        }

        video_packet_example
        {'frame_packet_map' : {
            0 : instance_list,
        # Where the key is the integer of the frame of the video, 0 indexed.
            6 : instance_list,
            9 : instance_list
        },
        'media' : {
            'url' : "https://something",
            'type' : 'video'
            }
        }

        instance_example
        {  'type': 'box', # options ['tag', 'box', 'polygon']
            label_file_id:, Integer   # Project label_file id.
                                accessible through diffgram.get_label_file_dict() See sample
            'x_max': 128, Integer
            'x_min': 1,
            'y_min': 1,
            'y_max': 128,
            'points': [] # Required for polygon more on this coming soon
            'number': 0  # A number is optional, and only relates to video instances
        }
        Validates basics of packet form
        and makes request to /input/packet endpoint.

        """
        file_id = packet.get('file_id')
        if not file_id:
            FileConstructor.__media_packet_sanity_checks(packet = packet)

        instance = None

        if packet.get("instance_list"):
            packet['instance_list'] = self.__validate_and_format_instance_list(
                instance_list = packet.get('instance_list'),
                assume_new_instances_machine_made = assume_new_instances_machine_made,
                convert_names_to_label_files = convert_names_to_label_files
            )

        if packet.get("frame_packet_map"):
            packet['frame_packet_map'] = self.__validate_and_format_frame_packet_map(
                frame_packet_map = packet['frame_packet_map'],
                assume_new_instances_machine_made = assume_new_instances_machine_made,
                convert_names_to_label_files = convert_names_to_label_files
            )

        # Test one of the instances
        # QUESTION Should we be testing all? User option maybe?
        # (Otherwise invalid ones get discarded when it hits API)

        # TODO due to changes, this no longer tests anything , choose new way to sample
        # instance list / packets here.

        if instance:
            instance_type = instance.get("type", None)
            if not instance_type:
                raise Exception(" type is not defined in the first instance \
									of instance_list. Options are 'tag', 'box', 'polygon'.")

            if instance_type not in ['tag', 'box', 'polygon']:
                raise Exception(" invalid instance type. Options are 'tag', 'box', 'polygon'.")

            if "label_file_id" not in instance:
                raise Exception(" label_file_id is not defined in the first instance \
									of instance_list. ")

        if job:
            packet["job_id"] = job.id
            packet["mode"] = "attach_to_job"

        endpoint = "/api/walrus/v1/project/" + \
                   self.client.project_string_id + "/input/packet"

        response = self.client.session.post(
            self.client.host + endpoint,
            json = packet)

        self.client.handle_errors(response)

        data = response.json()

        # TODO better handling input vs file

        if data["log"]["success"] is True:
            return True

        # TODO return file data here if in immediate mode
        # else return input class? / handle this properly

    # file = self.file_from_response(file_dict = data['file'])
    # return file

    def __validate_and_format_frame_packet_map(
            self,
            frame_packet_map: dict,
            assume_new_instances_machine_made: bool = True,
            convert_names_to_label_files: bool = True):
        """
        Warning: Mutates packet map
        """

        if type(frame_packet_map) != dict:
            raise Exception("frame_packet_map is not a dict")

        for frame, instance_list in frame_packet_map.items():
            if instance_list is None:
                raise Exception("instance_list cannot be None")

            if type(frame) != int:
                raise Exception("frame is not a integer. The key should be the integer frame number.")

            if type(instance_list) != list:
                raise Exception(
                    "instance_list is not a list. The value of the frame should be a list of instance dicts.")

            frame_packet_map[frame] = self.__validate_and_format_instance_list(
                instance_list = instance_list,
                assume_new_instances_machine_made = assume_new_instances_machine_made,
                convert_names_to_label_files = convert_names_to_label_files,
                check_frame_number = True
            )

        return frame_packet_map

    def __validate_and_format_instance_list(
            self,
            instance_list: list,
            assume_new_instances_machine_made: bool,
            convert_names_to_label_files: bool,
            check_frame_number: bool = False):

        FileConstructor.sanity_check_instance_list(instance_list)

        instance_list = FileConstructor.format_assumptions(
            instance_list = instance_list,
            assume_new_instances_machine_made = assume_new_instances_machine_made)

        if convert_names_to_label_files is True:
            instance_list = self.instance_list_label_strings_to_ids(
                instance_list = instance_list
            )

        if check_frame_number:
            for elm in instance_list:
                if elm.get('frame_number') is None:
                    raise Exception('All instances must have a "frame_number" key.')

        return instance_list

    def instance_list_label_strings_to_ids(self, instance_list: list):

        # Convert "name" label (ie == "cat") to Project label_file id
        for index, instance in enumerate(instance_list):
            instance = convert_label(self, instance)
            instance_list[index] = instance

        return instance_list

    @staticmethod
    def __check_for_duplicates_on_instance_list(instance_list):
        id_list = []
        duplicates = []
        for elm in instance_list:
            if elm.get('id'):
                if elm.get('id') not in id_list:
                    id_list.append(elm.get('id'))
                else:
                    duplicates.append(elm.get('id'))
        if len(duplicates) > 0:
            raise Exception(
                'Instance list must not have duplicate IDs. \n Duplicate IDs are: {}'.format(str(duplicates)))

    @staticmethod
    def sanity_check_instance_list(instance_list: list):

        if type(instance_list) != list:
            raise Exception("instance_list is not array like")

        if len(instance_list) == 0:
            raise Warning("'instance_list' is empty")

        for elm in instance_list:
            if elm is None:
                raise Exception("instance_list elements cannot be None")

        FileConstructor.__check_for_duplicates_on_instance_list(instance_list)

        return

    @staticmethod
    def format_assumptions(
            instance_list: list,
            assume_new_instances_machine_made: bool):

        if assume_new_instances_machine_made is True:
            for i in range(len(instance_list)):
                instance_list[i]['machine_made'] = True

        return instance_list

    def import_bulk(self):
        """
        Import multiple packets
        FUTURE
            Accept a dict of packets
            Each packet is defined as
            { packet_id : { packet }}

        """
        raise NotImplementedError

    def get_file_list(self, id_list: list, with_instances: bool = False):
        """
        returns Diffgram File object
        """

        raise NotImplementedError

    def file_list_exists(self, id_list, use_session = True):
        """
            Verifies that the given ID list exists inside the project.
        :param id_list:
        :return: Boolean
        """
        url = '/api/v1/project/{}/file/exists'.format(
            self.client.project_string_id
        )
        spec_dict = {
            'file_id_list': id_list
        }
        if use_session:
            response = self.client.session.post(
                self.client.host + url,
                json = spec_dict)
        else:
            response = requests.post(
                url = self.client.host + url,
                json = spec_dict,
                auth = self.client.get_http_auth()
            )
        self.client.handle_errors(response)

        response_json = response.json()

        if response_json.get('result'):
            return response_json.get('result').get('exists')

    def get_by_id(self,
                  id: int,
                  with_instances: bool = False,
                  use_session = True):
        """
        returns Diffgram File object
        """

        if not with_instances:
            endpoint = "/api/v1/file/view"

            spec_dict = {
                'file_id': id,
                'project_string_id': self.client.project_string_id,
            }

            file_response_key = 'file'

        else:
            endpoint = "/api/project/{}/file/{}/annotation/list".format(self.client.project_string_id, id)
            spec_dict = {
                'directory_id': self.client.directory_id
            }
            file_response_key = 'file_serialized'

        if use_session:
            response = self.client.session.post(
                self.client.host + endpoint,
                json = spec_dict)
        else:
            # Add Auth
            response = requests.post(self.client.host + endpoint,
                                     json = spec_dict,
                                     auth = self.client.get_http_auth())

        self.client.handle_errors(response)

        response_json = response.json()
        file_data = response_json.get(file_response_key)

        return File.new(
            client = self.client,
            file_json = file_data)
