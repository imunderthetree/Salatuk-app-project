import requests
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QTimer
import pygame
import os
import random

def get_prayer_times_by_coordinates(latitude, longitude):
    url = f'http://api.aladhan.com/v1/timings?latitude={latitude}&longitude={longitude}&method=2'
    response = requests.get(url)
    data = response.json()
    return data['data']['timings'], data['data']['date']['hijri']

def get_prayer_times_by_city(city):
    url = f'http://api.aladhan.com/v1/timingsByCity?city={city}&country=&method=2'
    response = requests.get(url)
    data = response.json()
    return data['data']['timings'], data['data']['date']['hijri']

def display_prayer_times(prayer_times, hijri_date):
    hijri_date_str = f"{hijri_date['month']['en']} {hijri_date['day']}, {hijri_date['year']}"
    hijri_date_label.setText(f"Today's Hijri Date: {hijri_date_str}")

    ordered_prayers = ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']

    for i, prayer in enumerate(ordered_prayers):
        time_24h = prayer_times[prayer]
        time_12h = datetime.strptime(time_24h, "%H:%M").strftime("%I:%M %p")
        prayer_labels[i].setText(f"{prayer}: {time_12h}")
        prayer_labels[i].setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Bold))

    start_countdown(prayer_times, ordered_prayers)

def get_current_location():
    geolocator = Nominatim(user_agent="prayer_times_app")
    location = geolocator.geocode("Your address")
    return location.latitude, location.longitude

def get_times_by_city():
    city = city_entry.text()
    if city:
        prayer_times, hijri_date = get_prayer_times_by_city(city)
        display_prayer_times(prayer_times, hijri_date)
    else:
        prayer_times_display.setText("Please enter a city name")

def get_times_by_location():
    latitude, longitude = get_current_location()
    prayer_times, hijri_date = get_prayer_times_by_coordinates(latitude, longitude)
    display_prayer_times(prayer_times, hijri_date)

def play_random_athan():
    athan_folder = "C:/Users/user/Documents/Projects/Athans"
    athan_files = [f for f in os.listdir(athan_folder) if f.endswith('.mp3')]
    if athan_files:
        random_athan = random.choice(athan_files)
        pygame.mixer.music.load(os.path.join(athan_folder, random_athan))
        pygame.mixer.music.play()

def update_countdown():
    now = datetime.now().strftime("%H:%M:%S")
    next_prayer = None
    min_diff = float('inf')

    for prayer, time in current_prayer_times.items():
        prayer_time = datetime.strptime(time, "%H:%M")
        now_time = datetime.strptime(now, "%H:%M:%S")
        
        # If Isha has passed, show Fajr as next prayer
        if prayer == "Isha":
            fajr_time = datetime.strptime(current_prayer_times["Fajr"], "%H:%M") + timedelta(days=1)
            diff = (fajr_time - now_time).total_seconds()
            if diff > 0:
                min_diff = diff
                next_prayer = "Fajr"

        diff = (prayer_time - now_time).total_seconds()
        if 0 < diff < min_diff:
            min_diff = diff
            next_prayer = prayer

    if next_prayer:
        hours, remainder = divmod(min_diff, 3600)
        minutes, seconds = divmod(remainder, 60)
        countdown_label.setText(f"Next prayer: {next_prayer} in {int(hours)}h {int(minutes)}m {int(seconds)}s")
        if int(hours) == 0 and int(minutes) == 0 and int(seconds) == 0:
            play_random_athan()
    else:
        countdown_label.setText("No upcoming prayers for today")

def start_countdown(prayer_times, ordered_prayers):
    global current_prayer_times
    current_prayer_times = {prayer: prayer_times[prayer] for prayer in ordered_prayers}
    update_countdown()
    countdown_timer.start(1000)

def pause_athan():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
    else:
        pygame.mixer.music.unpause()

app = QtWidgets.QApplication([])

window = QtWidgets.QWidget()
window.setWindowTitle("Salatuk")
window.setWindowIcon(QtGui.QIcon('icon.png'))

app.setStyleSheet("""
    QWidget {
        background-color: #1e3d59;
        font-family: 'Scheherazade', 'Arial', sans-serif;
    }
    QLabel {
        font-size: 18px;
        color: #f4d03f;
    }
    QLineEdit {
        padding: 8px;
        font-size: 16px;
        border: 2px solid #f4d03f;
        border-radius: 6px;
        background-color: #fff;
        color: #1e3d59;
    }
    QPushButton {
        background-color: #117864;
        color: white;
        padding: 12px;
        border: none;
        border-radius: 6px;
        font-size: 16px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #0e6251;
    }
    #countdown_label {
        font-size: 20px;
        color: #f4d03f;
        font-weight: bold;
        margin-top: 20px;
    }
    #hijri_date_label {
        font-size: 20px;
        color: #f4d03f;
        font-weight: bold;
        margin-top: 10px;
    }
    #header_label {
        font-size: 28px;
        font-weight: bold;
        color: #f4d03f;
        margin-bottom: 20px;
        font-family: 'Amiri', 'Arial', sans-serif;
    }
    QVBoxLayout {
        border: 2px solid #f4d03f;
        border-radius: 10px;
        padding: 10px;
    }
""")

layout = QtWidgets.QVBoxLayout()

header_label = QtWidgets.QLabel("Salatuk")
header_label.setAlignment(QtCore.Qt.AlignCenter)
header_label.setObjectName("header_label")
layout.addWidget(header_label)

city_label = QtWidgets.QLabel("Enter your city:")
layout.addWidget(city_label)

city_entry = QtWidgets.QLineEdit()
layout.addWidget(city_entry)

city_button = QtWidgets.QPushButton("Get Prayer Times by City")
city_button.clicked.connect(get_times_by_city)
layout.addWidget(city_button)

prayer_times_display = QtWidgets.QLabel()
layout.addWidget(prayer_times_display)

# Add some spacing between the buttons
layout.addSpacing(10)

location_button = QtWidgets.QPushButton("Get Prayer Times by Location")
location_button.clicked.connect(get_times_by_location)
layout.addWidget(location_button)

pause_button_layout = QtWidgets.QHBoxLayout()
pause_button_layout.addStretch(1)
pause_button = QtWidgets.QPushButton("⏸️")
pause_button.setFixedSize(50, 50)
pause_button.clicked.connect(pause_athan)
pause_button_layout.addWidget(pause_button)
pause_button_layout.addStretch(1)
layout.addLayout(pause_button_layout)

hijri_date_label = QtWidgets.QLabel()
hijri_date_label.setObjectName("hijri_date_label")
layout.addWidget(hijri_date_label)

prayer_grid = QtWidgets.QGridLayout()
prayer_labels = []
ordered_prayers = ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
for i, prayer in enumerate(ordered_prayers):
    prayer_label = QtWidgets.QLabel(f"{prayer}: ")
    prayer_labels.append(prayer_label)
    prayer_grid.addWidget(prayer_label, i // 2, i % 2)

layout.addLayout(prayer_grid)

countdown_label = QtWidgets.QLabel()
countdown_label.setObjectName("countdown_label")
layout.addWidget(countdown_label)

window.setLayout(layout)
window.show()

pygame.mixer.init()

countdown_timer = QTimer()
countdown_timer.timeout.connect(update_countdown)

app.exec_()
