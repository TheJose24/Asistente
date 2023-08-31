// Declaracion de variables globales
let blobs = [];
let stream;
let rec;
let recordUrl;
let audioResponseHandler;

// Función para configurar el URL de grabación y el manejador de respuesta
function recorder(url, handler) {
    recordUrl = url;
    if (typeof handler !== "undefined") {
        audioResponseHandler = handler;
    }
}

// Función para iniciar la grabación
async function record() {
    try {
        document.getElementById("text").innerHTML = "<i>Grabando...</i>";
        document.getElementById("record").style.display="none";
        document.getElementById("stop").style.display="";
        document.getElementById("record-stop-label").style.display="initial";
        document.getElementById("record-stop-loading").style.display="none"
        document.getElementById("stop").disabled=false

        // Limpiar el array de blobs
        blobs = [];

        // Obtener acceso al micrófono
        stream = await navigator.mediaDevices.getUserMedia({audio:true, video:false})
        rec = new MediaRecorder(stream);

        // Capturar los datos de audio disponibles durante la grabación
        rec.ondataavailable = e => {
            if (e.data) {
                blobs.push(e.data);
            }
        }
        
        // Llamar a la función doPreview cuando se detenga la grabación
        rec.onstop = doPreview;
        
        // Iniciar la grabación
        rec.start();
    } catch (e) {
        alert("No fue posible iniciar el grabador de audio.");
    }
}

// Función para procesar los blobs de audio y enviarlos al servidor
function doPreview() {
    if (!blobs.length) {
        // No hay blobs para procesar
    } else {
        // Crear un objeto Blob a partir de los blobs grabados
        const blob = new Blob(blobs);

        // Usar fetch para enviar el audio grabado al servidor
        var fd = new FormData();
        fd.append("audio", blob, "audio");
        fetch(recordUrl, {
            method: "POST",
            body: fd,
        })
        .then((response) => response.json())
        .then(audioResponseHandler)
        .catch(err => {
            console.log("Oops: Ocurrió un error", err);
        });
    }
}

// Función para detener la grabación
function stop() {
    // Cambiar la interfaz para mostrar que se está procesando
    document.getElementById("text").innerHTML = "Procesando...";
    document.getElementById("record-stop-label").style.display="none";
    document.getElementById("record-stop-loading").style.display="block";
    document.getElementById("stop").disabled=true;
    
    rec.stop();
}

// Función para manejar la respuesta de audio
function handleAudioResponse(response){
    if (!response || response == null) {
        //TODO subscribe you thief
        console.log("No response");
        return;
    }
    // Detener y liberar el stream de audio
    stream.getTracks().forEach(track => track.stop());
    
    // Limpiar los blobs grabados
    blobs = [];

    // Restablecer la visibilidad de los botones
    document.getElementById("record").style.display = "";
    document.getElementById("stop").style.display = "none";

    // Restablecer el contenido de texto
    document.getElementById("text").innerHTML = "";

    // Llamar al audioResponseHandler si está definido
    if (audioResponseHandler != null) {
        audioResponseHandler(response);
    }
}