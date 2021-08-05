from diffgram.core.directory import Directory
from diffgram.pytorch_diffgram.diffgram_pytorch_dataset import DiffgramPytorchDataset

class SlicedDirectory(Directory):

    def __init__(self, client, original_directory: Directory, query: str):
        self.original_directory = original_directory
        self.query = query
        self.client = client

    def all_file_ids(self):
        page_num = 1
        result = []
        while page_num is not None:
            diffgram_files = self.list_files(limit = 1000,
                                             page_num = page_num,
                                             file_view_mode = 'ids_only',
                                             query = self.query)
            page_num = self.file_list_metadata['next_page']
            result = result + diffgram_files
        return result


    def to_pytorch(self, transform = None):
        """
            Transforms the file list inside the dataset into a pytorch dataset.
        :return:
        """
        file_id_list = self.all_file_ids()
        pytorch_dataset = DiffgramPytorchDataset(
            project = self.client,
            diffgram_file_id_list = file_id_list,
            transform = transform

        )
        return pytorch_dataset

