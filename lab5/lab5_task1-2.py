import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
from scipy.signal import iirfilter, filtfilt

# Часовий інтервал
t = np.linspace(0, 2 * np.pi, 1000)

# Початкові параметри
init = {
    'A': 1.0,
    'f': 1.0,
    'phi': 0.0,
    'noise_mean': 0.0,
    'noise_std': 0.2,
    'show_noise': True,
    'show_filtered': True,
}

# Поточний шум
last_noise = np.random.normal(init['noise_mean'], init['noise_std'], size=len(t))

# Чиста гармоніка
def clean_harmonic(A, f, phi):
    return A * np.sin(2 * np.pi * f * t + phi)

# Фільтрація
def apply_filter_iir(signal, cutoff=2.0, order=4):
    fs = 1 / (t[1] - t[0])
    b, a = iirfilter(order, cutoff / (0.5 * fs), btype='low', ftype='butter')
    return filtfilt(b, a, signal)

# Графік
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.25, bottom=0.35)

# Початкові дані
pure = clean_harmonic(init['A'], init['f'], init['phi'])
y0 = pure + last_noise

# Лінії
l_signal, = ax.plot(t, y0, label="Зашумлена гармоніка")
l_filtered, = ax.plot(t, apply_filter_iir(y0), 'g--', label="Фільтрована")
l_clean, = ax.plot(t, pure, 'k:', label="Чиста гармоніка")

ax.set_title("Гармоніка з шумом, фільтрацією та чиста")
ax.legend(loc="upper right")

# Слайдери
def create_slider(ax_rect, label, valmin, valmax, valinit, step=None):
    return Slider(plt.axes(ax_rect), label, valmin, valmax, valinit=valinit, valstep=step)

s_amp = create_slider([0.25, 0.30, 0.65, 0.03], 'A', 0.1, 5, init['A'])
s_freq = create_slider([0.25, 0.25, 0.65, 0.03], 'f', 0.1, 5, init['f'])
s_phase = create_slider([0.25, 0.20, 0.65, 0.03], 'ϕ', 0, 2*np.pi, init['phi'])
s_nmean = create_slider([0.25, 0.15, 0.65, 0.03], 'Шум Mean', -1, 1, init['noise_mean'])
s_nstd = create_slider([0.25, 0.10, 0.65, 0.03], 'Шум Std', 0.01, 1.0, init['noise_std'])

# Чекбокси
check_ax = plt.axes([0.05, 0.6, 0.15, 0.2])
check = CheckButtons(check_ax, ['Шум', 'Фільтр', 'Чиста'], [init['show_noise'], init['show_filtered'], True])

# Кнопка Reset 
reset_ax = plt.axes([0.05, 0.85, 0.15, 0.05])
button = Button(reset_ax, 'Reset')

# Оновлення графіка 
def update(val=None):
    global last_noise
    A = s_amp.val
    f = s_freq.val
    phi = s_phase.val
    mean = s_nmean.val
    std = s_nstd.val
    show_noise, show_filtered, show_clean = check.get_status()
  
    last_noise = np.random.normal(mean, std, size=len(t))

    pure = clean_harmonic(A, f, phi)
    signal = pure + last_noise

    l_signal.set_ydata(signal)
    l_signal.set_visible(show_noise)

    l_filtered.set_ydata(apply_filter_iir(signal))
    l_filtered.set_visible(show_filtered)

    l_clean.set_ydata(pure)
    l_clean.set_visible(show_clean)

    fig.canvas.draw_idle()

# Прив'язка слайдерів і чекбоксів
for s in [s_amp, s_freq, s_phase, s_nmean, s_nstd]:
    s.on_changed(update)
check.on_clicked(update)

# Reset 
def reset(event):
    s_amp.reset()
    s_freq.reset()
    s_phase.reset()
    s_nmean.reset()
    s_nstd.reset()
    update()

button.on_clicked(reset)

# Показ 
plt.show()
