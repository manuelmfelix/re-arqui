/**
 * Portfolio/Project detail functionality for RE-ARQUI
 */
document.addEventListener('DOMContentLoaded', function() {
  // DOM elements
  const viewer = document.getElementById('fullscreen-viewer');
  const image = document.getElementById('fullscreen-image');
  const caption = document.getElementById('fullscreen-caption');
  const closeBtn = document.querySelector('.fullscreen-close');
  const prevBtn = document.querySelector('.fullscreen-prev');
  const nextBtn = document.querySelector('.fullscreen-next');
  const galleryImages = document.querySelectorAll('.gallery-image');
  const header = document.querySelector('header');
  
  // Gallery state
  let currentIndex = 0;
  let images = Array.from(galleryImages);
  let lastScrollTop = 0;
  
  // Show specific image in fullscreen
  function showImage(index) {
    if (images.length === 0) return;
    
    // Ensure index is within bounds
    currentIndex = ((index % images.length) + images.length) % images.length;
    const img = images[currentIndex];
    
    // Update image and caption
    image.src = img.src;
    image.alt = img.alt || '';
    caption.textContent = img.alt || '';
    
    // Preload adjacent images
    if (images.length > 1) {
      const nextImg = new Image();
      nextImg.src = images[(currentIndex + 1) % images.length].src;
      
      const prevImg = new Image();
      prevImg.src = images[(currentIndex - 1 + images.length) % images.length].src;
    }
  }
  
  // Open fullscreen viewer
  images.forEach((img, index) => {
    img.addEventListener('click', () => {
      currentIndex = index;
      showImage(currentIndex);
      viewer.classList.add('active');
      document.body.style.overflow = 'hidden';
    });
  });
  
  // Navigate to previous image
  function prevImage() {
    showImage(currentIndex - 1);
  }
  
  // Navigate to next image
  function nextImage() {
    showImage(currentIndex + 1);
  }
  
  // Close the viewer
  function closeViewer() {
    viewer.classList.remove('active');
    document.body.style.overflow = '';
  }
  
  // Event Listeners
  
  // Close button click
  if (closeBtn) {
    closeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      closeViewer();
    });
  }
  
  // Previous button click
  if (prevBtn) {
    prevBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      prevImage();
    });
  }
  
  // Next button click
  if (nextBtn) {
    nextBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      nextImage();
    });
  }
  
  // Close when clicking on the background (not the image)
  viewer.addEventListener('click', function(event) {
    // This is the key fix: check if the clicked element is the viewer itself
    // and not any of its children or descendants
    if (event.target === viewer) {
      closeViewer();
    }
  });
  
  // Make sure clicks on the image don't close the viewer
  image.addEventListener('click', function(event) {
    event.stopPropagation();
  });
  
  // Make sure clicks on the navigation buttons don't close the viewer
  if (prevBtn) prevBtn.addEventListener('click', function(event) { 
    event.stopPropagation(); 
  });
  
  if (nextBtn) nextBtn.addEventListener('click', function(event) {
    event.stopPropagation();
  });
  
  // Make sure clicks on the caption don't close the viewer
  if (caption) caption.addEventListener('click', function(event) {
    event.stopPropagation();
  });
  
  // Keyboard navigation
  document.addEventListener('keydown', (e) => {
    // Only handle keyboard events when viewer is active
    if (!viewer.classList.contains('active')) return;
    
    switch (e.key) {
      case 'ArrowLeft':
        prevImage();
        break;
      case 'ArrowRight':
        nextImage();
        break;
      case 'Escape':
        closeViewer();
        break;
    }
  });
  
  // Header fade effect on scroll
  window.addEventListener('scroll', () => {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    if (scrollTop > 100) {
      header.style.opacity = scrollTop > lastScrollTop ? '0.5' : '1';
    } else {
      header.style.opacity = '1';
    }
    
    lastScrollTop = scrollTop;
  });
});