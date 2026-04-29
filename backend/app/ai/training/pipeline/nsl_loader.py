import pandas as pd
import os

def load_nsl():
    """
    Load NSL-KDD dataset
    """

    base_path = "ai/training/datasets/network_data_nsl"

    train_file = os.path.join(base_path, "KDDTrain+.csv")
    test_file = os.path.join(base_path, "KDDTest+.csv")

    print("Loading NSL-KDD dataset...")

    train_df = pd.read_csv(train_file)
    test_df = pd.read_csv(test_file)

    data = pd.concat([train_df, test_df], ignore_index=True)

    print("Dataset loaded.")
    print("Shape:", data.shape)

    return data
