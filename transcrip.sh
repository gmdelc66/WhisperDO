#!/bin/bash
# Este script permite seleccionar entre transcribir en inglés o traducir desde español, francés
# o cualquier otro idioma a inglés, basándose en el parámetro pasado al script.
# Ejemplo de uso:
# Hacer el Script Ejecutable:
  #
  #chmod +x transcrip.sh
# ./transcrip.sh /audio/* english
# donde /audio/ = carpeta con archivos a transcribir de audio a texto
# english si audio esta en ingles
# spanish si esta en Español
# french si esta en frances
# en Inglés: Modelo small es suficiente debido a la alta calidad del modelo en inglés y a la necesidad
# de un procesamiento más rápido.
# Otros Idiomas: Modelo large es preferido para garantizar la mayor precisión posible y para
# manejar tareas más complejas como la traducción.

# Configuraciones predeterminadas
model="small.en"
lang="English"
task="transcribe"

# Verifica si se ha proporcionado un archivo de origen
if [ -z "$1" ]; then
  echo "Error: No se ha proporcionado un archivo de origen. Este script ahora saldrá."
  exit 1
fi

# Configura el modelo y las tareas basadas en el idioma
if [ "$2" == "english" ]; then
  model="small.en"
  lang="English"
  task="transcribe"
elif [ "$2" == "espanol" ]; then
  model="large"
  lang="Spanish"
  task="translate"
elif [ "$2" == "french" ]; then
  model="large"
  lang="French"
  task="translate"
fi

while [ ! -z "$1" ]; do
  filename="$1"
  name=$(basename "$filename" | cut -d. -f1)
  runtime=$(date +"%H%M%S")
  date=$(date +"%Y-%m-%d")
  target_dir="$HOME/Desktop/Transcripts/$date $runtime $name"
  short_dir="~/Desktop/Transcripts/$date $runtime $name"

  echo "------------------------------------------"
  echo "Archivo objetivo: $filename"
  echo "Ejecutando Whisper con el modelo $model en $lang para $task"
  echo "Los archivos se guardarán en $short_dir"

  mkdir -p "$target_dir"

  python3 -c "import whisper; from whisper.transcribe import cli; cli()" "$filename" --model "$model" --language "$lang" --task "$task" --output_dir "$target_dir"

  echo "Tarea completa. Los archivos se han guardado en $short_dir"

  shift
done

echo "Tareas completadas."
