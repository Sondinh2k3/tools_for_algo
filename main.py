from collections import defaultdict
from utils.data_handler import load_traffic_data
from mfd import process_mfd_data, find_mfd_setpoint, plot_mfd

# --- Cấu hình ---
DATA_DIR_PATH = 'data'
OUTPUT_PLOT_PATH = 'output/mfd_plot.png'

# Giả định các tham số này là hằng số cho hệ thống
LANE_LENGTH_M = 50  # mét
# NUM_LANES sẽ được xác định từ dữ liệu

def main():
    """
    Hàm chính của chương trình.
    """
    print("Chuong trinh tinh toan tham so dieu khien den giao thong")
    print("--- Bat dau ---")

    # 1. Tai du lieu tu file
    print(f"Dang tai du lieu tu thu muc '{DATA_DIR_PATH}'...")
    data_by_timestamp = load_traffic_data(DATA_DIR_PATH)
    
    if not data_by_timestamp:
        print("--- Ket thuc do loi ---")
        return

    # 2. Xác định số làn cho mỗi detector
    lanes_per_detector = defaultdict(set)
    for records in data_by_timestamp.values():
        for record in records:
            try:
                lanes_per_detector[record['detector_id']].add(record['lane'])
            except KeyError:
                pass
    
    # Tạo một map từ detector_id -> số làn
    num_lanes_map = {detector: len(lanes) for detector, lanes in lanes_per_detector.items()}

    if not num_lanes_map:
        print("Khong the xac dinh so lan cho bat ky detector nao. Thoat.")
        return
        
    print(f"So lan duong cho moi detector: {num_lanes_map}")

    # 3. Thuc hien cac tinh toan
    print("Dang xu ly du lieu MFD...")
    mfd_points = process_mfd_data(data_by_timestamp, LANE_LENGTH_M, num_lanes_map)
    
    print("Dang tim diem dat (setpoint)...")
    setpoint = find_mfd_setpoint(mfd_points)

    if not setpoint:
        print("Khong tim thay diem dat.")
        print("--- Ket thuc ---")
        return
        
    accumulation_setpoint, max_flow = setpoint
    print("\n--- KET QUA ---")
    print(f"Luu luong toi da (Max Flow): {max_flow} xe/gio")
    print(f"Diem dat tich luy (Accumulation Setpoint): {accumulation_setpoint:.2f} xe")
    print("Day la gia tri tich luy nho nhat ung voi luu luong toi da.")
    print("---------------")

    # 4. Xuat ket qua (ve do thi)
    print(f"Dang ve do thi va luu tai '{OUTPUT_PLOT_PATH}'...")
    plot_mfd(mfd_points, setpoint, OUTPUT_PLOT_PATH)
    
    print("\n--- Hoàn thành ---")


if __name__ == "__main__":
    main()