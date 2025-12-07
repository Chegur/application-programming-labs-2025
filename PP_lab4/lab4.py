import pandas as pd
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
import os
from typing import List
import argparse
def parse_arguments() -> argparse.Namespace:
    """
    Парсит аргументы командной строки
    """
    parser = argparse.ArgumentParser(description="Добавление столбца в csv и построение графика амплитуд")
    parser.add_argument('annotation', type=str, help='Путь к CSV-файлу с аннотацией')
    parser.add_argument('new_annotation', type=str, help='Путь к новому csv-файлу')
    parser.add_argument('output_plot_png', type=str, help='Адресс графика амплитуд')
    return parser.parse_args()

def load_annotation(csv_path: str) -> pd.DataFrame:
    """
    Загружает аннотацию из CSV (с колонками absolute_path, relative_path).
    """
    return pd.read_csv(csv_path)


def compute_max_amplitude(file_path: str) -> float:
    """
    Вычисляет максимальную амплитуду по модулю для аудиофайла.
    """
    try:
        data, _ = sf.read(file_path)
        return float(np.max(np.abs(data)))
    except Exception as e:
        print(f"Ошибка при обработке {file_path}: {e}")
        return np.nan


def enrich_dataframe_with_amplitude(df: pd.DataFrame) -> pd.DataFrame:
    """
    Добавляет колонку 'max_amplitude' в DataFrame.
    """
    df = df.copy()
    df['max_amplitude'] = df['absolute_path'].apply(compute_max_amplitude)
    return df

def sort_by_max_amplitude(df: pd.DataFrame, ascending: bool = False) -> pd.DataFrame:
    """
    Сортирует DataFrame по колонке 'max_amplitude'.
    """
    return df.sort_values('max_amplitude', ascending=ascending).reset_index(drop=True)

def filter_by_amplitude(df: pd.DataFrame, min_amplitude: float = 0.1) -> pd.DataFrame:
    """
    Фильтрует строки, где max_amplitude >= min_amplitude.
    """
    return df[df['max_amplitude'] >= min_amplitude].reset_index(drop=True)

def plot_max_amplitudes(df: pd.DataFrame, output_image_path: str) -> None:
    """
    Строит график: x — порядковый номер, y — max_amplitude.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['max_amplitude'], marker='o', linestyle='-', color='purple')
    plt.title('Максимальная амплитуда (по модулю) для каждого аудиофайла')
    plt.xlabel('Порядковый номер (после сортировки)')
    plt.ylabel('Максимальная амплитуда')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(output_image_path, dpi=150)
    plt.show()

def main():
    args = parse_arguments()
    ANNOTATION_PATH = args.annotation
    OUTPUT_CSV_PATH = args.new_annotation
    OUTPUT_PLOT_PATH = args.output_plot_png

    df = load_annotation(ANNOTATION_PATH)
    print(f"Загружено {len(df)} записей из аннотации.")

    df_enriched = enrich_dataframe_with_amplitude(df)
    print("Добавлена колонка 'max_amplitude'.")

    df_sorted = sort_by_max_amplitude(df_enriched, ascending=False)
    print("DataFrame отсортирован по максимальной амплитуде.")

    df_filtered = filter_by_amplitude(df_sorted, min_amplitude=0.05)
    print(f"После фильтрации осталось {len(df_filtered)} файлов.")

    plot_max_amplitudes(df_sorted, OUTPUT_PLOT_PATH)
    
    df_sorted.to_csv(OUTPUT_CSV_PATH, index=False, encoding='utf-8')
    print(f"Результат сохранён в:\n- CSV: {OUTPUT_CSV_PATH}\n- График: {OUTPUT_PLOT_PATH}")


if __name__ == "__main__":
    main()