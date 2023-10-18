import os
import numpy as np
import cv2
import torch
from torch.utils.data import Dataset


class AutoDriveDataset(Dataset):
    def __init__(self, data_folder, mode, transform=None):
        self.data_folder = data_folder
        self.mode = mode
        self.transform = transform

        assert self.mode in {"train", "val"}

        if self.mode == "train":
            file_path = os.path.join(data_folder, "train.txt")
        else:
            file_path = os.path.join(data_folder, "val.txt")

        self.file_list = list()
        with open(file_path, "r") as f:
            files = f.readlines()
            for file in files:
                if file.strip() is None:
                    continue
                self.file_list.append([file.split(" ")[0], float(file.split(" ")[1])])

    def __getitem__(self, i):
        img = cv2.imread(self.file_list[i][0])
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        if self.transform:
            img = self.transform(img)
        label = self.file_list[i][1]
        label = torch.from_numpy(np.array([label])).float()
        return img, label

    def __len__(self):
        return len(self.file_list)
