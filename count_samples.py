import os

FOLDER = "./nsis/"

global_count = 0

for category in os.listdir(FOLDER):
    category_count = 0
    for sample_folder in os.listdir(FOLDER + category):
        if "." not in sample_folder:
            global_count += 1
            category_count += 1
    print(f"{category} : {category_count} samples.")
print(f"Total samples : {global_count}")
