from torch.utils.data import Dataset, DataLoader
import torch as torch  # type: ignore
from diffgram.core.diffgram_dataset_iterator import DiffgramDatasetIterator


class DiffgramPytorchDataset(DiffgramDatasetIterator, Dataset):

    def __init__(self, project, diffgram_file_id_list = None, transform = None, validate_ids = True):
        """

        :param project (sdk.core.core.Project): A Project object from the Diffgram SDK
        :param diffgram_file_list (list): An arbitrary number of file ID's from Diffgram.
        :param transform (callable, optional): Optional transforms to be applied on a sample
        """
        super(DiffgramPytorchDataset, self).__init__(project, diffgram_file_id_list, validate_ids)

        self.diffgram_file_id_list = diffgram_file_id_list

        self.project = project
        self.transform = transform

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
