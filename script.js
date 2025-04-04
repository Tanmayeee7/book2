document.addEventListener('DOMContentLoaded', function() {
    const bookNameInput = document.getElementById('bookName');
    const generateBtn = document.getElementById('generateBtn');
    const spinner = document.getElementById('spinner');
    const resultContainer = document.getElementById('resultContainer');
    const resultTitle = document.getElementById('resultTitle');
    const output = document.getElementById('output');
    const errorMessage = document.getElementById('errorMessage');
    
    generateBtn.addEventListener('click', generateOverview);
    
    bookNameInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            generateOverview();
        }
    });
    
    async function generateOverview() {
        const topic = bookNameInput.value.trim();
        
        if (!topic) {
            errorMessage.style.display = 'block';
            return;
        }
        
        errorMessage.style.display = 'none';
        generateBtn.disabled = true;
        spinner.style.display = 'block';
        resultContainer.style.display = 'none';
        
        try {
            const response = await fetch('http://localhost:5000/generate-overview', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ topic })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to generate overview');
            }
            
            resultTitle.textContent = `Overview of ${data.topic}`;
            output.innerHTML = formatMarkdown(data.overview);
            resultContainer.style.display = 'block';
        } catch (error) {
            output.textContent = error.message;
            resultTitle.textContent = 'Error';
            resultContainer.style.display = 'block';
        } finally {
            generateBtn.disabled = false;
            spinner.style.display = 'none';
        }
    }
    
    function formatMarkdown(text) {
        // Convert markdown to HTML
        return text
            .replace(/^# (.*$)/gm, '<h1>$1</h1>')
            .replace(/^## (.*$)/gm, '<h2>$1</h2>')
            .replace(/^### (.*$)/gm, '<h3>$1</h3>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/^> (.*$)/gm, '<blockquote>$1</blockquote>')
            .replace(/^(\d+)\. (.*$)/gm, '<li>$2</li>')
            .replace(/^- (.*$)/gm, '<li>$1</li>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>');
    }
});