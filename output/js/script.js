document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Checkboxes from LocalStorage
    const checkboxes = document.querySelectorAll('.q-checkbox');
    const storageKey = 'phoenix_physics_progress';

    // Load state
    let progressState = JSON.parse(localStorage.getItem(storageKey)) || {};

    // Initialize UI based on state
    checkboxes.forEach(cb => {
        const qId = cb.dataset.id;
        if (progressState[qId]) {
            cb.checked = true;
            markQuestionCompleted(cb);
        }

        // Add change listener
        cb.addEventListener('change', (e) => {
            const isChecked = e.target.checked;
            const id = e.target.dataset.id;

            if (isChecked) {
                progressState[id] = true;
                markQuestionCompleted(e.target);
            } else {
                delete progressState[id];
                markQuestionUncompleted(e.target);
            }

            localStorage.setItem(storageKey, JSON.stringify(progressState));
            updateProgressCounters();
        });
    });

    updateProgressCounters();
});

// Helper: Visual feedback for completion
function markQuestionCompleted(checkboxInput) {
    const card = checkboxInput.closest('.question-card');
    if (card) {
        card.classList.add('completed');
    }
}

function markQuestionUncompleted(checkboxInput) {
    const card = checkboxInput.closest('.question-card');
    if (card) {
        card.classList.remove('completed');
    }
}

// 2. Toggle Answer Function (Global)
window.toggleAnswer = function (btn) {
    const answerContainer = btn.nextElementSibling; // content div
    const isHidden = answerContainer.classList.contains('hidden');

    if (isHidden) {
        answerContainer.classList.remove('hidden');
        answerContainer.classList.add('visible');
        btn.innerHTML = '<span class="icon">🙈</span> Hide Answer';
    } else {
        answerContainer.classList.remove('visible');
        answerContainer.classList.add('hidden');
        btn.innerHTML = '<span class="icon">👁️</span> Show Answer';
    }
};

// 3. Update Progress UI
function updateProgressCounters() {
    const storageKey = 'phoenix_physics_progress';
    const progressState = JSON.parse(localStorage.getItem(storageKey)) || {};
    const totalCompleted = Object.keys(progressState).length;

    // Current Page Progress
    const pageCheckboxes = document.querySelectorAll('.q-checkbox');
    if (pageCheckboxes.length > 0) {
        let pageCompleted = 0;
        pageCheckboxes.forEach(cb => {
            if (cb.checked) pageCompleted++;
        });

        const pageTotal = pageCheckboxes.length;
        const percent = Math.round((pageCompleted / pageTotal) * 100);

        const progressBar = document.getElementById('chapter-progress-bar');
        const progressText = document.getElementById('chapter-progress-text');

        if (progressBar) progressBar.style.width = `${percent}%`;
        if (progressText) progressText.textContent = `${pageCompleted}/${pageTotal} Questions Completed`;
    }
    // Note: Global progress on index page also requires reading counts, simplified for static site.
}

// 4. Gemini API Integration (via Vercel Function)

window.askGemini = async function (btn, questionId) {
    const responseDiv = document.getElementById(`gemini-${questionId}`);
    const contentDiv = responseDiv.querySelector('.gemini-content');

    // Get question and answer text
    const card = btn.closest('.question-card');
    const questionText = card.querySelector('.question-body').innerText;
    const answerText = card.querySelector('.answer-inner').innerText;

    // Toggle visibility if already showing
    if (!responseDiv.classList.contains('hidden') && contentDiv.innerHTML !== '') {
        responseDiv.classList.add('hidden');
        return;
    }

    responseDiv.classList.remove('hidden');
    contentDiv.innerHTML = '<div class="loading">Summoning AI Tutor...</div>';

    const prompt = `
    You are a helpful physics tutor. Explain the following physics question and its answer simply and clearly.
    Break it down step-by-step if it's a calculation. 
    Use the provided answer to ensure correctness, but explain the 'why' behind it.
    
    Question: ${questionText}
    
    Provided Answer: ${answerText}
    
    Explanation:
    `;

    try {
        // Call our own backend API (Vercel Function)
        const response = await fetch('/api/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt: prompt })
        });

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        // Gemini response structure
        const aiText = data.candidates[0].content.parts[0].text;

        // Simple Markdown parsing for the response
        const htmlText = aiText
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n\n/g, '<br><br>')
            .replace(/\n/g, '<br>');

        contentDiv.innerHTML = htmlText;

    } catch (error) {
        contentDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
    }
};
