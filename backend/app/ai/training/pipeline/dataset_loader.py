import os
import pandas as pd

# Get absolute path to training directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# datasets folder
DATASET_PATH = os.path.join(BASE_DIR, "datasets")

def load_unsw():
    """
    Load UNSW-NB15 dataset parts and combine them
    """

    print("Loading UNSW dataset...")

    files = [
        "network_data_unsw/UNSW-NB15_1.csv",
        "network_data_unsw/UNSW-NB15_2.csv",
        "network_data_unsw/UNSW-NB15_3.csv",
        "network_data_unsw/UNSW-NB15_4.csv",
    ]

    # Official UNSW feature names
    columns = [
        "srcip","sport","dstip","dsport","proto","state","dur","sbytes","dbytes",
        "sttl","dttl","sloss","dloss","service","Sload","Dload","Spkts","Dpkts",
        "swin","dwin","stcpb","dtcpb","smeansz","dmeansz","trans_depth","res_bdy_len",
        "Sjit","Djit","Stime","Ltime","Sintpkt","Dintpkt","tcprtt","synack","ackdat",
        "is_sm_ips_ports","ct_state_ttl","ct_flw_http_mthd","is_ftp_login","ct_ftp_cmd",
        "ct_srv_src","ct_srv_dst","ct_dst_ltm","ct_src_ltm","ct_src_dport_ltm",
        "ct_dst_sport_ltm","ct_dst_src_ltm","attack_cat","label"
    ]

    dataframes = []

    for file in files:

        path = os.path.join(DATASET_PATH, file)
        print(f"Reading {path}")

        df = pd.read_csv(
            path,
            names=columns,
            nrows=100000,
            low_memory=False
        )

        dataframes.append(df)

    df = pd.concat(dataframes, ignore_index=True)

    print("UNSW dataset loaded.")
    print("Shape:", df.shape)

    return df
