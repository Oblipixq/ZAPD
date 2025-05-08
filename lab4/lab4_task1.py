import pandas as pd
import numpy as np
import timeit
import os

# === Зчитування та підготовка даних ===
df = pd.read_csv(
    os.path.join(os.path.dirname(__file__),"household_power_consumption.txt"),
    sep=";",
    na_values="?",
    dtype=str
)

df.dropna(inplace=True)

df["DateTime"] = pd.to_datetime(df["Date"] + " " + df["Time"], dayfirst=True)

numeric_cols = [
    "Global_active_power", "Global_reactive_power", "Voltage",
    "Global_intensity", "Sub_metering_1", "Sub_metering_2", "Sub_metering_3"
]
df[numeric_cols] = df[numeric_cols].astype(float)
data_np = df[numeric_cols].to_numpy()
datetime_np = df["DateTime"].to_numpy()

# Колонкові індекси для NumPy
idx = {col: i for i, col in enumerate(numeric_cols)}

# === ЗАВДАННЯ 1: Потужність > 5 кВт ===
def task1_pandas():
    return df[df["Global_active_power"] > 5]

def task1_numpy():
    return data_np[data_np[:, idx["Global_active_power"]] > 5]

# === ЗАВДАННЯ 2: Напруга > 235 В ===
def task2_pandas():
    return df[df["Voltage"] > 235]

def task2_numpy():
    return data_np[data_np[:, idx["Voltage"]] > 235]

# === ЗАВДАННЯ 3: 19-20A та група 2 > групи 3 ===
def task3_pandas():
    mask = (df["Global_intensity"] >= 19) & (df["Global_intensity"] <= 20)
    sub = df[mask]
    return sub[sub["Sub_metering_2"] > sub["Sub_metering_3"]]

def task3_numpy():
    mask = (data_np[:, idx["Global_intensity"]] >= 19) & \
           (data_np[:, idx["Global_intensity"]] <= 20)
    sub = data_np[mask]
    return sub[sub[:, idx["Sub_metering_2"]] > sub[:, idx["Sub_metering_3"]]]

# === ЗАВДАННЯ 4: Випадкові 500000 записів, середні значення ===
def task4_pandas():
    sample = df.sample(n=500000, random_state=42)
    return sample[["Sub_metering_1", "Sub_metering_2", "Sub_metering_3"]].mean()

def task4_numpy():
    np.random.seed(42)
    indices = np.random.choice(len(data_np), size=500000, replace=False)
    sample = data_np[indices]
    return sample[:, [idx["Sub_metering_1"], idx["Sub_metering_2"], idx["Sub_metering_3"]]].mean(axis=0)

# === ЗАВДАННЯ 5: Після 18:00, потужність > 6, найбільша група 2, вибірки ===
def task5_pandas():
    after_6pm = df[df["DateTime"].dt.hour >= 18]
    high_power = after_6pm[after_6pm["Global_active_power"] > 6]
    group2_dominant = high_power[
        (high_power["Sub_metering_2"] > high_power["Sub_metering_1"]) &
        (high_power["Sub_metering_2"] > high_power["Sub_metering_3"])
    ]
    mid = len(group2_dominant) // 2
    first_half = group2_dominant.iloc[:mid].iloc[::3]
    second_half = group2_dominant.iloc[mid:].iloc[::4]
    return pd.concat([first_half, second_half])

def task5_numpy():
    hours = pd.to_datetime(datetime_np).hour
    after_6pm_mask = hours >= 18
    high_power_mask = data_np[:, idx["Global_active_power"]] > 6
    combined_mask = after_6pm_mask & high_power_mask

    selected = data_np[combined_mask]
    dt_selected = datetime_np[combined_mask]

    group2 = selected[:, idx["Sub_metering_2"]]
    group1 = selected[:, idx["Sub_metering_1"]]
    group3 = selected[:, idx["Sub_metering_3"]]

    dominant_mask = (group2 > group1) & (group2 > group3)
    final = selected[dominant_mask]

    mid = len(final) // 2
    first_half = final[:mid][::3]
    second_half = final[mid:][::4]
    return np.concatenate([first_half, second_half], axis=0)

# === Профілювання timeit ===
functions = [
    ("Завдання 1 (NumPy)", "task1_numpy()"),
    ("Завдання 1 (Pandas)", "task1_pandas()"),
    ("Завдання 2 (NumPy)", "task2_numpy()"),
    ("Завдання 2 (Pandas)", "task2_pandas()"),
    ("Завдання 3 (NumPy)", "task3_numpy()"),
    ("Завдання 3 (Pandas)", "task3_pandas()"),
    ("Завдання 4 (NumPy)", "task4_numpy()"),
    ("Завдання 4 (Pandas)", "task4_pandas()"),
    ("Завдання 5 (NumPy)", "task5_numpy()"),
    ("Завдання 5 (Pandas)", "task5_pandas()"),
]

for name, stmt in functions:
    t = timeit.timeit(stmt, globals=globals(), number=3)
    print(f"{name}: {t:.5f} сек (3 запуску)")

    if "Pandas" in name:
        result = eval(stmt)
        print(f"Результат для {name}:")

        
        if isinstance(result, pd.DataFrame):
            print(result.head(5))  
            print(f"Всього рядків: {len(result)}")
        elif isinstance(result, pd.Series):
            print(result)
        else:
            print(result)

        print("-" * 50)


