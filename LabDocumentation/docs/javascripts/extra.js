// Extra JavaScript for Healthcare Database Security Research Lab Documentation

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  console.log('Healthcare Database Security Research Lab Documentation loaded');

  // Add copy button functionality for code blocks
  initializeCopyButtons();

  // Initialize mermaid diagrams if present
  if (typeof mermaid !== 'undefined') {
    mermaid.initialize({
      startOnLoad: true,
      theme: 'default',
      securityLevel: 'loose'
    });
  }
});

// Initialize copy buttons for code blocks
function initializeCopyButtons() {
  const codeBlocks = document.querySelectorAll('pre > code');
  codeBlocks.forEach(function(codeBlock) {
    // Skip if button already exists
    if (codeBlock.parentElement.querySelector('.copy-button')) {
      return;
    }

    // Material theme handles this automatically, but we can extend if needed
  });
}

// Add smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  });
});
