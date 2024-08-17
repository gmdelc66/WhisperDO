import shutil, sys, time, os
from random import choice, randrange, paretovariate
import speech_recognition as sr
import pyttsx3
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Parámetros de cascada
MAX_CASCADES = 600
MAX_COLS = 20
FRAME_DELAY = 0.03
MAX_SPEED = 5

# Caracteres y colores
CSI = "\x1b["
pr = lambda command: print("\x1b[", command, sep="", end="")
getchars = lambda start, end: [chr(i) for i in range(start, end)]
black, green, white, red = "30", "32", "37", "31"  # Añadido rojo para detectar voz

latin = getchars(0x30, 0x80)
greek = getchars(0x390, 0x3d0)
hebrew = getchars(0x5d0, 0x5eb)
cyrillic = getchars(0x400, 0x50)
chars = latin + greek + hebrew + cyrillic


# Inicializar el tamaño de la terminal
def init():
    global cols, lines
    cols, lines = shutil.get_terminal_size()
    pr("?25l")  # Esconde el cursor
    pr("s")  # Guarda la posición del cursor


def end():
    pr("m")  # Reinicia atributos
    pr("2J")  # Limpia la pantalla
    pr("u")  # Restaura la posición del cursor
    pr("?25h")  # Muestra el cursor


def print_at(char, x, y, color="", bright="0"):
    pr("%d;%df" % (y, x))
    pr(bright + ";" + color + "m")
    print(char, end="", flush=True)


def update_line(speed, counter, line):
    counter += 1
    if counter >= speed:
        line += 1
        counter = 0
    return counter, line


def cascade(col, detect_voice=False):
    speed = randrange(1, MAX_SPEED)
    espeed = randrange(1, MAX_SPEED)
    line = counter = ecounter = 0
    oldline = eline = -1
    erasing = False
    bright = "1"
    limit = paretovariate(lines)
    color = red if detect_voice else green  # Cambiar color si detecta voz
    while True:
        counter, line = update_line(speed, counter, line)
        if randrange(10 * speed) < 1:
            bright = "0"
        if line > 1 and line <= limit and oldline != line:
            print_at(choice(chars), col, line - 1, color, bright)
        if line < limit:
            print_at(choice(chars), col, line, white, "1")
        if erasing:
            ecounter, eline = update_line(espeed, ecounter, eline)
            print_at(" ", col, eline, black)
        else:
            erasing = randrange(line + 1) > (lines / 2)
            eline = 0
        yield None
        oldline = line
        if eline >= limit:
            print_at(" ", col, oldline, black)
            break


def add_new(cascading, detect_voice=False):
    if randrange(MAX_CASCADES + 1) > len(cascading):
        col = randrange(cols)
        for i in range(randrange(MAX_COLS)):
            cascading.add(cascade((col + i) % cols, detect_voice))
        return True
    return False


def iterate(cascading):
    stopped = set()
    for c in cascading:
        try:
            next(c)
        except StopIteration:
            stopped.add(c)
    return stopped


# Monitor para la carpeta "leer"
class FileHandler(FileSystemEventHandler):
    def __init__(self, engine):
        self.engine = engine

    def on_created(self, event):
        if event.is_directory:
            return
        filename = event.src_path
        with open(filename, 'r') as f:
            text = f.read()
        self.engine.say(text)
        self.engine.runAndWait()


def listen_to_audio(recognizer, mic, engine):
    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Listening...")
            audio = recognizer.listen(source)
        print("Processing...")
        text = recognizer.recognize_google(audio)
        print(f"Recognized: {text}")
        with open(f"escucha/texto_{int(time.time())}.txt", "w") as f:
            f.write(text)
        engine.say(text)
        engine.runAndWait()
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
    return ""


def main():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    engine = pyttsx3.init()

    if not os.path.exists("escucha"):
        os.makedirs("escucha")
    if not os.path.exists("leer"):
        os.makedirs("leer")

    observer = Observer()
    observer.schedule(FileHandler(engine), path="leer", recursive=False)
    observer.start()

    cascading = set()
    while True:
        text = listen_to_audio(recognizer, mic, engine)
        detect_voice = bool(text)  # Si hay texto, detectamos voz
        while add_new(cascading, detect_voice): pass
        stopped = iterate(cascading)
        sys.stdout.flush()
        cascading.difference_update(stopped)
        time.sleep(FRAME_DELAY)


if __name__ == "__main__":
    try:
        init()
        main()
    except KeyboardInterrupt:
        pass
    finally:
        end()
