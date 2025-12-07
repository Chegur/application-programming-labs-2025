import os
import csv
import argparse
from pathlib import Path

SUPPORTED_EXTENSIONS = {'.wav', '.mp3', '.flac', '.ogg', '.aiff', '.aif', '.m4a'}

def is_audio_file(filepath: str) -> bool:
    """Проверяет, является ли файл аудиофайлом по расширению."""
    return Path(filepath).suffix.lower() in SUPPORTED_EXTENSIONS

def create_annotation_from_folder(folder_path: str, csv_output_path: str) -> None:
    """
    Создаёт CSV-аннотацию для всех аудиофайлов в папке.
    
    Формат CSV:
        relative_path,absolute_path
    """
    folder = Path(folder_path).resolve()
    if not folder.is_dir():
        raise ValueError(f"Указанный путь не является директорией: {folder}")
    audio_files = [
        f for f in folder.iterdir()
        if f.is_file() and is_audio_file(f)
    ]
    if not audio_files:
        print(f"В папке {folder} не найдено аудиофайлов с поддерживаемыми расширениями: {SUPPORTED_EXTENSIONS}")
        return
    audio_files.sort()
    current_dir = Path.cwd()

    with open(csv_output_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['relative_path', 'absolute_path'])

        for audio_file in audio_files:
            abs_path = str(audio_file.resolve())
            rel_path = os.path.relpath(abs_path, start=current_dir)
            writer.writerow([rel_path, abs_path])

    print(f"Создан файл аннотации: {csv_output_path}")
    print(f"Найдено и добавлено {len(audio_files)} аудиофайлов.")

def main():
    parser = argparse.ArgumentParser(description="Создание CSV-аннотации для аудиофайлов в папке")
    parser.add_argument('audio_folder', type=str, help='Путь к папке с аудиофайлами')
    parser.add_argument('csv_output', type=str, help='Путь для сохранения CSV-файла (например, annotation.csv)')
    args = parser.parse_args()

    create_annotation_from_folder(args.audio_folder, args.csv_output)

if __name__ == '__main__':
    main()