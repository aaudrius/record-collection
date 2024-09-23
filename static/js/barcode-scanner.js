document.addEventListener("DOMContentLoaded", function() {
  const videoElement = document.getElementById('barcode-video');

  function startDirectVideoStream() {
      navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
          .then(function(stream) {
              videoElement.srcObject = stream;
              videoElement.play();
              console.log('Direct video stream successful');
          })
          .catch(function(err) {
              console.error('Error accessing video stream:', err);
          });
  }

  function startQuagga() {
      const quaggaConfig = {
          inputStream: {
              type: 'LiveStream',
              target: videoElement,
              constraints: {
                  facingMode: 'environment'
              },
              area: { // defines rectangle of the detection/localization area
                  top: "20%",    // top offset
                  right: "20%",  // right offset
                  left: "20%",   // left offset
                  bottom: "20%"  // bottom offset
              },
              singleChannel: false // true: only the red color-channel is read
          },
          decoder: {
              readers: [
                  'code_128_reader',
                  'ean_reader',
                  'ean_8_reader',
                  'code_39_reader',
                  'code_39_vin_reader',
                  'codabar_reader',
                  'upc_reader',
                  'upc_e_reader',
                  'i2of5_reader'
              ],
              debug: {
                  drawBoundingBox: true,
                  showFrequency: true,
                  drawScanline: true,
                  showPattern: true
              }
          },
          locate: true
      };

      Quagga.init(quaggaConfig, function(err) {
          if (err) {
              console.error('Quagga initialization failed:', err);
              alert("Error starting barcode scanner: " + err.message);
              return;
          }

          Quagga.start();

          videoElement.style.opacity = 1;
      });

      Quagga.onDetected(function(result) {
          const code = result.codeResult.code;
          document.getElementById('barcode-input').value = code;
          document.getElementById('barcode-scanner').style.display = 'none';
          Quagga.stop();
      });
  }

  document.getElementById('scan-barcode-btn').onclick = function() {
      document.getElementById('barcode-scanner').style.display = 'block';
      startDirectVideoStream();
      startQuagga();
  };

  document.getElementById('close-barcode-btn').onclick = function() {
      Quagga.stop();
      videoElement.srcObject.getTracks().forEach(track => track.stop()); // Stop the video stream
      document.getElementById('barcode-scanner').style.display = 'none';
  };
});
