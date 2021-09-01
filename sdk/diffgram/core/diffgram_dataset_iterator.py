from PIL import Image, ImageDraw
from imageio import imread
import numpy as np

class DiffgramDatasetIterator:

    def __init__(self, project, diffgram_file_id_list, validate_ids = True):
        """

        :param project (sdk.core.core.Project): A Project object from the Diffgram SDK
        :param diffgram_file_list (list): An arbitrary number of file ID's from Diffgram.
        """
        self.diffgram_file_id_list = diffgram_file_id_list

        self.project = project
        self._internal_file_list = []
        if validate_ids:
            self.__validate_file_ids()
        self.current_file_index = 0

    def __iter__(self):
        self.current_file_index = 0
        return self

    def __len__(self):
        return len(self.diffgram_file_id_list)

    def __getitem__(self, idx):
        diffgram_file = self.project.file.get_by_id(self.diffgram_file_id_list[idx], with_instances = True)
        instance_data = self.get_file_instances(diffgram_file)
        return instance_data

    def __next__(self):
        file_id = self.diffgram_file_id_list[self.current_file_index]
        diffgram_file = self.project.file.get_by_id(file_id, with_instances = True)
        instance_data = self.get_file_instances(diffgram_file)
        self.current_file_index += 1
        return instance_data

    def __validate_file_ids(self):
        if not self.diffgram_file_id_list:
            return
        result = self.project.file.file_list_exists(self.diffgram_file_id_list)
        if not result:
            raise Exception(
                'Some file IDs do not belong to the project. Please provide only files from the same project.')

    def get_image_data(self, diffgram_file):
        if hasattr(diffgram_file, 'image'):
            image = imread(diffgram_file.image.get('url_signed'))
            return image
        else:
            raise Exception('Pytorch datasets only support images. Please provide only file_ids from images')

    def get_file_instances(self, diffgram_file):
        if diffgram_file.type not in ['image', 'frame']:
            raise NotImplementedError('File type "{}" is not supported yet'.format(diffgram_file['type']))

        image = self.get_image_data(diffgram_file)
        instance_list = diffgram_file.instance_list
        instance_types_in_file = set([x['type'] for x in instance_list])
        # Process the instances of each file
        sample = {'image': image, 'diffgram_file': diffgram_file}
        has_boxes = False
        has_poly = False
        if 'box' in instance_types_in_file:
            has_boxes = True
            x_min_list, x_max_list, y_min_list, y_max_list = self.extract_bbox_values(instance_list, diffgram_file)
            sample['x_min_list'] = x_min_list
            sample['x_max_list'] = x_max_list
            sample['y_min_list'] = y_min_list
            sample['y_max_list'] = y_max_list

        if 'polygon' in instance_types_in_file:
            has_poly = True
            mask_list = self.extract_masks_from_polygon(instance_list, diffgram_file)
            sample['polygon_mask_list'] = mask_list

        if len(instance_types_in_file) > 2 and has_boxes and has_boxes:
            raise NotImplementedError(
                'SDK only supports boxes and polygon types currently. If you want a new instance type to be supported please contact us!'
            )

        label_id_list, label_name_list = self.extract_labels(instance_list)
        sample['label_id_list'] = label_id_list
        sample['label_name_list'] = label_name_list

        return sample

    def extract_masks_from_polygon(self, instance_list, diffgram_file, empty_value = 0):
        nx, ny = diffgram_file.image['width'], diffgram_file.image['height']
        mask_list = []
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
