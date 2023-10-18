import torch.backends.cudnn as cudnn
import torch
from torch import nn
from torch.utils.data import DataLoader
import torchvision.transforms as transforms
from torch.utils.tensorboard import SummaryWriter

from models import AutoDriveNet
from datasets import AutoDriveDataset
from utils import *


def main():
    data_folder = "./dl/data/simulate"

    checkpoint = None
    batch_size = 200
    start_epoch = 1
    epochs = 2500
    lr = 1e-4

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    cudnn.benchmark = True
    writer = SummaryWriter()

    model = AutoDriveNet()
    optimizer = torch.optim.Adam(
        params=filter(lambda p: p.requires_grad, model.parameters()), lr=lr
    )

    model = model.to(device)
    criterion = nn.MSELoss().to(device)

    if checkpoint is not None:
        checkpoint = torch.load(checkpoint)
        start_epoch = checkpoint["epoch"] + 1
        model.load_state_dict(checkpoint["model"])
        optimizer.load_state_dict(checkpoint["optimizer"])

    transformations = transforms.Compose(
        [
            transforms.ToTensor(),
        ]
    )

    train_dataset = AutoDriveDataset(
        data_folder, mode="train", transform=transformations
    )
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=12,
        pin_memory=True,
    )

    for epoch in range(start_epoch, epochs + 1):
        model.train()
        loss_epoch = AverageMeter()

        for i, (imgs, labels) in enumerate(train_loader):
            imgs = imgs.to(device)
            labels = labels.to(device)

            pre_labels = model(imgs)
            loss = criterion(pre_labels, labels)

            optimizer.zero_grad()
            loss.backward()

            optimizer.step()

            loss_epoch.update(loss.item(), imgs.size(0))

            print("第 " + str(i) + " 个batch训练结束")

        del imgs, labels, pre_labels

        writer.add_scalar("MSE_Loss", loss_epoch.avg, epoch)
        print("epoch:" + str(epoch) + "  MSE_Loss:" + str(loss_epoch.avg))

        if epoch % 30 == 0:
            print("save model...")
            torch.save(
                {
                    "epoch": epoch,
                    "model": model.state_dict(),
                    "optimizer": optimizer.state_dict(),
                },
                "./dl/results/checkpoint.pth",
            )
    writer.close()


if __name__ == "__main__":
    main()
