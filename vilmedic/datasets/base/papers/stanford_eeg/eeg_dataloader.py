import numpy as np
import torch

import pickle

from torch.utils.data import Dataset, DataLoader
from eeg_dataloader_utils import *

from vilmedic.blocks.vision.eeg_modeling.dense_inception import DenseInception


class EegTextDataset(Dataset):
    """
    Pytorch dataset that loads both EEG clips and accompanying text report
    """

    def __init__(
        self,
        stanford_dataset_dir,
        lpch_dataset_dir,
        reports_dict_pth,
        split_type,
        clip_len=12,
    ):
        """
        Store the filenames of the seizures to use.
        Args:
            stanford_dataset_dir/lpch_dataset_dir: (string) directory containing the EEG files for stanford/lpch data
            reports_dict_pth: (string) path containing the reports dict
            split_type: (string) whether train, val, or test set
            clip_len: (int) how long EEG clip input is in seconds
        """

        with open(reports_dict_pth, "rb") as pkl_f:
            self.reports_dict = pickle.load(pkl_f)

        self.file_names = list(self.reports_dict.keys())

        eeg_file_tuples = compute_stanford_file_tuples(
            stanford_dataset_dir, lpch_dataset_dir, ["train", "dev"]
        )

        # create file_tuple dict
        eeg_file_tuple_dict = {}
        for entry in eeg_file_tuples:
            file_name = entry[0].split("/")[-1].split(".eeghdf")[0]
            # filter eeg_file_tuples to only ones with reports
            if file_name in self.file_names:
                eeg_file_tuple_dict[file_name] = entry
        self.eeg_file_tuple_dict = eeg_file_tuple_dict

        self.clip_len = clip_len

        # TODO: deal with train/val/test splits!!

    def __len__(self):
        return len(self.file_names)

    def __getitem__(self, idx):
        file_name = self.file_names[idx]

        eeg_text = self.reports_dict[file_name]

        file_path, clip_idx, split = self.eeg_file_tuple_dict[file_name]
        eeg_clip = stanford_eeg_loader(file_path, clip_idx, split, self.clip_len)

        return eeg_clip, eeg_text


def test_dataloader_and_encoder():
    stanford_dataset_dir = "/media/4tb_hdd/eeg_data/stanford/stanford_mini"
    lpch_dataset_dir = "/media/4tb_hdd/eeg_data/lpch/lpch"
    reports_dict_pth = "/media/nvme_data/eeg_reports/findings_5k_reports_dict.pkl"

    eeg_ds = EegTextDataset(
        stanford_dataset_dir, lpch_dataset_dir, reports_dict_pth, split_type="train"
    )

    eeg_clip, eeg_text = eeg_ds[0]

    model = DenseInception(data_shape=eeg_clip.shape)

    x = torch.Tensor(eeg_clip.T).unsqueeze(0)
    y = model(x)  ## KS: NOT WORKING RIGHT NOW, WILL FIX

    breakpoint()


if __name__ == "__main__":
    test_dataloader_and_encoder()
