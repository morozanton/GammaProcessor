import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, differential_evolution

INPUT_PATH = "D:\Anton\Desktop (D)\Shots_processing\AREAS_FITTED\SmallDet_Shot_14_areas_channel2700to2790.txt"


# Функции экспоненциального распада

def decay_model_single(t, A, tau):
    return A * np.exp(-t / tau)


def decay_model_double(t, A1, tau1, A2, tau2):
    return A1 * np.exp(-t / tau1) + A2 * np.exp(-t / tau2)


# Читаем данные
with open(INPUT_PATH, 'r') as inp:
    lines = inp.readlines()

time, intensity = [], []
for line in lines:
    t, i = line.split()
    time.append(int(t))
    intensity.append(float(i))

time = np.array(time)
intensity = np.array(intensity)


# Функция потерь
def loss(params, model):
    return np.sum((model(time, *params) - intensity) ** 2)


# Выбор модели: 1 или 2 изотопа
use_double_exponential = True  # Переключатель

if use_double_exponential:
    model = decay_model_double
    bounds = [(0, max(intensity)), (1, max(time)), (0, max(intensity)), (1, max(time))]
else:
    model = decay_model_single
    bounds = [(0, max(intensity)), (1, max(time))]

# Поиск оптимального начального приближения
result = differential_evolution(loss, bounds, args=(model,))

# Аппроксимация
params, covariance = curve_fit(model, time, intensity, p0=result.x)

# Вывод результатов
if use_double_exponential:
    A1_opt, tau1_opt, A2_opt, tau2_opt = params
    print(f"A1 = {A1_opt:.2f}, τ1 = {tau1_opt:.2f} sec")
    print(f"A2 = {A2_opt:.2f}, τ2 = {tau2_opt:.2f} sec")
    print(f"T_half1 = {0.693 * tau1_opt:.2f} sec")
    print(f"T_half2 = {0.693 * tau2_opt:.2f} sec\n")
    activity_0 = (A1_opt / tau1_opt) + (A2_opt / tau2_opt)
    print(f"Activity at t=0: {activity_0:.2f} Bq")

else:
    A_opt, tau_opt = params
    print(f"A = {A_opt:.2f}, τ = {tau_opt:.2f} sec")
    print(f"T_half = {0.693 * tau_opt:.2f} sec\n")
    activity_0 = A_opt / tau_opt
    print(f"Activity at t=0: {activity_0:.2f} Bq")

# График
t_fit = np.linspace(time.min(), time.max(), len(time))
I_fit = model(t_fit, *params)


plt.scatter(time, intensity, label="Input Data", color="red")
plt.plot(t_fit, I_fit, label="Approximation", linestyle="--")
plt.xlabel("Time (sec)")
plt.ylabel("Intensity")
plt.yscale("log")
plt.legend()
plt.show()
