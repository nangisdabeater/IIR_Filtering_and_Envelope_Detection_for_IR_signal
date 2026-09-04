import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# ===== THÔNG SỐ =====
SAMPLE_RATE = 1_000_000
CARRIER_FREQ = 38_000
BIT_DURATION = 0.001
NUM_BITS = 32

# ===== 1. TẠO BIT =====
def generate_binary_sequence(num_bits):        # num_bits: Số lượng bit cần tạo (ví dụ: 32 bit).
    return np.random.randint(0, 2, num_bits)   # return (np.array): Mảng chứa các giá trị 0 và 1 ngẫu nhiên.

# ===== 2. ĐIỀU CHẾ OOK =====
def modulate_signal(binary_data, sample_rate, carrier_freq, bit_duration):          # binary_data: Mảng bit đầu vào từ hàm generate_binary_sequence.
    samples_per_bit = int(sample_rate * bit_duration)                               # sample_rate: Tần số lấy mẫu hệ thống (Hz) - ở đây là 1MHz.
    total_samples = len(binary_data) * samples_per_bit                              # carrier_freq: Tần số của sóng mang (Hz) - ở đây là 38kHz.
    t = np.linspace(0, total_samples / sample_rate, total_samples, endpoint=False)  # bit_duration: Thời gian tồn tại của 1 bit (giây) - ở đây là 1ms.

    carrier = np.sin(2 * np.pi * carrier_freq * t)                                  # samples_per_bit: Số lượng mẫu (samples) trong 1 chu kỳ bit.
    baseband = np.repeat(binary_data, samples_per_bit)                              # total_samples: Tổng số mẫu của toàn bộ chuỗi tín hiệu.

    modulated = baseband * carrier                                                  # carrier: Sóng sin thuần túy đóng vai trò sóng mang.

    return t, baseband, carrier, modulated                                         
 # modulated: Tín hiệu sau điều chế (Bật sóng mang khi bit=1, tắt khi bit=0).
 # baseband: Tín hiệu bit được "kéo dài" ra theo thời gian để nhân với sóng mang.
# ===== 3. THÊM NHIỄU =====
def add_noise(signal_in, snr_db=8):
    signal_power = np.mean(signal_in**2)                             # signal_in: Tín hiệu sạch sau điều chế.
    noise_power = signal_power / (10**(snr_db/10))                   # snr_db: Tỷ số tín hiệu trên nhiễu (dB), số càng cao tín hiệu càng sạch.

    awgn = np.random.normal(0, np.sqrt(noise_power), len(signal_in)) # signal_power: Công suất trung bình của tín hiệu gốc.

    t = np.linspace(0, len(signal_in)/SAMPLE_RATE, len(signal_in))   # noise_power: Công suất nhiễu cần thiết để đạt mức SNR mong muốn.
    low_freq_noise = 0.3 * (
        0.5*np.sin(2*np.pi*50*t) +                                   # low_freq_noise: Nhiễu tần số thấp (mô phỏng nhiễu từ lưới điện 50Hz hoặc đèn huỳnh quang).
        0.3*np.sin(2*np.pi*120*t)                                    # awgn: Nhiễu trắng (Additive White Gaussian Noise) phân bố đều mọi tần số.
    )

    return signal_in + awgn + low_freq_noise

# ===== 4. BANDPASS =====
def design_bandpass(fc, bw, fs):
    nyq = fs / 2                                           # fc: Tần số trung tâm muốn giữ lại (38kHz).
    low = (fc - bw/2) / nyq                                # bw: Băng thông (Độ rộng dải tần cho phép đi qua quanh fc).
    high = (fc + bw/2) / nyq                               # fs: Tần số lấy mẫu của hệ thống.
    b, a = signal.cheby1(4, 1, [low, high], btype='band')  # nyq: Tần số Nyquist (bằng 1/2 tần số lấy mẫu).
    return b, a                                            # b, a: Các hệ số của bộ lọc Chebyshev Type I (dùng để thực hiện lọc tín hiệu).

# ===== 5. ENVELOPE =====
def envelope_detector(sig):
    rectified = np.abs(sig)                              # rectified: Tín hiệu sau khi lấy trị tuyệt đối (chỉnh lưu toàn kỳ), lật các phần âm lên dương.

    nyq = SAMPLE_RATE / 2                                # cutoff: Tần số cắt cho bộ lọc thông thấp (để loại bỏ dao động 38kHz, giữ lại đường bao chậm).
    cutoff = 5000 / nyq                                  # env: Tín hiệu biên bao (envelope) - đường cong nối các đỉnh của sóng mang.

    b, a = signal.cheby1(4, 0.5, cutoff, btype='low')    # threshold: Ngưỡng quyết định (thường lấy 50% giá trị cực đại) để phân biệt bit 0 và 1.
    zplane(b, a, "Z-plane Lowpass Chebyshev")
    env = signal.filtfilt(b, a, rectified)

    threshold = np.max(env) * 0.5

    return env, threshold

# ===== 6. RECOVER =====
def recover_bits(envelope, threshold, num_bits, samples_per_bit):
    bits = np.zeros(num_bits, dtype=int)

    for i in range(num_bits):                                     # bits: Mảng trống để lưu kết quả khôi phục.
        seg = envelope[i*samples_per_bit:(i+1)*samples_per_bit]   # seg: Đoạn tín hiệu biên bao tương ứng với vị trí của 1 bit cụ thể.
        if np.mean(seg) > threshold:                              # np.mean(seg): Giá trị trung bình của đoạn tín hiệu đó; nếu > ngưỡng thì coi là bit 1.
            bits[i] = 1

    return bits
def zplane(b, a, title="Pole-Zero Map"):
    zeros = np.roots(b)
    poles = np.roots(a)

    plt.figure()

    # Vòng tròn đơn vị
    circle = plt.Circle((0, 0), 1, color='blue', fill=False, linestyle='dashed')
    plt.gca().add_artist(circle)

    # Vẽ zeros và poles
    plt.scatter(np.real(zeros), np.imag(zeros), marker='o', label='Zeros')
    plt.scatter(np.real(poles), np.imag(poles), marker='x', label='Poles')

    plt.title(title)
    plt.xlabel("Real")
    plt.ylabel("Imag")
    plt.legend()
    plt.grid(True)
    plt.axis('equal')

# ===== 7. PLOT =====
def plot_results(t, baseband, carrier, modulated, noisy, filtered, envelope, recovered, spb):
    t_ms = t * 1000

    plt.figure(figsize=(12, 14))

    # 1. Baseband
    plt.subplot(6,1,1)
    plt.plot(t_ms, baseband, color='blue')
    plt.title("1. Tín hiệu xung vuông (baseband)")
    plt.grid(True, linestyle='--', alpha=0.5)

    # 2. Carrier
    plt.subplot(6,1,2)
    plt.plot(t_ms, carrier, color='orange')
    plt.title("2. Sóng mang 38kHz")
    plt.grid(True, linestyle='--', alpha=0.5)

    # 3. Modulated
    plt.subplot(6,1,3)
    plt.plot(t_ms, modulated, color='green')
    plt.title("3. Tín hiệu OOK điều chế")
    plt.grid(True, linestyle='--', alpha=0.5)

    # 4. Noisy
    plt.subplot(6,1,4)
    plt.plot(t_ms, noisy, color='red')
    plt.title("4. Tín hiệu nhận (có nhiễu)")
    plt.grid(True, linestyle='--', alpha=0.5)

    # 5. Filtered
    plt.subplot(6,1,5)
    plt.plot(t_ms, filtered, color='blue')
    plt.title("5. Sau lọc thông dải (Bandpass 38kHz)")
    plt.grid(True, linestyle='--', alpha=0.5)

    # 6. Envelope + Bits
    plt.subplot(6,1,6)
    plt.plot(t_ms, envelope, color='magenta', label="Envelope")

    rec = np.repeat(recovered, spb)
    plt.plot(t_ms, rec*np.max(envelope), color='black', label="Recovered bits")

    plt.legend()
    plt.title("6. Tách biên bao & khôi phục dữ liệu")
    plt.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.show()

# ===== MAIN =====
def main():
    print("=== DSP IR OOK 38kHz ===")

    bits = generate_binary_sequence(NUM_BITS)

    t, baseband, carrier, modulated = modulate_signal(
        bits, SAMPLE_RATE, CARRIER_FREQ, BIT_DURATION
    )

    noisy = add_noise(modulated)

    b, a = design_bandpass(CARRIER_FREQ, 6000, SAMPLE_RATE)
    zplane(b, a, "Z-plane Bandpass Chebyshev")
    filtered = signal.filtfilt(b, a, noisy)

    envelope, threshold = envelope_detector(filtered)

    spb = int(SAMPLE_RATE * BIT_DURATION)
    recovered = recover_bits(envelope, threshold, NUM_BITS, spb)

    ber = np.mean(bits != recovered) * 100

    print("Bit gốc: ", "".join(map(str, bits)))
    print("Bit thu: ", "".join(map(str, recovered)))
    print(f"BER: {ber:.2f}%")

    plot_results(t, baseband, carrier, modulated, noisy, filtered, envelope, recovered, spb)

if __name__ == "__main__":
    main()