import matplotlib.pyplot as plt
from collections import defaultdict

# Hằng số
AVG_VEHICLE_LENGTH = 3  # mét

def calculate_accumulation(occupancy, lane_length, num_lanes):
    """
    Tính toán tích lũy (số lượng xe) trên một đoạn đường.
    Công thức: tích lũy = chiều dài làn * số làn / chiều dài trung bình xe * độ chiếm dụng / 100
    """
    return lane_length * (num_lanes / AVG_VEHICLE_LENGTH) * (occupancy / 100)

def process_mfd_data(data_by_timestamp, lane_length, num_lanes_map):
    """
    Xử lý và tổng hợp dữ liệu thô để tạo ra các điểm dữ liệu cho MFD
    theo chu kỳ 50 giây.
    """
    mfd_data_points = []
    
    # Sắp xếp các timestamp để đảm bảo xử lý theo thứ tự thời gian
    sorted_timestamps = sorted(data_by_timestamp.keys())
    
    # Lặp qua các timestamp theo từng khối 5 (5 * 10s = 50s)
    for i in range(0, len(sorted_timestamps), 5):
        chunk_timestamps = sorted_timestamps[i:i+5]
        
        # Chỉ xử lý nếu có đủ 5 timestamp trong khối
        if len(chunk_timestamps) < 5:
            continue

        window_accumulations = []
        window_flows = []

        # Xử lý từng timestamp trong khối 50s
        for timestamp in chunk_timestamps:
            records = data_by_timestamp[timestamp]
            
            records_by_detector = defaultdict(list)
            for record in records:
                records_by_detector[record.get('detector_id')].append(record)

            total_flow_at_ts = 0
            total_accumulation_at_ts = 0

            for detector_id, detector_records in records_by_detector.items():
                if not detector_records:
                    continue

                avg_occupancy = sum(rec['space_occupy_ratio'] for rec in detector_records) / len(detector_records)
                total_flow_for_detector = sum(rec['flow'] for rec in detector_records)
                num_lanes_for_detector = num_lanes_map.get(detector_id, 1)

                accumulation_for_detector = calculate_accumulation(
                    avg_occupancy,
                    lane_length,
                    num_lanes_for_detector
                )

                total_flow_at_ts += total_flow_for_detector
                total_accumulation_at_ts += accumulation_for_detector
            
            window_accumulations.append(total_accumulation_at_ts)
            window_flows.append(total_flow_at_ts)

        # Tổng hợp kết quả cho cửa sổ 50s
        # Tích lũy là trung bình cộng
        final_accumulation = sum(window_accumulations) / len(window_accumulations)
        # Lưu lượng là trung bình cộng (để giữ đúng đơn vị vehicles/hour)
        final_flow = sum(window_flows) / len(window_flows)
        
        mfd_data_points.append((final_accumulation, final_flow))
        
    return mfd_data_points

def find_mfd_setpoint(mfd_data):
    """
    Tìm điểm đặt từ dữ liệu MFD.
    Điểm đặt là điểm có tích lũy nhỏ nhất ứng với lưu lượng lớn nhất.
    """
    if not mfd_data:
        return None, None

    # Tìm lưu lượng lớn nhất
    max_flow = 0
    for acc, flow in mfd_data:
        if flow > max_flow:
            max_flow = flow

    # Tìm các điểm có lưu lượng lớn nhất
    critical_points = []
    for acc, flow in mfd_data:
        if flow == max_flow:
            critical_points.append((acc, flow))

    # Tìm điểm có tích lũy nhỏ nhất trong các điểm trên
    if not critical_points:
        return None, None
        
    setpoint = min(critical_points, key=lambda point: point[0])
    return setpoint

def plot_mfd(mfd_data, setpoint, output_path):
    """
    Vẽ đồ thị MFD và lưu ra file.
    """
    if not mfd_data:
        print("Khong co du lieu de ve.")
        return

    accumulations = [p[0] for p in mfd_data]
    flows = [p[1] for p in mfd_data]

    plt.figure(figsize=(10, 6))
    plt.scatter(accumulations, flows, label='MFD Data')
    
    if setpoint:
        plt.scatter(setpoint[0], setpoint[1], color='red', s=100, zorder=5, label=f'Setpoint\nAcc: {setpoint[0]:.2f}, Flow: {setpoint[1]}')

    plt.title('MFD (Macroscopic Fundamental Diagram)')
    plt.xlabel('Total Accumulation (vehicles)')
    plt.ylabel('Total Flow (vehicles/hour)')
    plt.grid(True)
    plt.legend()
    
    plt.savefig(output_path)
    print(f"Da luu do thi MFD tai: {output_path}")
