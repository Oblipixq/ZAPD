import urllib.request 
import pandas as pd
import os
from datetime import datetime as dt

for area_id in range(1, 26):  
    url = f"https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={area_id}&year1=1981&year2=2024&type=Mean"
    time = dt.now().strftime("%d%m%Y%H%M%S")
    filename = f'vhi_id_{area_id}_{time}.csv'
    if os.path.exists(filename):
        print(f"Файл для області {area_id} вже існує: {filename}. Пропускаємо завантаження.")
        continue
    
    try:
        vhi_url = urllib.request.urlopen(url)
        with open(filename, 'wb') as out:
            out.write(vhi_url.read())
            out.close
        print(f"VHI дата для області {area_id} завантажена/збережена у {filename}")
    except Exception as e:
        print(f"Помилка для області {area_id}: {e}")

def read_vhi_from_csv(directory):
    data_frames = []
    for filename in os.listdir(directory):
        if filename.startswith('vhi_id_') and filename.endswith('.csv'):
            filepath = os.path.join(directory, filename)
            try:
                area_id = int(filename.split('_')[2])
            except (IndexError, ValueError) as e:
                print(f"Невірний формат імені файлу: {filename}. Видаляємо файл.")
                os.remove(filepath) 
                continue
            df = pd.read_csv(filepath, index_col=False, header=1)
            df['area_ID'] = area_id  
            
            data_frames.append(df)    
    return pd.concat(data_frames, ignore_index=True)

directory = '.' 
vhi_data = read_vhi_from_csv(directory)
vhi_data.columns = vhi_data.columns.str.strip().str.replace('<br>', '', regex=True)
vhi_data['year'] = vhi_data['year'].astype(str).str.extract(r'(\d+)')
vhi_data = vhi_data.dropna(subset=['year']).copy() 
vhi_data['year'] = vhi_data['year'].astype(int) 
# print("Стовпці у фреймі:")
# print(vhi_data.columns)

area_map = {
    1: "Вінницька", 2: "Волинська", 3: "Дніпропетровська", 4: "Донецька",
    5: "Житомирська", 6: "Закарпатська", 7: "Запорізька", 8: "Івано-Франківська",
    9: "Київська", 10: "Кіровоградська", 11: "Луганська", 12: "Львівська",
    13: "Миколаївська", 14: "Одеська", 15: "Полтавська", 16: "Рівненська",
    17: "Сумська", 18: "Тернопільська", 19: "Харківська", 20: "Херсонська",
    21: "Хмельницька", 22: "Черкаська", 23: "Чернівецька", 24: "Чернігівська",
    25: "Республіка Крим"
}

def replace_area_indices(df, map):
    if 'area_ID' in df.columns:
        df['area'] = df['area_ID'].map(map) 
    else:
        print("Помилка: стовпець 'area_ID' не знайдено у фреймі даних.")
    return df

vhi_data = replace_area_indices(vhi_data, area_map)

def analyze_vhi_data(df, area, year):
    area_data = df[(df['area'] == area) & (df['year'] == year)]
    if not area_data.empty:
        print("#"*70)
        print(f"Область: {area}, Рік: {year}")
        print(f"Мін VHI: {area_data['VHI'].min()}, Макс VHI: {area_data['VHI'].max()}, Серднє: {area_data['VHI'].mean()}, Медіана VHI: {area_data['VHI'].median()}")
        print("#"*70)
    else:
        print(f"Нема інформації для {area} обл in {year}")

def user_input_for_vhi(df):
    print("#"*70)
    print("Доступні області:")
    for id, area in area_map.items():
        print(f"{id}: {area}")
    
    area_id = int(input("Введіть номер області (1-25): "))
    year = int(input("Введіть рік: "))
    
    if area_id not in area_map:
        print("Невірний номер області.")
        return
    
    area = area_map[area_id]
    analyze_vhi_data(df, area, year)

user_input_for_vhi(vhi_data)

def vhi_for_range(df):
    print("Доступні області:")
    for id, area in area_map.items():
        print(f"{id}: {area}")
    
    area_input = input("Введіть номери областей через кому (1,3,5): ")
    area_list = [int(x.strip()) for x in area_input.split(',')]
    
    start_year = int(input("Введіть початковий рік: "))
    end_year = int(input("Введіть кінцевий рік: "))
    
    invalid_area = [a for a in area_list if a not in area_map]
    if invalid_area:
        print(f"Невірні області: {', '.join(map(str, invalid_area))}.")
        return
    
    filtered_data = df[(df['area_ID'].isin(area_list)) & 
                        (df['year'].between(start_year, end_year))]

    row_limit = 52 + ((end_year - start_year) * 52)
    
    if not filtered_data.empty:
        print("#"*70)
        for area_id in area_list:
            area_name = area_map[area_id]
            print(f"Ряд VHI для області {area_name} з {start_year} по {end_year}:")
            area_data = filtered_data[filtered_data['area_ID'] == area_id]
            area_data_limited = area_data.head(row_limit)
            print(area_data_limited[['year', 'VHI']].to_string(index=False))
            print("#"*70)
    else:
        print(f"Немає даних для вказаних областей або років.")

vhi_for_range(vhi_data)


def find_extreme_droughts(df, map):
    print("\nПосухи в Україні ")
    print("#" * 70)
    try:
        percent = float(input("Введіть відсоток областей для визначення екстремальних посух (наприклад, 20): ").replace(',', '.'))
        if percent <= 0 or percent > 100:
            print("\n Відсоток має бути в межах від 1 до 100.\n")
            return
    except ValueError:
        print("\n Невірний формат числа. Спробуйте ще раз.\n")
        return

    total_area = 25
    threshold_area = max(1, int(total_area * percent / 100)) 
    print(f"\n Шукаємо роки, коли більше {percent:.1f}% областей (тобто {threshold_area}+) постраждали від посухи (VHI < 15)...")
    print("#" * 70)

    drought_years = []
    for year in sorted(df['year'].unique()):
        year_data = df[df['year'] == year]
        drought_area = year_data[year_data['VHI'] < 15]['area_ID'].unique()

        if len(drought_area) >= threshold_area:
            affected_area = [map[r] for r in drought_area if r in map]
            drought_years.append({
                'year': year,
                'affected_count': len(drought_area),
                'area': affected_area
            })

    if drought_years:
        print(f"\nЗнайдено {len(drought_years)} рік(ів) з екстремальними посухами!\n")
        for record in drought_years:
            print(f"Рік: {record['year']} | Уражено областей: {record['affected_count']}")
            print("Області: " + ', '.join(record['area']))
            print("#" * 70)
    else:
        print("\n Посухи, що уразили більше зазначеного відсотка областей, не знайдено.")

find_extreme_droughts(vhi_data, area_map)