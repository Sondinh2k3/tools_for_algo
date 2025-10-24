import csv
from collections import defaultdict
import glob
import os

def load_traffic_data(data_dir):
    """
    Tải dữ liệu giao thông từ tất cả các file CSV trong một thư mục.

    Args:
        data_dir (str): Đường dẫn tới thư mục chứa các file CSV.

    Returns:
        dict: Một dictionary với key là timestamp và value là list các bản ghi (dạng dict) cho timestamp đó.
    """
    data_by_timestamp = defaultdict(list)
    csv_files = glob.glob(os.path.join(data_dir, '*.csv'))

    if not csv_files:
        print(f"Lỗi: Không tìm thấy file CSV nào trong thư mục '{data_dir}'")
        return None

    for file_path in csv_files:
        detector_id = os.path.splitext(os.path.basename(file_path))[0]
        try:
            with open(file_path, mode='r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile)
                for row in reader:
                    # Chuyển đổi kiểu dữ liệu
                    row['flow'] = int(float(row['flow']))
                    row['space_occupy_ratio'] = float(row['space_occupy_ratio'])
                    row['detector_id'] = detector_id
                    data_by_timestamp[row['timestamp']].append(row)
        except FileNotFoundError:
            print(f"Lỗi: Không tìm thấy file tại '{file_path}'")
            continue
        except Exception as e:
            print(f"Lỗi khi đọc file '{file_path}': {e}")
            continue
            
    return data_by_timestamp
