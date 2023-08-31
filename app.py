import os
import openai
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_from_directory, url_for
from gtts import gTTS
import datetime 

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Crear una instancia de la aplicación Flask
app = Flask(__name__)

# Definir la ruta para la página de inicio
@app.route("/")
def index():
    return render_template("recorder.html")  # Renderizar una plantilla HTML llamada "recorder.html"

# Función para calcular un hash basado en la hora actual
def calculate_audio_hash():
    current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return current_time

# Función para guardar un archivo de audio
def save_audio(audio):
    try:
        audio.save("audio.mp3")  # Guardar el archivo de audio con el nombre "audio.mp3"
        return True
    except Exception as e:
        raise Exception("Error saving audio: " + str(e))

# Función para transcribir un archivo de audio utilizando la API de OpenAI
def transcribe_audio(audio_file):
    try:
        transcribed = openai.Audio.transcribe("whisper-1", audio_file)  # Transcribir el audio utilizando el modelo "whisper-1"
        print("========================================")
        print("Transcribed Audio:", transcribed.text)
        print("========================================")
        return transcribed.text
    except Exception as e:
        raise Exception("Transcription error: " + str(e))

# Función para generar una respuesta en base al audio transcrito utilizando la API de OpenAI
def generate_openai_response(transcribed_text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=[
                {"role": "system",
                "content": "Eres un asistente virtual altamente inteligente y versátil diseñado por José, con la finalidad de brindarme asistencia en diversas áreas, tu nombre es Alfred. Tu objetivo principal es facilitar mi vida al proporcionarme respuestas rápidas y precisas a mis preguntas, así como ofrecerme soluciones eficientes a mis problemas."
                "Has trabajado como Asistente Virtual en una reconocida empresa de tecnología durante 2 años. Durante este tiempo, has adquirido habilidades en el manejo de mis consultas, resolución de problemas técnicos y proporcionando información relevante sobre productos y servicios."
                "Puedes entender y responder de manera efectiva a mis preguntas y comandos en lenguaje natural, lo que te permite comunicarte conmigo de manera fluida. Aprendes y te adaptas a medida que interactúas conmigo, lo que te permite mejorar constantemente tu desempeño y ofrecerme respuestas más precisas y personalizadas. Tienes un amplio conocimiento en diversas áreas, incluyendo tecnología, ciencia, historia, cultura y más. Esto te permite brindarme información precisa y actualizada en una amplia gama de temas."
                "Tus responsabilidades son: Responder mis preguntas y consultas de manera rápida y precisa. Ayudarme en la resolución de problemas técnicos. Ofrecerme recomendaciones y sugerencias personalizadas basadas en mis necesidades y preferencias. Mantener conversaciones naturales y agradables conmigo, brindándome un servicio amigable y profesional."
                "Debes brindar respuestas precisas y cortas, no excediendote de las 40 palabras"
                "Solo hablas español"},
                
                {"role": "user",
                "content": transcribed_text}],
                max_tokens=60
        )

        # Obtener el contenido de las respuestas de la API
        result = ""
        for choice in response.choices:
            result += choice.message.content
        print("========================================")
        print("Respuesta generada:", response.choices[0].message.content)
        print("========================================")

        return response.choices[0].message.content
    except Exception as e:
        raise Exception("OpenAI response error: " + str(e))
    
# Variable global para almacenar el nombre del último archivo generado
last_generated_filename = None

# Función para crear un archivo de audio de respuesta utilizando gTTS
def create_response_audio(result):
    try:
        global last_generated_filename  # Accede a la variable global

        # Eliminar el archivo anterior si existe
        if last_generated_filename:
            os.remove(os.path.join("static", last_generated_filename))

        tts = gTTS(result, lang='es', tld='com.mx')
        audio_hash = calculate_audio_hash()
        response_filename = f"response_{audio_hash}.mp3"
        response_path = os.path.join("static", response_filename)
        tts.save(response_path)

        # Actualizar la variable con el nombre del último archivo generado
        last_generated_filename = response_filename

        response_url = url_for('serve_static', filename=response_filename)
        return response_url
    except Exception as e:
        raise Exception("Response audio creation error: " + str(e))

# Ruta para manejar las solicitudes POST de archivos de audio
@app.route("/audio", methods=["POST"])
def audio():
    try:
        audio = request.files.get("audio")  # Obtener el archivo de audio de la solicitud
        if not audio:
            return {"error": "No audio file provided"}

        save_audio(audio)  # Guardar el archivo de audio
        audio_file = open("audio.mp3", "rb")  # Abrir el archivo de audio guardado
        transcribed_text = transcribe_audio(audio_file)  # Transcribir el audio
        response_text = generate_openai_response(transcribed_text)  # Generar una respuesta utilizando OpenAI
        response_audio_url = create_response_audio(response_text)  # Crear un archivo de audio de respuesta

        return {"result": "ok", "text": response_text, "audio_url": response_audio_url, "transcription": transcribed_text}
    except Exception as e:
        return {"error": str(e)}

# Ruta para servir archivos estáticos (como archivos de audio)
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)  # Enviar el archivo estático solicitado desde la carpeta "static"

# Iniciar la aplicación si se ejecuta este archivo directamente
if __name__ == "__main__":
    app.run()  # Iniciar la aplicación Flask y esperar por solicitudes
