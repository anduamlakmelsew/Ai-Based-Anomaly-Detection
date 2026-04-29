import pandas as pd

base_path = "datasets/web_csic2010/Web-Application-Attack-Datasets/OriginalDataSets/csic_2010/"

files = {
    "normal_train": (base_path + "normalTrafficTraining.txt", 0),
    "normal_test": (base_path + "normalTrafficTest.txt", 0),
    "anomalous": (base_path + "anomalousTrafficTest.txt", 1),
}

def parse_requests(file_path, label):
    requests = []
    current_request = []

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()

            if line == "":
                if current_request:
                    requests.append((" ".join(current_request), label))
                    current_request = []
            else:
                current_request.append(line)

        # catch last request
        if current_request:
            requests.append((" ".join(current_request), label))

    return requests

# Build dataset
all_data = []

for name, (path, label) in files.items():
    print(f"Processing {name}...")
    all_data.extend(parse_requests(path, label))

df = pd.DataFrame(all_data, columns=["request", "label"])

print("Dataset shape:", df.shape)

# Remove duplicates
df = df.drop_duplicates()

print("After dedup:", df.shape)

# Save
df.to_parquet("processed/web_clean.parquet")

print("✅ Clean dataset ready!")
