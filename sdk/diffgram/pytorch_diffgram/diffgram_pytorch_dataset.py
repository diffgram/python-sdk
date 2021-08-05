from torch.utils.data import Dataset, DataLoader
import torch
import os
from imageio import imread
import numpy as np
import scipy as sp
from PIL import Image, ImageDraw


class DiffgramPytorchDataset(Dataset):

    def __init__(self, project, diffgram_file_id_list = None, transform = None):
        """

        :param project (sdk.core.core.Project): A Project object from the Diffgram SDK
        :param diffgram_file_list (list): An arbitrary number of file ID's from Diffgram.
        :param transform (callable, optional): Optional transforms to be applied on a sample
        """
        self.diffgram_file_id_list = diffgram_file_id_list

        self.project = project
        self.transform = transform
        self._internal_file_list = []
        self.__validate_file_ids()

    def __validate_file_ids(self):
        result = self.project.file.file_list_exists(self.diffgram_file_id_list)
        if not result:
            raise Exception(
                'Some file IDs do not belong to the project. Please provide only files from the same project.')

    def __extract_masks_from_polygon(self, instance_list, diffgram_file, empty_value = 0):
        nx, ny = diffgram_file.image['width'], diffgram_file.image['height']
        mask_list = []
        for instance in instance_list:
            if instance['type'] != 'polygon':
                continue
            poly = [(p['x'], p['y']) for p in instance['points']]

            img = Image.new(mode = 'L', size = (nx, ny), color = 0)  # mode L = 8-bit pixels, black and white
            draw = ImageDraw.Draw(img)
            print()
            draw.polygon(poly, outline = 1, fill = 1)
            mask = np.array(img).astype('float32')
            # mask[np.where(mask == 0)] = empty_value
            print('mask', len(mask))
            mask_list.append(mask)
        return mask_list

    def __extract_bbox_values(self, instance_list, diffgram_file):
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
            x_min_list.append(inst['x_min'] / diffgram_file.image['width'])
            x_max_list.append(inst['x_max'] / diffgram_file.image['width'])
            y_min_list.append(inst['y_min'] / diffgram_file.image['width'])
            y_max_list.append(inst['y_max'] / diffgram_file.image['width'])

        return x_min_list, x_max_list, y_min_list, y_max_list

    def __len__(self):
        return len(self.diffgram_file_id_list)

    def __get_next_page_of_data(self):
        raise NotImplementedError

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        diffgram_file = self.project.file.get_by_id(self.diffgram_file_id_list[idx], with_instances = True)
        if hasattr(diffgram_file, 'image'):
            image = imread(diffgram_file.image.get('url_signed'))
        else:
            raise Exception('Pytorch datasets only support images. Please provide only file_ids from images')

        instance_list = diffgram_file.instance_list
        instance_types_in_file = set([x['type'] for x in instance_list])
        # Process the instances of each file
        processed_instance_list = []
        sample = {'image': image, 'diffgram_file': diffgram_file}
        if 'box' in instance_types_in_file:
            x_min_list, x_max_list, y_min_list, y_max_list = self.__extract_bbox_values(instance_list, diffgram_file)
            sample['x_min_list'] = torch.Tensor(x_min_list)
            sample['x_max_list'] = torch.Tensor(x_max_list)
            sample['y_min_list'] = torch.Tensor(y_min_list)
            sample['y_max_list'] = torch.Tensor(y_max_list)
        if 'polygon' in instance_types_in_file:
            mask_list = self.__extract_masks_from_polygon(instance_list, diffgram_file)
            sample['polygon_mask_list'] = mask_list
        if self.transform:
            sample = self.transform(sample)

        return sample
