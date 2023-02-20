import logging

from PIL import Image, ImageDraw
from imageio import imread
import numpy as np
import traceback
import sys
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from typing import Callable


class DiffgramDatasetIterator:
    diffgram_file_id_list: list
    max_size_cache: int = 1073741824
    pool: ThreadPoolExecutor
    project: 'Project'
    file_cache: dict
    _internal_file_list: list
    current_file_index: int
    custom_signer_fn: Callable

    def __init__(self,
                 project,
                 diffgram_file_id_list,
                 validate_ids = True,
                 max_size_cache = 1073741824,
                 max_num_concurrent_fetches = 25,
                 custom_signer_fn = None):
        """

        :param project (sdk.core.core.Project): A Project object from the Diffgram SDK
        :param diffgram_file_list (list): An arbitrary number of file ID's from Diffgram.
        """
        self.diffgram_file_id_list = []
        self.max_size_cache = 1073741824
        self.pool = None
        self.custom_signer_fn = custom_signer_fn
        self.file_cache = {}
        self._internal_file_list = []
        self.current_file_index = 0
        self.start_iterator(
            project = project,
            diffgram_file_id_list = diffgram_file_id_list,
            validate_ids = validate_ids,
            max_size_cache = max_size_cache,
            max_num_concurrent_fetches = max_num_concurrent_fetches
        )

    def start_iterator(self,
                       project,
                       diffgram_file_id_list,
                       validate_ids = True,
                       max_size_cache = 1073741824,
                       max_num_concurrent_fetches = 25):
        self.diffgram_file_id_list = diffgram_file_id_list
        self.max_size_cache = max_size_cache
        self.pool = ThreadPoolExecutor(max_num_concurrent_fetches)
        self.project = project
        self.file_cache = {}
        self._internal_file_list = []
        if validate_ids:
            self.__validate_file_ids()
        self.current_file_index = 0

    def __iter__(self):
        self.current_file_index = 0
        return self

    def __len__(self):
        return len(self.diffgram_file_id_list)

    def save_file_in_cache(self, idx, instance_data):
        # If size of cache greater than 1GB (Default)
        if sys.getsizeof(self.file_cache) > self.max_size_cache:
            keys = list(self.file_cache.keys())
            latest_keys = keys[:-10]  # Get oldest 10 elements
            for k in latest_keys:
                self.file_cache.pop(k)

        self.file_cache[idx] = instance_data

    def get_next_n_items(self, idx, num_items = 25):
        """
            Get next N items and save them to cache proactively.
        :param idx:
        :param n:
        :return:
        """
        latest_index = idx + num_items
        if latest_index >= len(self.diffgram_file_id_list):
            latest_index = len(self.diffgram_file_id_list)

        for i in range(idx + 1, latest_index):
            self.pool.submit(self.__get_file_data_for_index, (i,))
        return True

    def __get_file_data_for_index(self, idx):
        diffgram_file = self.project.file.get_by_id(self.diffgram_file_id_list[idx], with_instances = True,
                                                    use_session = False)
        instance_data = self.get_file_instances(diffgram_file)
        self.save_file_in_cache(idx, instance_data)
        return instance_data

    def __getitem__(self, idx):
        if self.file_cache.get(idx):
            return self.file_cache.get(idx)

        result = self.__get_file_data_for_index(idx)

        self.get_next_n_items(idx, num_items = 25)

        return result

    def __next__(self):
        if self.file_cache.get(self.current_file_index):
            result = self.file_cache.get(self.current_file_index)
            self.current_file_index += 1
            return result
        if self.current_file_index >= len(self.diffgram_file_id_list):
            raise StopIteration
        instance_data = self.__get_file_data_for_index(self.current_file_index)
        self.current_file_index += 1
        return instance_data

    def __validate_file_ids(self):
        if not self.diffgram_file_id_list:
            return
        result = self.project.file.file_list_exists(
            self.diffgram_file_id_list,
            use_session = False)
        if not result:
            raise Exception(
                'Some file IDs do not belong to the project. Please provide only files from the same project.')

    def set_custom_url_signer(self, signer_fn: Callable):
        self.custom_signer_fn = signer_fn

    def get_image_data(self, diffgram_file):
        MAX_RETRIES = 10
        image = None
        if hasattr(diffgram_file, 'image'):
            for i in range(0, MAX_RETRIES):
                try:
                    url = None
                    if diffgram_file.image:
                        url = diffgram_file.image.get('url_signed')
                    if diffgram_file.image and self.custom_signer_fn is not None:
                        blob_path = diffgram_file.image['url_signed_blob_path']
                        bucket_name = diffgram_file.image['bucket_name']
                        url = self.custom_signer_fn(blob_path, bucket_name)
                    if url:
                        image = imread(url)
                    break
                except Exception as e:
                    if i < MAX_RETRIES - 1:
                        continue
                    else:
                        print('Fetch Image Failed: Diffgram File ID: {}'.format(diffgram_file.id))
                        print(traceback.format_exc())
                        return None
            return image
        else:
            raise Exception('Pytorch datasets only support images. Please provide only file_ids from images')

    def gen_global_attrs(self, instance_list):
        res = []
        for inst in instance_list:
            if inst['type'] != 'global':
                continue
            res.append(inst['attribute_groups'])
        return res

    def gen_tag_instances(self, instance_list):
        result = []
        for inst in instance_list:
            if inst['type'] != 'tag':
                continue
            for k in list(inst.keys()):
                val = inst[k]
                if val is None:
                    inst.pop(k)
            elm = {
                'label': inst['label_file']['label']['name'],
                'label_file_id': inst['label_file']['id'],
            }
            result.append(elm)
        return result

    def get_file_instances(self, diffgram_file) -> dict:
        if not diffgram_file:
            return
        sample = {'diffgram_file': diffgram_file, 'type': diffgram_file.type}
        if diffgram_file.type not in ['image', 'frame', 'compound']:
            logging.warning('File type "{}" is not supported yet'.format(diffgram_file.type))
            return sample
        if diffgram_file.type in ['image', 'frame']:
            sample['image'] = self.get_image_data(diffgram_file)
        elif diffgram_file.type  is not None and diffgram_file.type.startswith('compound'):
            from diffgram.file.compound_file import CompoundFile
            compound_file: CompoundFile = diffgram_file
            sample['children'] = []
            child_files = compound_file.fetch_child_files(with_instances = True)
            print('chsad', child_files)
            for child in child_files:
                result = self.get_file_instances(child)
                sample['children'].append(result)
        instance_list = diffgram_file.instance_list
        instance_types_in_file = set([x['type'] for x in instance_list])
        # Process the instances of each file

        has_boxes = False
        has_poly = False
        has_tags = False
        has_global = False
        sample['raw_instance_list'] = instance_list
        if 'box' in instance_types_in_file:
            has_boxes = True
            x_min_list, x_max_list, y_min_list, y_max_list = self.extract_bbox_values(instance_list, diffgram_file)
            sample['x_min_list'] = x_min_list
            sample['x_max_list'] = x_max_list
            sample['y_min_list'] = y_min_list
            sample['y_max_list'] = y_max_list
        else:
            sample['x_min_list'] = []
            sample['x_max_list'] = []
            sample['y_min_list'] = []
            sample['y_max_list'] = []

        if 'polygon' in instance_types_in_file:
            has_poly = True
            mask_list = self.extract_masks_from_polygon(instance_list, diffgram_file)
            sample['polygon_mask_list'] = mask_list
        if 'tag' in instance_types_in_file:
            has_tags = True
            sample['tags'] = self.gen_tag_instances(instance_list)
        if 'global' in instance_types_in_file:
            has_global = True
            sample['global_attributes'] = self.gen_global_attrs(instance_list)

        else:
            sample['polygon_mask_list'] = []

        if len(instance_types_in_file) > 4 and has_poly and has_boxes and has_tags and has_global:
            raise NotImplementedError(
                'SDK Streaming only supports boxes and polygon, tags and global attributes types currently. If you want a new instance type to be supported please contact us!'
            )

        label_id_list, label_name_list = self.extract_labels(instance_list)
        sample['label_id_list'] = label_id_list
        sample['instance_types_in_file'] = instance_types_in_file
        sample['label_name_list'] = label_name_list

        return sample

    def extract_masks_from_polygon(self, instance_list, diffgram_file, empty_value = 0):
        nx, ny = diffgram_file.image['width'], diffgram_file.image['height']
        mask_list = []
        if nx is None or ny is None:
            return mask_list

        for instance in instance_list:
            if instance['type'] != 'polygon':
                continue
            poly = [(p['x'], p['y']) for p in instance['points']]
            img = Image.new(mode = 'L', size = (nx, ny), color = 0)  # mode L = 8-bit pixels, black and white
            draw = ImageDraw.Draw(img)
            draw.polygon(poly, outline = 1, fill = 1)
            mask = np.array(img).astype('float32')
            # mask[np.where(mask == 0)] = empty_value
            mask_list.append(mask)
        return mask_list

    def extract_labels(self, instance_list, allowed_instance_types = None):
        label_file_id_list = []
        label_names_list = []
        for inst in instance_list:
            if inst['type'] == 'global':
                continue
            if inst is None:
                continue
            if allowed_instance_types and inst['type'] in allowed_instance_types:
                continue
            label_file_id_list.append(inst['label_file']['id'])
            label_names_list.append(inst['label_file']['label']['name'])

        return label_file_id_list, label_names_list

    def extract_bbox_values(self, instance_list, diffgram_file):
        """
            Creates a pytorch tensor based on the instance type.
            For now we are assuming shapes here, but we can extend it
            to accept custom shapes specified by the user.
        :param instance:
        :return:
        """
        x_min_list = []
        x_max_list = []
        y_min_list = []
        y_max_list = []

        for inst in instance_list:
            if inst['type'] != 'box':
                continue
            x_min_list.append(inst['x_min'])
            x_max_list.append(inst['x_max'])
            y_min_list.append(inst['y_min'])
            y_max_list.append(inst['y_max'])

        return x_min_list, x_max_list, y_min_list, y_max_list
