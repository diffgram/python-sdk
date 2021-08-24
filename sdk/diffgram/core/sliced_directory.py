from diffgram.core.directory import Directory
from diffgram.pytorch_diffgram.diffgram_pytorch_dataset import DiffgramPytorchDataset
from diffgram.tensorflow_diffgram.diffgram_tensorflow_dataset import DiffgramTensorflowDataset


class SlicedDirectory(Directory):

    def __init__(self, client, original_directory: Directory, query: str):
        self.original_directory = original_directory
        self.query = query
        self.client = client
        # Share the same ID from the original directory as this is just an in-memory construct for better semantics.
        self.id = original_directory.id
        self.file_id_list = self.all_file_ids()
        super(Directory, self).__init__(self.client, self.file_id_list)

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

        pytorch_dataset = DiffgramPytorchDataset(
            project = self.client,
            diffgram_file_id_list = self.file_id_list,
            transform = transform

        )
        return pytorch_dataset

    def to_tensorflow(self):
        file_id_list = self.all_file_ids()
        diffgram_tensorflow_dataset = DiffgramTensorflowDataset(
            project = self.client,
            diffgram_file_id_list = file_id_list
        )
        tf_dataset = diffgram_tensorflow_dataset.get_dataset_obj()
        return tf_dataset
