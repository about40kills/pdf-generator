document.addEventListener('DOMContentLoaded', () => {
  const convertButton = document.querySelector('.convert');
  const downloadButton = document.querySelector('.download');
  const loaderElement = document.querySelector('.loader');

  const container = document.querySelector('.image-container');
  
  // Initialize variables for drag and drop
  let draggedItem = null;
   
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
    })
    .catch(error => {
      console.error('Error generating PDF:', error);
      loaderElement.style.display = 'none';
      convertButton.querySelector('.text').style.display = 'inline-block';
    });
  });
});