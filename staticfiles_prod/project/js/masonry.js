/**
 * Masonry grid functionality for RE-ARQUI
 */
document.addEventListener('DOMContentLoaded', function() {
  // Add loaded class to images once they're loaded
  const images = document.querySelectorAll('.project-image');
  
  images.forEach(img => {
    // If image is already cached, add loaded class immediately
    if (img.complete) {
      img.classList.add('loaded');
    } else {
      // Otherwise, wait for load event
      img.addEventListener('load', function() {
        img.classList.add('loaded');
      });
    }
    
    // Handle error cases
    img.addEventListener('error', function() {
      // Replace broken images with a no-image div
      const container = img.parentElement;
      const noImage = document.createElement('div');
      noImage.className = 'no-image';
      noImage.textContent = 'Image not available';
      
      container.replaceChild(noImage, img);
    });
  });
}); 