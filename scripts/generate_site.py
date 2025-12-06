import os
import re
import html

# Configuration
INPUT_FILE = "d717c9f4 (1).md"
OUTPUT_DIR = "output"
STYLES_PATH = "./css/styles.css"
SCRIPT_PATH = "./js/script.js"

def parse_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    chapters = []
    current_chapter = None
    current_section = None
    
    # Split by lines to process line by line or use regex for larger blocks
    # Using regex to match structure
    
    # 1. Split into Chapters (Level 1 Headers)
    # The file starts with some intro text before the first chapter. We can look for "# 1. "
    
    chapter_splits = re.split(r'^# (\d+\..*)$', content, flags=re.MULTILINE)
    
    # chapter_splits[0] is preamble.
    # chapter_splits[1] is title of ch1, chapter_splits[2] is content of ch1
    # chapter_splits[3] is title of ch2, chapter_splits[4] is content of ch2, etc.
    
    for i in range(1, len(chapter_splits), 2):
        title = chapter_splits[i].strip()
        body = chapter_splits[i+1]
        
        chapter_data = {
            'id': f"chapter_{i//2 + 1}",
            'title': title,
            'sections': []
        }
        
        # 2. Split Chapter into Sections (Level 2 Headers)
        # ## A. ...
        section_splits = re.split(r'^## ([A-Z]\..*)$', body, flags=re.MULTILINE)
        
        # section_splits[0] might be intro text for chapter (ignored usually)
        
        for k in range(1, len(section_splits), 2):
            sec_title = section_splits[k].strip()
            sec_body = section_splits[k+1]
            
            section_data = {
                'title': sec_title,
                'questions': []
            }
            
            # 3. Find Questions (Level 3 Headers)
            # ### Q1.1: ...
            # Questions have structure: ### Title \n **Question:** ... \n **Answer:** ...
            
            question_splits = re.split(r'^### (Q.*)$', sec_body, flags=re.MULTILINE)
            
            for m in range(1, len(question_splits), 2):
                q_title_full = question_splits[m].strip()
                q_body = question_splits[m+1]
                
                # Parse Question and Answer content
                # Look for **Question:** and **Answer:** or **Solution:** markers
                
                # Normalize line endings
                q_body = q_body.strip()
                
                # Regex to find the split between Question text and Answer text
                # Usually: **Question:** (text) (newline) **Answer:** (text)
                
                # Check for "Answer:" or "Solution:"
                split_match = re.search(r'\n(\*\*Answer:\*\*|\*\*Solution:\*\*)', q_body)
                
                if split_match:
                    q_text_raw = q_body[:split_match.start()]
                    a_text_raw = q_body[split_match.start() + len(split_match.group(1)):]
                    
                    # Remove the leading "**Question:**" if present
                    q_text_raw = re.sub(r'^\*\*Question:\*\*\s*', '', q_text_raw.strip())
                else:
                    # Fallback if structure is weird
                    q_text_raw = q_body
                    a_text_raw = "Answer parsing failed. Please check source."
                
                # Convert Markdown to basic HTML (paragraphs, code blocks)
                # Simple converter for this specific format
                def md_to_html(text):
                    # Escape HTML
                    text = html.escape(text)
                    
                    # Bold
                    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
                    
                    # Subscripts (e.g., v_x, F_1, v_boat)
                    # Pattern: Letter followed by underscore and alphanumeric sequence
                    # Avoid replacing if it looks like italic markdown (surrounded by underscores)
                    # We handle simple variable subscripts: v_y, F_net, etc.
                    text = re.sub(r'([a-zA-Z])_([a-zA-Z0-9]+)', r'\1<sub>\2</sub>', text)

                    # Code blocks
                    text = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', text, flags=re.DOTALL)
                    
                    # Lists
                    text = re.sub(r'^\s*-\s+(.*)', r'<li>\1</li>', text, flags=re.MULTILINE)
                    # Wrap adjacent lis in ul (simple hacky way: just let them be, or wrap later if needed. 
                    # For now, let's just make them divs with class list-item to avoid breaking invalid HTML)
                    text = re.sub(r'<li>(.*?)</li>', r'<div class="list-item">• \1</div>', text)

                    # Paragraphs (double newline)
                    paragraphs = text.split('\n\n')
                    return "".join([f"<p>{p.strip()}</p>" for p in paragraphs if p.strip()])

                section_data['questions'].append({
                    'id': q_title_full.split(':')[0].split(' ')[0], # e.g. Q1.1
                    'full_title': q_title_full,
                    'question_html': md_to_html(q_text_raw),
                    'answer_html': md_to_html(a_text_raw)
                })
            
            chapter_data['sections'].append(section_data)
        
        chapters.append(chapter_data)
        
    return chapters

def generate_html(chapters):
    # Base Template
    def get_page_content(title, body_content, nav_active_idx=None):
        nav_links = ""
        for idx, ch in enumerate(chapters):
            active_class = "active" if idx == nav_active_idx else ""
            nav_links += f'<a href="{ch["id"]}.html" class="nav-link {active_class}">{ch["title"]}</a>'
            
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap">
    <link rel="stylesheet" href="{STYLES_PATH}">
</head>
<body>
    <div class="app-container">
        <aside class="sidebar">
            <div class="brand">
                <h1>Phoenix Physics</h1>
            </div>
            <nav class="nav-menu">
                <a href="index.html" class="nav-link {'active' if nav_active_idx == -1 else ''}">Home</a>
                {nav_links}
            </nav>
        </aside>
        
        <main class="content-area">
            {body_content}
        </main>
    </div>
    <script src="{SCRIPT_PATH}"></script>
</body>
</html>"""

    # 1. Generate Index
    index_body = """
    <div class="hero">
        <h1>Physics Question Bank</h1>
        <p>Complete study guide with theory and numericals.</p>
        <div class="progress-overview">
            <div class="progress-card">
                <h3>Total Progress</h3>
                <div class="progress-bar-container">
                    <div class="progress-bar" id="total-progress"></div>
                </div>
                <span id="progress-text">0% Completed</span>
            </div>
        </div>
        <div class="chapter-grid">
    """
    for ch in chapters:
        index_body += f"""
            <a href="{ch['id']}.html" class="chapter-card">
                <h2>{ch['title']}</h2>
                <p>{len(ch['sections'])} Sections</p>
                <div class="mini-progress" data-chapter-id="{ch['id']}">0%</div>
            </a>
        """
    index_body += "</div></div>"
    
    with open(os.path.join(OUTPUT_DIR, "index.html"), 'w') as f:
        f.write(get_page_content("Physics Question Bank", index_body, -1))

    # 2. Generate Chapter Pages
    for idx, ch in enumerate(chapters):
        ch_body = f"""
        <header class="chapter-header">
            <h1>{ch['title']}</h1>
            <div class="chapter-progress-container">
                 <span id="chapter-progress-text">0/0 Completed</span>
                 <div class="progress-bar-bg"><div class="progress-bar-fill" id="chapter-progress-bar"></div></div>
            </div>
        </header>
        <div class="chapter-content">
        """
        
        for sec in ch['sections']:
            ch_body += f"""
            <section class="section-block">
                <h2 class="section-title">{sec['title']}</h2>
                <div class="questions-list">
            """
            for q in sec['questions']:
                ch_body += f"""
                <div class="question-card" id="{q['id']}">
                    <div class="question-header">
                        <label class="custom-checkbox">
                            <input type="checkbox" class="q-checkbox" data-id="{q['id']}">
                            <span class="checkmark"></span>
                        </label>
                        <h3 class="question-title">{q['full_title']}</h3>
                    </div>
                    <div class="question-body">
                        {q['question_html']}
                    </div>
                    <div class="answer-section">
                        <button class="toggle-answer-btn" onclick="toggleAnswer(this)">
                            <span class="icon">👁️</span> Show Answer
                        </button>
                        <div class="answer-content hidden">
                            <div class="answer-inner">
                                {q['answer_html']}
                            </div>
                            <div class="gemini-section">
                                <button class="ask-gemini-btn" onclick="askGemini(this, '{q['id']}')">
                                    <span class="icon">✨</span> Ask Gemini to Explain
                                </button>
                                <div class="gemini-response hidden" id="gemini-{q['id']}">
                                    <div class="gemini-content"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                """
            ch_body += "</div></section>"
            
        ch_body += "</div>" # End chapter content
        
        with open(os.path.join(OUTPUT_DIR, f"{ch['id']}.html"), 'w') as f:
            f.write(get_page_content(ch['title'], ch_body, idx))

if __name__ == "__main__":
    print("Parsing markdown...")
    try:
        chapters = parse_markdown(INPUT_FILE)
        print(f"Parsed {len(chapters)} chapters.")
        
        print("Generating HTML...")
        generate_html(chapters)
        print("Done! Website generated in 'output' directory.")
    except Exception as e:
        print(f"Error: {e}")
