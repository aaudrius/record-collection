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
              area: { 
                  top: "20%",
                  right: "20%",
                  left: "20%",
                  bottom: "20%"
              },
              singleChannel: false
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
      videoElement.srcObject.getTracks().forEach(track => track.stop());
      document.getElementById('barcode-scanner').style.display = 'none';
  };
});
