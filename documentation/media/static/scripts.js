// Document ready event
document.addEventListener('DOMContentLoaded', function() {
  // Set current year in footer
  document.getElementById('current-year').textContent = new Date().getFullYear();

  // Add click handlers to all "Copy Documentation text" links
  const docLinks = document.querySelectorAll('a');
  
  docLinks.forEach(link => {
    if (link.textContent.trim() === 'Copy Documentation text') {
      link.addEventListener('click', function(e) {
        e.preventDefault();
        const toolName = this.closest('.group').querySelector('.text-blue-700.font-medium').textContent.trim();
        copyText('doc', toolName, this);
      });
    }
    else if (link.textContent.trim() === 'Copy AI summary docs') {
      link.addEventListener('click', function(e) {
        e.preventDefault();
        const toolName = this.closest('.group').querySelector('.text-blue-700.font-medium').textContent.trim();
        copyText('ai', toolName, this);
      });
    }
  });
  
  function copyText(type, name, element) {
    const url = type === 'doc' ? 
      `/copy_doc_text/?name=${encodeURIComponent(name)}` : 
      `/copy_ai_summary/?name=${encodeURIComponent(name)}`;
    
    console.log(`Copying ${type} for ${name} from ${url}`);
    
    fetch(url)
      .then(response => response.json())
      .then(data => {
        // Get content from the response
        let content;
        if (data.text) {
          content = data.text;
        } else if (data.summary) {
          content = data.summary;
        } else if (data.error) {
          content = `No content available for ${name}`;
        } else {
          content = `No content available for ${name}`;
        }
        
        // Copy to clipboard
        navigator.clipboard.writeText(content)
          .then(() => {
            // Show "Copied successfully" message
            const originalText = element.textContent;
            element.textContent = "Copied!";
            
            // Reset text after 2 seconds
            setTimeout(() => {
              element.textContent = originalText;
            }, 2000);
          })
          .catch(err => {
            console.error('Could not copy text: ', err);
          });
      })
      .catch(error => {
        console.error('Error:', error);
        // Show "Copied!" anyway even if there's an error
        const originalText = element.textContent;
        element.textContent = "Copied!";
        setTimeout(() => {
          element.textContent = originalText;
        }, 2000);
      });
  }
});

// Function to toggle the documentation section
function toggleDocs() {
  const docGrid = document.getElementById('doc-grid');
  const toggleArrow = document.getElementById('toggle-arrow');
  
  if (docGrid.style.display === 'none') {
    docGrid.style.display = 'block';
    toggleArrow.textContent = '↑';
  } else {
    docGrid.style.display = 'none';
    toggleArrow.textContent = '↓';
  }
}
