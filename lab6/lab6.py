import numpy as np
import matplotlib.pyplot as plt

# Генерація даних
np.random.seed(0)
true_k, true_b = 2.5, -1.0
x = np.linspace(-10, 10, 100)
noise = np.random.normal(0, 3, size=x.shape)
y = true_k * x + true_b + noise

# Метод найменших квадратів
def manual_least_squares(x, y):
    x_mean = sum(x) / len(x)
    y_mean = sum(y) / len(y)
    numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
    denominator = sum((xi - x_mean)**2 for xi in x)
    beta1 = numerator / denominator
    beta0 = y_mean - beta1 * x_mean
    return beta1, beta0

k_hat, b_hat = manual_least_squares(x, y)

# polyfit
k_poly, b_poly = np.polyfit(x, y, 1)

# Візуалізація
plt.figure(figsize=(10, 6))
plt.scatter(x, y, label='Дані', color='lightgray')
plt.plot(x, true_k * x + true_b, label='Початкова пряма', linestyle='dotted')
plt.plot(x, k_hat * x + b_hat, label='МНК', color='blue')
plt.plot(x, k_poly * x + b_poly, label='np.polyfit', color='green', linestyle='--')
plt.legend()
plt.title('Метод найменших квадратів (формула)')
plt.xlabel('x')
plt.ylabel('y')
plt.grid(True)
plt.show()

print("Формули МНК вручну:     k = {:.3f}, b = {:.3f}".format(k_hat, b_hat))
print("polyfit (перевірка):    k = {:.3f}, b = {:.3f}".format(k_poly, b_poly))
print("Початкові параметри:    k = {:.3f}, b = {:.3f}".format(true_k, true_b))



# Метод градієнтного спуску
def gradient_descent(x, y, learning_rate=0.001, n_iter=1000):
    k, b = 0.0, 0.0
    n = len(x)
    errors = []

    for _ in range(n_iter):
        y_pred = k * x + b
        error = y_pred - y
        cost = (1 / n) * np.sum(error ** 2)
        errors.append(cost)

        # Градієнти
        dk = (2 / n) * np.sum(error * x)
        db = (2 / n) * np.sum(error)

        # Оновлення параметрів
        k -= learning_rate * dk
        b -= learning_rate * db

    return k, b, errors


k_gd, b_gd, error_history = gradient_descent(x, y, learning_rate=0.01, n_iter=1000)


plt.figure(figsize=(10, 6))
plt.scatter(x, y, label='Дані', color='lightgray')
plt.plot(x, true_k * x + true_b, label='Початкова пряма', linestyle='dotted')
plt.plot(x, k_hat * x + b_hat, label='МНК', color='blue')
plt.plot(x, k_gd * x + b_gd, label='Градієнтний спуск', color='red')
plt.legend()
plt.title('Завдання 2: Градієнтний спуск')
plt.xlabel('x')
plt.ylabel('y')
plt.grid(True)
plt.show()

# Графік похибки
plt.figure(figsize=(8, 4))
plt.plot(error_history)
plt.title('Графік зменшення помилки (MSE) під час ГСП')
plt.xlabel('Ітерація')
plt.ylabel('MSE')
plt.grid(True)
plt.show()

