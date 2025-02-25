gamma_spectra_processor/  
│── main.py  
│   ├── Загружает файлы и определяет детектор  
│   ├── Вызывает обработку спектров  
│   ├── Сохраняет результат  
│  
│── gamma_spectrum.py  
│   ├── class GammaSpectrum  
│   │   ├── __init__(self, filename)  # Загружает данные из файла  
│   │   ├── remove_header_footer(self)  # Убирает хедер и футер  
│   │   ├── add_channel_numbers(self)  # Добавляет номера каналов  
│   │   ├── apply_calibration(self, calibration)  # Переводит каналы в энергию  
│   │   ├── save(self, output_file)  # Сохраняет спектр  
│  
│── spectrum_processor.py  
│   ├── class SpectrumProcessor  
│   │   ├── sum_spectra(self, spectra_list)  # Складывает спектры  
│   │   ├── subtract_background(self, spectrum, background)  # Вычитает фон  
│   │   ├── process_directory(self, directory)  # Обрабатывает все файлы в папке  
│  
│── energy_calibration.py  
│   ├── class EnergyCalibration  
│   │   ├── __init__(self, coefficients)  # Задает параметры калибровки  
│   │   ├── calibrate(self, channel)  # Переводит номер канала в энергию  
│  
│── detector_manager.py  
│   ├── class DetectorManager  
│   │   ├── __init__(self, config)  # Загружает конфигурацию детекторов  
│   │   ├── get_detector(self, filename)  # Определяет детектор по имени файла  
│   │   ├── get_calibration(self, detector_name)  # Получает калибровку для детектора  
│  
│── config.py  
│   ├── Словарь с детекторами и их калибровками  
│   ├── Пути к данным  
