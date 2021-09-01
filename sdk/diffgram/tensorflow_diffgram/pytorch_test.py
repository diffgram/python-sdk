import diffgram
from diffgram.pytorch_diffgram.diffgram_pytorch_dataset import DiffgramPytorchDataset

project = diffgram.Project(project_string_id = "voc-test",
                  client_id = "LIVE__p0blrrm6p5fnan5sh8ec",
                  client_secret = "d14sl5vtg672ms8rg97yp1vc9do1ao3ee2xlzktk29kbk49t8mklpt7bvnmh",
                  debug = True)

file = project.file.get_by_id(1554, with_instances = True)

diffgram_dataset = DiffgramPytorchDataset(
    project = project,
    diffgram_file_id_list = [1554]
)





# Draw
def display_masks():
    import matplotlib.pyplot as plt
    from PIL import Image, ImageDraw
    img = Image.new("L", [diffgram_dataset[0]['diffgram_file'].image['width'],
                          diffgram_dataset[0]['diffgram_file'].image['height']], 0)
    mask1 = diffgram_dataset[0]['polygon_mask_list'][0]
    mask2 = diffgram_dataset[0]['polygon_mask_list'][1]
    plt.figure()
    plt.subplot(1, 2, 1)
    # plt.imshow(img, 'gray', interpolation='none')
    plt.imshow(mask1, 'jet', interpolation = 'none', alpha = 0.7)
    plt.imshow(mask2, 'Oranges', interpolation = 'none', alpha = 0.7)
    plt.show()


# Dataset Example

dataset = project.directory.get('Default')

pytorch_dataset = dataset.to_pytorch()
tf_dataset = dataset.to_tensorflow()


sliced_dataset = dataset.slice(query = 'labels.sheep  > 0 or labels.sofa > 0')

