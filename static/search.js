document.addEventListener("DOMContentLoaded", function() {
    var toggleSearchBtn = document.getElementById('toggle-search-btn');
    var albumSearch = document.getElementById('album_search');
    var barcodeSearch = document.getElementById('barcode_search');
    var searchType = document.getElementById('search-type');

    toggleSearchBtn.addEventListener('click', function() {
      if (albumSearch.style.display === 'none') {
        albumSearch.style.display = 'block';
        barcodeSearch.style.display = 'none';
        searchType.value = 'album_search';
        toggleSearchBtn.textContent = 'Switch to Barcode Search';
      } else {
        albumSearch.style.display = 'none';
        barcodeSearch.style.display = 'block';
        searchType.value = 'barcode_search';
        toggleSearchBtn.textContent = 'Switch to Album Search';
      }
    });

    document.getElementById('search-form').addEventListener('submit', function(e) {
      var artistInput = document.getElementById('artist-input');
      var albumInput = document.getElementById('album-input');
      var barcodeInput = document.getElementById('barcode-input');
      
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