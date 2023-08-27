import os
import openai
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_from_directory, url_for
from gtts import gTTS
import hashlib

# Cargar llaves del archivo .env
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Crear una instancia de la aplicación Flask
app = Flask(__name__)

# Definir una ruta para la página de inicio
@app.route("/")
def index():
    return render_template("recorder.html")

def calculate_hash(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# Definir una ruta para recibir y procesar audio
@app.route("/audio", methods=["POST"])
def audio():
    try:
        # Calcular el hash del archivo de audio
        audio_hash = calculate_hash("audio.mp3")
        # Obtener el archivo de audio grabado desde la solicitud
        audio = request.files.get("audio")
        print("1")
        # Guardar el archivo de audio en el sistema de archivos
        audio.save("audio.mp3")
        print("audio guardado")
        # Abrir el archivo de audio para lectura binaria
        audio_file = open("audio.mp3", "rb")
        print("audio abierto")
        # Transcribir el audio usando la API de OpenAI
        transcribed = openai.Audio.transcribe("whisper-1", audio_file)
        print("audio transcrito")
        
        # Mostrar el audio transcrito en la consola
        print("Texto transcrito:", transcribed.text)
        
        # Crear la respuesta de OpenAI con el texto transcrito
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
                "content": transcribed.text}],
                max_tokens=60
        )

        # Obtener el contenido de las respuestas de la API
        result = ""
        for choice in response.choices:
            result += choice.message.content

        # Obtener la ruta absoluta del directorio actual
        current_directory = os.path.abspath(os.path.dirname(__file__))
        print("Directorio actual:", current_directory)

        # Obtener la ruta completa del directorio "static"
        static_directory = os.path.join(current_directory, "static")

        # Nombre del archivo de respuesta con el hash
        response_filename = f"response_{audio_hash}.mp3"

        # Crear un archivo de audio de respuesta utilizando gTTS y guardarlo en "static"
        response_path = os.path.join(static_directory, response_filename)
        tts = gTTS(result, lang='es', tld='com.pe')
        tts.save(response_path)

        # Retornar la URL del archivo de respuesta al cliente
        response_url = url_for('serve_static', filename=response_filename)
        return {"result": "ok", "text": result, "audio_url": response_url}
    except Exception as e:
         # Manejar errores y retornar un diccionario con el mensaje de error
        return {"error": str(e)}
    
# Ruta para servir archivos estáticos (como response.mp3)
@app.route('/static/<path:filename>')
def serve_static(filename):
    print(filename)
    print(serve_static.__name__)
    return send_from_directory('static', filename)

# Iniciar la aplicación
if __name__ == "__main__":
    app.run()
