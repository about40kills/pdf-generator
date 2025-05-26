document.addEventListener('DOMContentLoaded', () => {
  const convertButton = document.querySelector('.convert');
  const downloadButton = document.querySelector('.download');
  const loaderElement = document.querySelector('.loader');
  const searchContainer = document.querySelector('.search-container');
  const searchInput = document.getElementById('searchInput');
  const searchButton = document.getElementById('searchButton');
  const searchResults = document.getElementById('searchResults');

  const container = document.querySelector('.image-container');
  
  // Initialize variables for drag and drop
  let draggedItem = null;
  let currentPdfName = null;
   
  // Add event listeners to all images
  const images = document.querySelectorAll('.image-container img');
  
  images.forEach(img => {
    // Make the image draggable
    img.setAttribute('draggable', true);
    
    // Add drag start event
    img.addEventListener('dragstart', function(e) {
      draggedItem = this;
      setTimeout(() => { 
        this.style.opacity = '0.5';
        this.classList.add('dragging');
      }, 0);
      
      // Store the dragged element's data
      e.dataTransfer.setData('text/plain', this.getAttribute('data-name'));
      e.dataTransfer.effectAllowed = 'move';
    });
    
    // Add drag end event
    img.addEventListener('dragend', function() {
      this.style.opacity = '1';
      this.classList.remove('dragging');
      draggedItem = null;
    });
    
    // Add dragover event
    img.addEventListener('dragover', function(e) {
      e.preventDefault();
      return false;
    });  
    
    // Add dragenter event
    img.addEventListener('dragenter', function(e) {
      e.preventDefault();
      this.classList.add('drag-over');
    });
    
    // Add dragleave event
    img.addEventListener('dragleave', function() {
      this.classList.remove('drag-over');
    });
    
    // Add drop event
    img.addEventListener('drop', function(e) {
      e.preventDefault();
      
      if (draggedItem !== this) {
        // Get the positions of the dragged and target elements
        const allImages = Array.from(container.querySelectorAll('img'));
        const draggedIndex = allImages.indexOf(draggedItem);
        const targetIndex = allImages.indexOf(this);
        
        // Rearrange the elements
        if (draggedIndex < targetIndex) {
          container.insertBefore(draggedItem, this.nextSibling);
        } else {
          container.insertBefore(draggedItem, this);
        }
      }
      
      this.classList.remove('drag-over');
      return false;
    });
  });
  
  // Initially hide the download button
  downloadButton.style.display = 'none';
  
  convertButton.addEventListener('click', () => {
    // Show loader, hide text
    loaderElement.style.display = 'inline-block';
    convertButton.querySelector('.text').style.display = 'none';
    
    // Get all images' data-name attributes
    const images = Array.from(document.querySelectorAll('img[data-name]'))
      .map(img => img.dataset.name);
    
    // Send the image names to the server
    fetch('/pdf', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(images)
    })
    .then(response => response.text())
    .then(pdfPath => {
      // Hide loader, show text
      loaderElement.style.display = 'none';
      convertButton.querySelector('.text').style.display = 'inline-block';
      
      // Set the download link
      downloadButton.href = pdfPath;
      downloadButton.style.display = 'block';
      
      // Extract PDF name from path
      currentPdfName = pdfPath.split('/').pop();
      
      // Show search container
      searchContainer.style.display = 'block';
      
      // Process each image to extract text
      processImagesForSearch(images, currentPdfName);
    })
    .catch(error => {
      console.error('Error generating PDF:', error);
      loaderElement.style.display = 'none';
      convertButton.querySelector('.text').style.display = 'inline-block';
    });
  });

  // Function to process images for search
  async function processImagesForSearch(imageNames, pdfName) {
    for (let i = 0; i < imageNames.length; i++) {
      const imageName = imageNames[i];
      const formData = new FormData();
      const response = await fetch(`/images/${imageName}`);
      const blob = await response.blob();
      formData.append('file', blob, imageName);
      formData.append('pdf_name', pdfName);
      formData.append('page_number', i + 1);

      try {
        const backendUrl = window.location.hostname === 'localhost' 
          ? 'http://localhost:56948' 
          : 'https://pdf-generator-61cx.onrender.com';
          
        await fetch(`${backendUrl}/extract-text`, {
          method: 'POST',
          body: formData
        });
      } catch (error) {
        console.error(`Error processing image ${imageName}:`, error);
      }
    }
  }

  // Search functionality
  searchButton.addEventListener('click', async () => {
    const query = searchInput.value.trim();
    if (!query || !currentPdfName) return;

    try {
      const backendUrl = window.location.hostname === 'localhost' 
        ? 'http://localhost:56948' 
        : 'https://pdf-generator-61cx.onrender.com';
        
      const response = await fetch(`${backendUrl}/search?pdf_name=${currentPdfName}&query=${encodeURIComponent(query)}`);
      const data = await response.json();

      // Clear previous results
      searchResults.innerHTML = '';

      if (data.results && data.results.length > 0) {
        data.results.forEach(result => {
          const resultItem = document.createElement('div');
          resultItem.className = 'search-result-item';
          
          const pageNumber = document.createElement('div');
          pageNumber.className = 'page-number';
          pageNumber.textContent = `Page ${result.page}`;
          
          const context = document.createElement('div');
          context.className = 'context';
          context.textContent = result.context;
          
          resultItem.appendChild(pageNumber);
          resultItem.appendChild(context);
          searchResults.appendChild(resultItem); // Add this line
        });
      } else {
        searchResults.innerHTML = '<div class="search-result-item">No matches found</div>';
      }
    } catch (error) {
      console.error('Error searching:', error);
      searchResults.innerHTML = '<div class="search-result-item">Error performing search</div>';
    }
  });

  // Allow search on Enter key
  searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      searchButton.click();
    }
  });
});