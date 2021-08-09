import os

import numpy as np
import scipy as sp

from diffgram.core.diffgram_dataset_iterator import DiffgramDatasetIterator


class DiffgramPytorchDataset(DiffgramDatasetIterator, Dataset):

    def __init__(self, project, diffgram_file_id_list = None, transform = None):
        """

        :param project (sdk.core.core.Project): A Project object from the Diffgram SDK
        :param diffgram_file_list (list): An arbitrary number of file ID's from Diffgram.
        :param transform (callable, optional): Optional transforms to be applied on a sample
        """
        super(DiffgramDatasetIterator, self).__init__(project, diffgram_file_id_list)
        global torch, Dataset, DataLoader
        try:
            import torch as torch  # type: ignore
            from torch.utils.data import Dataset, DataLoader
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "'torch' module should be installed to convert the Dataset into pytorch format"
            )
        self.diffgram_file_id_list = diffgram_file_id_list

        self.project = project
        self.transform = transform
        self.__validate_file_ids()

    def __len__(self):
        return len(self.diffgram_file_id_list)

    def __get_next_page_of_data(self):
        raise NotImplementedError

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        diffgram_file = self.project.file.get_by_id(self.diffgram_file_id_list[idx], with_instances = True)

        sample = self.get_file_instances(diffgram_file)
        if 'x_min_list' in sample:
            sample['x_min_list'] = torch.Tensor(sample['x_min_list'])
        if 'x_max_list' in sample:
            sample['x_max_list'] = torch.Tensor(sample['x_max_list'])
        if 'y_min_list' in sample:
            sample['y_min_list'] = torch.Tensor(sample['y_min_list'])
        if 'y_max_list' in sample:
            sample['y_max_list'] = torch.Tensor(sample['y_max_list'])

        if self.transform:
            sample = self.transform(sample)

        return sample
