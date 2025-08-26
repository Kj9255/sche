import sys
from PyQt6.QtWidgets import QApplication, QDialog

from UI.initial_setup_dialog import InitialSetupDialog
from UI.main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    setup_dialog = InitialSetupDialog()
    if setup_dialog.exec() == QDialog.DialogCode.Accepted:
        engine = setup_dialog.loaded_engine
        participants = setup_dialog.loaded_participants
        poll_dates = setup_dialog.loaded_poll_dates
        day_ranges = setup_dialog.loaded_day_ranges

        main_window = MainWindow()
        main_window.engine_name = engine
        main_window.participants = participants
        main_window.poll_dates = poll_dates
        main_window.day_ranges = day_ranges

        if main_window.engine_name == "Timeful":
            main_window.sidebar.btn_timeful.setChecked(True)
            main_window.sidebar.btn_cabbage.setChecked(False)
        else:
            main_window.sidebar.btn_cabbage.setChecked(True)
            main_window.sidebar.btn_timeful.setChecked(False)

        # If a CSV path was provided via initial setup, load it now
        from PyQt6.QtCore import QSettings
        settings = QSettings("Harmobot", "Harmobot")
        startup_csv = settings.value("startup_csv_path", "")
        if startup_csv:
            # Clear the flag to avoid reloading on next runs
            settings.remove("startup_csv_path")
            # Call the CSV loader directly
            try:
                # Reuse existing handler by simulating a file-open: temporarily monkeypatch QFileDialog
                from core import export_handlers
                from PyQt6.QtWidgets import QFileDialog
                orig_get_open = QFileDialog.getOpenFileName
                try:
                    QFileDialog.getOpenFileName = lambda *args, **kwargs: (startup_csv, "CSV Files (*.csv)")
                    export_handlers.load_from_csv(main_window)
                finally:
                    QFileDialog.getOpenFileName = orig_get_open
            except Exception:
                pass
        else:
            main_window.initialize_schedule_table()
        main_window.show()
        sys.exit(app.exec())
    else:
        sys.exit()

if __name__ == "__main__":
    main()
