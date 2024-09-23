document.addEventListener("DOMContentLoaded", function() {
    let toggleSearchBtn = document.getElementById('toggle-search-btn');
    let albumSearch = document.getElementById('album_search');
    let barcodeSearch = document.getElementById('barcode_search');
    let searchType = document.getElementById('search-type');

    toggleSearchBtn.addEventListener('click', function() {
      if (albumSearch.style.display === 'none') {
        albumSearch.style.display = 'block';
        barcodeSearch.style.display = 'none';
        searchType.value = 'album_search';
        toggleSearchBtn.textContent = 'Switch to Barcode Search';
        stopVideoStream();
      } else {
        albumSearch.style.display = 'none';
        barcodeSearch.style.display = 'block';
        searchType.value = 'barcode_search';
        toggleSearchBtn.textContent = 'Switch to Album Search';
      }
    });

    document.getElementById('search-form').addEventListener('submit', function(e) {
      let artistInput = document.getElementById('artist-input');
      let albumInput = document.getElementById('album-input');
      let barcodeInput = document.getElementById('barcode-input');
      
      if (searchType.value === 'album_search') {
        if (!artistInput.value.trim()) {
          e.preventDefault();
          alert('Artist name is mandatory for album search.');
        }
      } else if (searchType.value === 'barcode_search' && !barcodeInput.value.trim()) {
        e.preventDefault();
        alert('Barcode is mandatory for barcode search.');
      }
    });
  });