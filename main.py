import PySimpleGUI as sg
import threading
import time
import simpleaudio as sa
import os
import sys

# Determine the path to the bundled files directory
if getattr(sys, 'frozen', False):
    bundle_dir = sys._MEIPASS
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

# Paths to audio files and data file
WORK_CHIME_FILE = os.path.join(bundle_dir, "work_chime.wav")
REST_CHIME_FILE = os.path.join(bundle_dir, "rest_chime.wav")
TIMER_FILE = os.path.join(os.path.expanduser("~\\Documents"), "timers.txt")

def load_timers():
    timers = []
    try:
        with open(TIMER_FILE, "r") as file:
            for line in file:
                parts = line.strip().split(",")
                if len(parts) == 4:
                    exercise_name, work_time, rest_time, num_sets = parts
                    timers.append((exercise_name, int(work_time), int(rest_time), int(num_sets)))
                else:
                    print("Invalid timer data:", line)
    except Exception as e:
        print("Error loading timers:", e)
    return timers

def save_timer(exercise_name, work_time, rest_time, num_sets):
    with open(TIMER_FILE, "a") as file:
        file.write(f"{exercise_name},{work_time},{rest_time},{num_sets}\n")

def timer_thread(exercise_name, work_time, rest_time, num_sets):
    for _ in range(num_sets):
        print("Playing work chime...")
        play_chime(WORK_CHIME_FILE)
        print("Work chime played.")
        time.sleep(work_time)
        print("Playing rest chime...")
        play_chime(REST_CHIME_FILE)
        print("Rest chime played.")
        time.sleep(rest_time)

def play_chime(chime_file):
    chime_path = os.path.join(bundle_dir, chime_file)
    print("Chime Path:", chime_path)
    wave_obj = sa.WaveObject.from_wave_file(chime_path)
    play_obj = wave_obj.play()
    play_obj.wait_done()

def main():
    TIMERS = load_timers()  # Load timers at the beginning of the program
    exercise_list = [exercise_name for exercise_name, _, _, _ in TIMERS]  # Use the loaded timers here
    layout = [
        [sg.Text("Exercise Name:"), sg.InputText(key="-EXERCISE-")],
        [sg.Text("Work Time (seconds):"), sg.InputText(key="-WORK-")],
        [sg.Text("Rest Time (seconds):"), sg.InputText(key="-REST-")],
        [sg.Text("Number of Sets:"), sg.InputText(key="-SETS-")],
        [sg.Button("Add Timer"), sg.Button("Start Timer")],
        [sg.Listbox(values=exercise_list, size=(30, 6), key="-EXERCISES-")]
    ]

    window = sg.Window("Exercise Timer App", layout)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Add Timer":
            exercise_name = values["-EXERCISE-"]
            work_time = values["-WORK-"]
            rest_time = values["-REST-"]
            num_sets = values["-SETS-"]

            if all([exercise_name, work_time, rest_time, num_sets]):
                try:
                    work_time = int(work_time)
                    rest_time = int(rest_time)
                    num_sets = int(num_sets)

                    save_timer(exercise_name, work_time, rest_time, num_sets)
                    TIMERS.append((exercise_name, work_time, rest_time, num_sets))
                    exercise_list.append(exercise_name)
                    window["-EXERCISES-"].update(exercise_list)
                except ValueError:
                    sg.popup_error("Invalid input. Please enter numeric values.")
            else:
                sg.popup_error("Please fill in all fields.")

        elif event == "Start Timer":
            selected_exercise = values["-EXERCISES-"][0]

            # Look up the selected exercise in TIMERS and get its details
            selected_timer = next((t for t in TIMERS if t[0] == selected_exercise), None)
            if selected_timer is None:
                sg.popup_error("Selected exercise not found.")
                continue

            exercise_name, work_time, rest_time, num_sets = selected_timer

            threading.Thread(target=timer_thread, args=(exercise_name, work_time, rest_time, num_sets)).start()

    window.close()

if __name__ == "__main__":
    main()
