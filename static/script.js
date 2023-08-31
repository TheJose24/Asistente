
        const audio1 = document.getElementById('audio');
        const context = new AudioContext();
      

      /**
       * Three.js
       */

      var noise = new SimplexNoise();
      var vizInit = function () {

audio.addEventListener('play',() => {threePlay(audio)}, {once: true})

function threePlay() {
    var context = new AudioContext();
    var src = context.createMediaElementSource(audio);
    var analyser = context.createAnalyser();
    src.connect(analyser);
    analyser.connect(context.destination);
    analyser.fftSize = 512;
    var bufferLength = analyser.frequencyBinCount;
    var dataArray = new Uint8Array(bufferLength);
    var scene = new THREE.Scene();
    var group = new THREE.Group();
    var camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0,0,55);
    camera.lookAt(scene.position);
    scene.add(camera);

    var renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);


    var icosahedronGeometry = new THREE.IcosahedronGeometry(5, 4);
   //Mesh Texture
    var lambertMaterial = new THREE.MeshLambertMaterial({
        color: 0x323232,
        wireframe: true
    });

    var ball = new THREE.Mesh(icosahedronGeometry, lambertMaterial);
    ball.position.set(0, 0, 0);
    group.add(ball);

    /*
       Point Lights
    */
    const pointLight1 = new THREE.PointLight( 0xFFFFFF, 3, 100 );
    pointLight1.position.set( 30, 30, 10 );
    scene.add(pointLight1);
    
    const pointLight2 = new THREE.PointLight( 0xFFFFFF, 1.3, 100 );
    pointLight2.position.set( 30, -30, 10 );
    scene.add(pointLight2);
    
    const pointLight3 = new THREE.PointLight( 0xFFFFFF, 3, 100 );
    pointLight3.position.set( -30, -35, 10 );
    scene.add(pointLight3);
    
    const pointLight4 = new THREE.PointLight( 0xFFFFFF, 1.3, 100 );
    pointLight4.position.set( -30, 30, 10 );
    scene.add(pointLight4);
    
    const pointLight5 = new THREE.PointLight( 0xFFFFFF, 3, 100 );
    pointLight5.position.set( 0, -10, 10 );
    scene.add(pointLight5);
    
    const pointLight6 = new THREE.PointLight( 0xFFFFFF, 5, 100 );
    pointLight6.position.set( 0, 50, 10 );
    scene.add(pointLight5);

    scene.add(group);

    document.getElementById('out').appendChild(renderer.domElement);

    window.addEventListener('resize', onWindowResize, false);

    render();

    function render() {
      analyser.getByteFrequencyData(dataArray);

      var lowerHalfArray = dataArray.slice(0, (dataArray.length/2) - 1);
      var upperHalfArray = dataArray.slice((dataArray.length/2) - 1, dataArray.length - 1);

      var overallAvg = avg(dataArray);
      var lowerMax = max(lowerHalfArray);
      var lowerAvg = avg(lowerHalfArray);
      var upperMax = max(upperHalfArray);
      var upperAvg = avg(upperHalfArray);

      var lowerMaxFr = lowerMax / lowerHalfArray.length;
      var lowerAvgFr = lowerAvg / lowerHalfArray.length;
      var upperMaxFr = upperMax / upperHalfArray.length;
      var upperAvgFr = upperAvg / upperHalfArray.length;

      
      makeRoughBall(ball, modulate(Math.pow(lowerMaxFr, 0.8), 0, 1, 0, 8), modulate(upperAvgFr, 0, 1, 0, 4));

      group.rotation.x += (0.002);
      group.rotation.y += (0.002);
      renderer.render(scene, camera);
      requestAnimationFrame(render);
    }

    function onWindowResize() {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    }

    function makeRoughBall(mesh, bassFr, treFr) {
        var scaleFactor = 1 - (bassFr * 10 + treFr * 10) * 0.004; // Puedes ajustar el valor como desees
            mesh.scale.set(scaleFactor, scaleFactor, scaleFactor);
        mesh.geometry.vertices.forEach(function (vertex, i) {
            var offset = mesh.geometry.parameters.radius;
            var amp = 2.5;
            var time = window.performance.now();
            vertex.normalize();
            var rf = 0.00001;
            var distance = (offset + bassFr ) + noise.noise3D(vertex.x + time *rf*5, vertex.y +  time*rf*8, vertex.z + time*rf*9) * amp * treFr;
            vertex.multiplyScalar(distance);
        });
        mesh.geometry.verticesNeedUpdate = true;
        mesh.geometry.normalsNeedUpdate = true;
        mesh.geometry.computeVertexNormals();
        mesh.geometry.computeFaceNormals();
    }
  };
}

window.onload = vizInit();

document.body.addEventListener('touchend', function(ev) { context.resume(); });

function fractionate(val, minVal, maxVal) {
    return (val - minVal)/(maxVal - minVal);
}

function modulate(val, minVal, maxVal, outMin, outMax) {
    var fr = fractionate(val, minVal, maxVal);
    var delta = outMax - outMin;
    return outMin + (fr * delta);
}

function avg(arr){
    var total = arr.reduce(function(sum, b) { return sum + b; });
    return (total / arr.length);
}

function max(arr){
    return arr.reduce(function(a, b){ return Math.max(a, b); })
}

audio.crossOrigin = "anonymous";