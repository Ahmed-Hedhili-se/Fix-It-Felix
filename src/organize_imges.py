import os
import shutil
import glob
import random
SOURCE_DIRS = [
    ,
]
BASE_DIR = "datasets/training_vision"
IMG_TRAIN = os.path.join(BASE_DIR, "images/train")
IMG_VAL = os.path.join(BASE_DIR, "images/val")
LBL_TRAIN = os.path.join(BASE_DIR, "labels/train")
LBL_VAL = os.path.join(BASE_DIR, "labels/val")
def organize_data():
    for d in [IMG_TRAIN, IMG_VAL, LBL_TRAIN, LBL_VAL]:
        os.makedirs(d, exist_ok=True)
    print(" Sorting images into YOLO format...")
    all_images = []
    for source in SOURCE_DIRS:
        if os.path.exists(source):
            found = glob.glob(os.path.join(source, "**", "*.jpg"), recursive=True) +                    glob.glob(os.path.join(source, "**", "*.png"), recursive=True) +                    glob.glob(os.path.join(source, "**", "*.jpeg"), recursive=True)
            all_images.extend(found)
            print(f"   Found {len(found)} images in '{os.path.basename(source)}'")
        else:
            print(f" Warning: Folder not found: {source}")
    if not all_images:
        print(" No images found! Please check your folder names.")
        return
    random.shuffle(all_images)
    split_idx = int(len(all_images) * 0.8)
    train_imgs = all_images[:split_idx]
    val_imgs = all_images[split_idx:]
    print(f" Moving {len(train_imgs)} to Train and {len(val_imgs)} to Validation...")
    def move_files(file_list, dest_img_dir, dest_lbl_dir):
        count = 0
        for img_path in file_list:
            filename = os.path.basename(img_path)
            try:
                shutil.copy(img_path, os.path.join(dest_img_dir, filename))
                label_path = os.path.splitext(img_path)[0] + ".txt"
                if os.path.exists(label_path):
                    shutil.copy(label_path, os.path.join(dest_lbl_dir, filename.replace(os.path.splitext(filename)[1], ".txt")))
                count += 1
            except Exception as e:
                print(f"Error moving {filename}: {e}")
        return count
    t_count = move_files(train_imgs, IMG_TRAIN, LBL_TRAIN)
    v_count = move_files(val_imgs, IMG_VAL, LBL_VAL)
    print(f" Success! Organized {t_count + v_count} images.")
    print(" Your data is now ready for 1_train_yolo.py")
if __name__ == "__main__":
    organize_data()