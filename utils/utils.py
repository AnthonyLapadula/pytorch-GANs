import matplotlib.pyplot as plt
import numpy as np
import torch
from torchvision import transforms, datasets
from torch.utils.data import DataLoader
from torch.optim import Adam


from .constants import LATENT_SPACE_DIM
from models.definitions.vanilla_gan_nets import DiscriminatorNet, GeneratorNet


def get_mnist_dataset(dataset_path):
    # It's good to normalize the images to [-1, 1] range https://github.com/soumith/ganhacks
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((.5,), (.5,))
    ])
    return datasets.MNIST(root=dataset_path, train=True, download=True, transform=transform)


def get_mnist_data_loader(dataset_path, batch_size):
    mnist_dataset = get_mnist_dataset(dataset_path)
    mnist_data_loader = DataLoader(mnist_dataset, batch_size=batch_size, shuffle=True, drop_last=True)
    return mnist_data_loader


def get_gaussian_latent_batch(batch_size, device):
    return torch.randn((batch_size, LATENT_SPACE_DIM), device=device)


def plot_single_img_from_tensor_batch(batch):
    img = batch[0].numpy()
    img = np.repeat(np.moveaxis(img, 0, 2), 3, axis=2)
    print(img.shape, np.min(img), np.max(img))
    plt.imshow(img)
    plt.show()


def get_vanilla_nets(device):
    d_net = DiscriminatorNet().train().to(device)
    g_net = GeneratorNet().train().to(device)
    return d_net, g_net


# Tried SGD for the discriminator, had problems tweaking it - Adam simply works nicely but default lr 1e-3 won't work!
# I had to train discriminator more (4 to 1 schedule worked) to get it working with default lr, still got worse results.
# 0.0002 and 0.5, 0.999 are from the DCGAN paper it works here nicely!
def prepare_optimizers(d_net, g_net):
    d_opt = Adam(d_net.parameters(), lr=0.0002, betas=(0.5, 0.999))
    g_opt = Adam(g_net.parameters(), lr=0.0002, betas=(0.5, 0.999))
    return d_opt, g_opt


def same_weights(model1, model2):
    for p1, p2 in zip(model1.parameters(), model2.parameters()):
        if p1.data.ne(p2.data).sum() > 0:
            return False
    return True