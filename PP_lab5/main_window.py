import os
import sys
from pathlib import Path
pyqt_path = Path(sys.executable).parent / "Lib/site-packages/PyQt5/Qt"
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(pyqt_path / "plugins")
os.environ["QT_PLUGIN_PATH"] = str(pyqt_path / "plugins")
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl, Qt
from sound_iterator import SoundPathIterator


class AudioPlayerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Аудиоплеер — Лабораторная №5")
        self.setGeometry(200, 200, 600, 300)

        self.iterator = None
        self.current_media = None
        self.player = QMediaPlayer()
        self.player.mediaStatusChanged.connect(self.on_media_status_changed)

        self.label_title = QLabel("Название: —")
        self.label_duration = QLabel("Длительность: —")
        self.btn_load = QPushButton("Загрузить аннотацию (CSV)")
        self.btn_next = QPushButton("Следующий аудиофайл")
        self.btn_play = QPushButton("Воспроизвести")

        self.btn_next.setEnabled(False)
        self.btn_play.setEnabled(False)

        self.btn_load.clicked.connect(self.load_annotation)
        self.btn_next.clicked.connect(self.next_audio)
        self.btn_play.clicked.connect(self.toggle_playback)

        central_widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(self.label_title)
        layout.addWidget(self.label_duration)
        layout.addWidget(self.btn_load)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_next)
        button_layout.addWidget(self.btn_play)
        layout.addLayout(button_layout)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def load_annotation(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите CSV-файл аннотации", "", "CSV Files (*.csv)"
        )
        if file_path:
            try:
                self.iterator = iter(SoundPathIterator(file_path))
                self.btn_next.setEnabled(True)
                self.label_title.setText("Название: готово к воспроизведению")
                self.label_duration.setText("Длительность: —")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить аннотацию:\n{e}")

    def next_audio(self):
        if self.iterator is None:
            return

        try:
            self.player.stop()

            audio_path = next(self.iterator)
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Файл не найден: {audio_path}")

            filename = os.path.basename(audio_path)
            self.label_title.setText(f"Название: {filename}")

            self.current_media = QMediaContent(QUrl.fromLocalFile(audio_path))
            self.player.setMedia(self.current_media)

            self.label_duration.setText("Длительность: загрузка...")
            self.player.durationChanged.connect(self.update_duration)
            
            self.btn_play.setEnabled(True)
            self.btn_play.setText("Воспроизвести")

        except StopIteration:
            QMessageBox.information(self, "Конец", "Больше аудиофайлов в аннотации нет.")
            self.btn_next.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить аудиофайл:\n{e}")

    def update_duration(self, duration_ms: int):
        if duration_ms > 0:
            seconds = duration_ms // 1000
            minutes = seconds // 60
            seconds = seconds % 60
            self.label_duration.setText(f"Длительность: {minutes}:{seconds:02d}")
        else:
            self.label_duration.setText("Длительность: неизвестна")

    def toggle_playback(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.btn_play.setText("Воспроизвести")
        else:
            self.player.play()
            self.btn_play.setText("Пауза")

    def on_media_status_changed(self, status):
        # Опционально: обработка ошибок загрузки
        if status == self.player.InvalidMedia:
            self.label_duration.setText("Длительность: ошибка загрузки")

    def closeEvent(self, event):
        self.player.stop()
        if hasattr(self.iterator, '_file') and self.iterator._file:
            self.iterator._file.close()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = AudioPlayerWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()