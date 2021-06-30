from torch.utils.data import Dataset, DataLoader
import torch
import os
from imageio import imread
import numpy as np


class DiffgramPytorchDataset(Dataset):

    def __init__(self, project, diffgram_file_id_list, transform = None):
        """

        :param project (sdk.core.core.Project): A Project object from the Diffgram SDK
        :param diffgram_file_list (list): An arbitrary number of file ID's from Diffgram.
        :param transform (callable, optional): Optional transforms to be applied on a sample
        """
        self.diffgram_file_id_list = diffgram_file_id_list
        self.project = project
        self.transform = transform

    def __process_instance(self, instance):
        """
            Creates a pytorch tensor based on the instance type.
            For now we are assuming shapes here, but we can extend it
            to accept custom shapes specified by the user.
        :param instance:
        :return:
        """
        if instance['type'] == 'box':
            result = np.array([instance['x_min'], instance['y_min'], instance['x_max'], instance['y_max']])
            result = torch.tensor(result)
        return result

    def __len__(self):
        return len(self.diffgram_file_id_list)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        diffgram_file = self.project.file.get_by_id(idx, with_instances = True)
        if hasattr(diffgram_file, 'image'):
            image = imread(diffgram_file.image.get('url_signed'))
        else:
            raise Exception('Pytorch datasets only support images. Please provide only file_ids from images')

        instance_list = diffgram_file.instance_list

        # Process the instances of each file
        processed_instance_list = []
        for instance in instance_list:
            instnace_tensor = self.__process_instance(instance)
            processed_instance_list.append(instnace_tensor)
        sample = {'image': image, 'instance_list': instance_list}

        if self.transform:
            sample = self.transform(sample)

        return sample
