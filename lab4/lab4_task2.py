import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr, spearmanr
import timeit
import os

# --- 1. Зчитування даних ---
col_names = ["mpg", "cylinders", "displacement", "horsepower", "weight",
             "acceleration", "model year", "origin", "car name"]

df = pd.read_csv(os.path.join(os.path.dirname(__file__),"auto-mpg.txt"), delim_whitespace=True, names=col_names, na_values="NA")
data_np = np.genfromtxt(os.path.join(os.path.dirname(__file__),"auto-mpg.txt"), dtype=float, usecols=range(8), missing_values="NA", filling_values=np.nan)

# --- 2. Обробка пропущених значень ---
df['horsepower'].fillna(df['horsepower'].median(), inplace=True)
df['mpg'].fillna(df['mpg'].mean(), inplace=True)
data_np = np.where(np.isnan(data_np), np.nanmedian(data_np, axis=0), data_np)

# --- 3. Нормалізація / стандартизація (ручні функції) ---
def normalize(data):
    return (data - np.min(data, axis=0)) / (np.ptp(data, axis=0))

def standardize(data):
    return (data - np.mean(data, axis=0)) / np.std(data, axis=0)

norm_np = normalize(data_np)
std_np = standardize(data_np)

df_numeric = df.drop(columns=["car name"])
norm_pd = (df_numeric - df_numeric.min()) / (df_numeric.max() - df_numeric.min())
std_pd = (df_numeric - df_numeric.mean()) / df_numeric.std()

# --- 4. Гістограма (mpg) ---
plt.hist(df['mpg'], bins=[0,10,15,20,25,30,35,40,45,50,55], edgecolor='black')
plt.title("Гістограма mpg")
plt.xlabel("mpg")
plt.ylabel("Кількість")
plt.show()

# --- 5. Графік залежності (horsepower vs mpg) ---
plt.scatter(df['horsepower'], df['mpg'], alpha=0.7)
plt.title("Залежність mpg від horsepower")
plt.xlabel("Horsepower")
plt.ylabel("MPG")
plt.grid(True)
plt.show()

# --- 6. Коефіцієнти кореляції ---
pearson_corr, _ = pearsonr(df['horsepower'], df['mpg'])
spearman_corr, _ = spearmanr(df['horsepower'], df['mpg'])
print(f"Коефіцієнт Пірсона: {pearson_corr:.4f}")
print(f"Коефіцієнт Спірмена: {spearman_corr:.4f}")

# --- 7. One-Hot Encoding по 'origin' ---
df_encoded = pd.get_dummies(df, columns=['origin'], prefix='origin')
print("One-Hot Encoding по 'origin':")
print(df_encoded.head())

# --- 8. Багатовимірна візуалізація (Pairplot) ---
sns.pairplot(df_numeric[["mpg", "horsepower", "weight", "acceleration"]])
plt.suptitle("Pairplot числових атрибутів", y=1.02)
plt.show()

# --- 9. Timeit: профілювання NumPy ---
numpy_code = r'''
import numpy as np
data = np.genfromtxt(r"C:\Users\Kiril\Desktop\Prog\zapd\lab4\auto-mpg.txt", dtype=float, usecols=range(8), missing_values="NA", filling_values=np.nan)
data = np.where(np.isnan(data), np.nanmedian(data, axis=0), data)
norm = (data - np.min(data, axis=0)) / (np.ptp(data, axis=0))
std = (data - np.mean(data, axis=0)) / np.std(data, axis=0)
'''

numpy_time = timeit.timeit(stmt=numpy_code, number=100, setup="pass")

# --- 10. Timeit: профілювання Pandas ---
pandas_code = r'''
import pandas as pd
df = pd.read_csv(r"C:\Users\Kiril\Desktop\Prog\zapd\lab4\auto-mpg.txt", delim_whitespace=True, names=["mpg", "cylinders", "displacement", "horsepower", "weight", 
                                                               "acceleration", "model year", "origin", "car name"], na_values="NA")
df["horsepower"].fillna(df["horsepower"].median(), inplace=True)
df["mpg"].fillna(df["mpg"].mean(), inplace=True)
numeric = df.drop(columns=["car name"])
norm = (numeric - numeric.min()) / (numeric.max() - numeric.min())
std = (numeric - numeric.mean()) / numeric.std()
'''

pandas_time = timeit.timeit(stmt=pandas_code, number=100, setup="pass")

# --- Вивід результатів timeit ---
print(f"\n⏱️ NumPy: час обробки за 100 повторів: {numpy_time:.4f} сек")
print(f"⏱️ Pandas: час обробки за 100 повторів: {pandas_time:.4f} сек")
