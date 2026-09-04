# DỰ ÁN: PHÁT HIỆN VÀ XỬ LÍ TÍN HIỆU HỒNG NGOẠI Ở ĐIỀU KHIỂN TỪ XA

### 📖 Giới thiệu
Dự án này tập trung vào việc mô phỏng toàn bộ chu trình truyền, nhận và xử lý tín hiệu hồng ngoại (IR) từ điều khiển từ xa. Tín hiệu điều khiển thực chất là các chuỗi dữ liệu số được điều chế trên sóng mang tần số 38kHz để tránh nhiễu từ môi trường. Bằng việc ứng dụng các thuật toán Xử lý tín hiệu số (DSP) trên MATLAB, hệ thống có thể trích xuất thành công mã lệnh từ một tín hiệu thô đã bị can nhiễu nặng nề.

### ⚙️ Thông số hệ thống
- **Tần số lấy mẫu (fs):** 1 MHz
- **Tần số sóng mang (fc):** 38 kHz
- **Thời gian 1 bit (Tb):** 1 ms
- **Định dạng dữ liệu:** Chuỗi 32 bit ngẫu nhiên (OOK Modulation)
- **Mô phỏng nhiễu:** Nhiễu AWGN (SNR 8dB) & Nhiễu ánh sáng môi trường (50Hz/120Hz)

### 🚀 Luồng xử lý tín hiệu (Workflow)
1. **Baseband:** Tạo chuỗi 32 bit ngẫu nhiên thành tín hiệu xung vuông lý tưởng.
2. **Điều chế OOK:** Trộn xung vuông với sóng mang 38 kHz.
3. **Kênh truyền:** Thêm nhiễu AWGN và nhiễu đèn huỳnh quang 50/120Hz.
4. **Lọc thông dải (Band-pass Filter):** Dùng bộ lọc IIR Chebyshev Loại 1 (bậc 4, băng thông 6kHz) kết hợp lọc triệt tiêu trễ pha (zero-phase) để tách sóng mang.
5. **Tách biên bao (Envelope Detection):** Chỉnh lưu toàn sóng (abs) và dùng bộ lọc thông thấp (Low-pass Filter 5kHz) để khôi phục xung vuông.
6. **Khôi phục dữ liệu:** Sử dụng ngưỡng quyết định động (50% biên độ đỉnh) để tính trung bình năng lượng và chốt mức logic, tính toán BER.

### 💻 Hướng dẫn chạy mô phỏng

**Yêu cầu hệ thống:**
- MATLAB 2025a (hoặc các phiên bản tương thích).
- Signal Processing Toolbox (Cần thiết cho các hàm `cheby1`, `filtfilt`).

**Các bước thực hiện:**
1. Clone repository này về máy:
   ```bash
   git clone [https://github.com/your-username/ir-remote-dsp.git](https://github.com/your-username/ir-remote-dsp.git)
2. Mở MATLAB và trỏ thư mục hiện tại (Current Folder) về thư mục vừa clone.

3. Mở và chạy file `code_matlab.m`:

Gõ lệnh `run('code_matlab.m')` trong Command Window hoặc nhấn nút Run trên giao diện.

4. Quan sát kết quả trên Command Window (Bit gốc, Bit thu, BER) và phân tích biểu đồ 6 bước xử lý tín hiệu.
