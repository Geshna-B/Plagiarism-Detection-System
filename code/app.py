#!/usr/bin/env python3
"""
Enhanced Flask Web UI for Plagiarism Detection with File Upload
"""
from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import tempfile
from datetime import datetime
from werkzeug.utils import secure_filename
import PyPDF2
import docx
from detectors.llm_integration import LLMIntegration
from detectors.automata_detector import PlagiarismDetector
from utils.reporting import ReportGenerator

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_uploaded_file(file):
    """Read content from uploaded file based on type"""
    try:
        if file.filename.endswith('.txt'):
            return file.read().decode('utf-8')
        
        elif file.filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        
        elif file.filename.endswith(('.docx', '.doc')):
            doc = docx.Document(file)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
    except Exception as e:
        raise Exception(f"Error reading file: {str(e)}")

class PlagiarismWebApp:
    def __init__(self):
        try:
            self.llm_integration = LLMIntegration()
            self.detector = PlagiarismDetector()
            self.reporter = ReportGenerator()
            self.initialized = True
            print("✅ Plagiarism detector initialized successfully")
        except Exception as e:
            print(f"❌ Initialization error: {e}")
            self.initialized = False
    
    def analyze_text(self, text, topic=None):
        if not self.initialized:
            return {'error': 'System not properly initialized'}
        
        try:
            # Use provided topic or auto-detect
            if not topic:
                topic = self._detect_topic(text)
            
            print(f"🔍 Analyzing text with topic: {topic}")
            
            # Get related content
            related_topics = self.llm_integration.expand_topic(topic)
            print(f"📚 Related topics: {related_topics}")
            
            source_texts = self.llm_integration.fetch_wikipedia_content(related_topics)
            
            if not source_texts:
                return {'error': 'No source content found'}
            
            print(f"✅ Found {len(source_texts)} source documents")
            
            # Detect plagiarism
            detection_results = self.detector.detect_plagiarism(text, source_texts)
            
            if detection_results.get('error'):
                return detection_results
            
            # Generate report
            report = self.reporter.generate_report(detection_results, text, source_texts)
            
            # Add source text excerpts to the report
            report['source_excerpts'] = []
            for source in source_texts:
                excerpt = source['content'][:500] + "..." if len(source['content']) > 500 else source['content']
                report['source_excerpts'].append({
                    'topic': source['topic'],
                    'excerpt': excerpt,
                    'full_length': len(source['content'])
                })
            
            return report
            
        except Exception as e:
            return {'error': f'Analysis failed: {str(e)}'}
    
    def _detect_topic(self, text):
        """Simple topic detection"""
        # Extract first meaningful words (skip common words)
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = [word for word in text.lower().split()[:20] if word not in common_words and len(word) > 3]
        return ' '.join(words[:3]) if words else 'general topic'

# Initialize the app
plagiarism_app = PlagiarismWebApp()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Check if it's a file upload or text input
        if 'file' in request.files:
            file = request.files['file']
            topic = request.form.get('topic', '').strip() or None
            
            if file.filename == '':
                return jsonify({'error': 'No file selected'})
            
            if file and allowed_file(file.filename):
                text = read_uploaded_file(file)
            else:
                return jsonify({'error': 'Invalid file type. Please upload TXT, PDF, or DOCX.'})
        else:
            data = request.get_json()
            text = data.get('text', '').strip()
            topic = data.get('topic', '').strip() or None
        
        if not text:
            return jsonify({'error': 'No text provided'})
        
        if len(text) < 50:
            return jsonify({'error': 'Text too short (minimum 50 characters)'})
        
        if len(text) > 100000:  # Limit text size
            return jsonify({'error': 'Text too long (maximum 100,000 characters)'})
        
        # Analyze the text
        results = plagiarism_app.analyze_text(text, topic)
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'})

@app.route('/download-report', methods=['POST'])
def download_report():
    """Download analysis report as JSON file"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No report data provided'})
        
        # Create a filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"plagiarism_report_{timestamp}.json"
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            temp_path = f.name
        
        return send_file(temp_path, 
                        as_attachment=True, 
                        download_name=filename,
                        mimetype='application/json')
        
    except Exception as e:
        return jsonify({'error': f'Download error: {str(e)}'})

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy', 
        'initialized': plagiarism_app.initialized,
        'timestamp': datetime.now().isoformat()
    })

def create_html_template():
    """Create the enhanced HTML template content"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plagiarism Detector | Automata Theory + AI</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #4361ee;
            --secondary: #3a0ca3;
            --success: #4cc9f0;
            --danger: #f72585;
            --warning: #f8961e;
            --info: #4895ef;
            --light: #f8f9fa;
            --dark: #212529;
            --gray: #6c757d;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: var(--dark);
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
            overflow: hidden;
            animation: fadeIn 0.8s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .header {
            background: linear-gradient(135deg, var(--secondary) 0%, var(--primary) 100%);
            color: white;
            padding: 40px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
            background-size: 20px 20px;
            animation: float 20s infinite linear;
        }
        
        @keyframes float {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            font-weight: 700;
            position: relative;
        }
        
        .header p {
            font-size: 1.3em;
            opacity: 0.9;
            position: relative;
        }
        
        .content {
            padding: 40px;
            display: grid;
            gap: 40px;
            grid-template-columns: 1fr 1.2fr;
        }
        
        @media (max-width: 1024px) {
            .content {
                grid-template-columns: 1fr;
            }
        }
        
        .input-section, .results-section {
            background: var(--light);
            padding: 30px;
            border-radius: 15px;
            border: 1px solid #e9ecef;
            box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        }
        
        .section-title {
            font-size: 1.5em;
            margin-bottom: 25px;
            color: var(--secondary);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .section-title i {
            color: var(--primary);
        }
        
        .tab-container {
            margin-bottom: 25px;
        }
        
        .tabs {
            display: flex;
            background: white;
            border-radius: 10px;
            padding: 5px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .tab {
            flex: 1;
            padding: 12px;
            text-align: center;
            cursor: pointer;
            border-radius: 8px;
            transition: all 0.3s ease;
            font-weight: 600;
        }
        
        .tab.active {
            background: var(--primary);
            color: white;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
            animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-10px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            margin-bottom: 10px;
            font-weight: 600;
            color: var(--dark);
            font-size: 1.1em;
        }
        
        textarea, input, .file-input {
            width: 100%;
            padding: 15px;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s ease;
            background: white;
        }
        
        textarea:focus, input:focus, .file-input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.1);
        }
        
        textarea {
            height: 200px;
            resize: vertical;
            line-height: 1.6;
        }
        
        .file-input {
            padding: 20px;
            border: 2px dashed #ced4da;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .file-input:hover {
            border-color: var(--primary);
            background: #f8f9ff;
        }
        
        .file-input.dragover {
            border-color: var(--success);
            background: #f0f9ff;
        }
        
        .file-info {
            margin-top: 10px;
            font-size: 0.9em;
            color: var(--gray);
        }
        
        .btn {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            border: none;
            padding: 18px 30px;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            box-shadow: 0 5px 15px rgba(67, 97, 238, 0.3);
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(67, 97, 238, 0.4);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .btn:disabled {
            background: #bdc3c7;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .btn-secondary {
            background: linear-gradient(135deg, var(--gray) 0%, #495057 100%);
        }
        
        .btn-success {
            background: linear-gradient(135deg, var(--success) 0%, #00b4d8 100%);
        }
        
        .error {
            background: var(--danger);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            animation: shake 0.5s ease;
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
        }
        
        .loading {
            text-align: center;
            padding: 50px;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid var(--primary);
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        /* Circular Progress */
        .progress-container {
            position: relative;
            width: 200px;
            height: 200px;
            margin: 0 auto 30px auto;
        }
        
        .circular-progress {
            transform: rotate(-90deg);
        }
        
        .progress-bg {
            fill: none;
            stroke: #e9ecef;
            stroke-width: 8;
        }
        
        .progress-fill {
            fill: none;
            stroke: var(--primary);
            stroke-width: 8;
            stroke-linecap: round;
            stroke-dasharray: 565.48;
            stroke-dashoffset: 565.48;
            transition: stroke-dashoffset 1s ease;
        }
        
        .progress-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        }
        
        .progress-value {
            font-size: 2.5em;
            font-weight: bold;
            color: var(--dark);
        }
        
        .progress-label {
            font-size: 1em;
            color: var(--gray);
        }
        
        .risk-badge {
            display: inline-block;
            padding: 10px 25px;
            border-radius: 25px;
            font-weight: bold;
            color: white;
            margin: 15px 0;
            font-size: 1.1em;
            box-shadow: 0 3px 10px rgba(0,0,0,0.2);
        }
        
        .risk-high { background: linear-gradient(135deg, #e74c3c, #c0392b); }
        .risk-medium { background: linear-gradient(135deg, #f39c12, #e67e22); }
        .risk-low { background: linear-gradient(135deg, #27ae60, #2ecc71); }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin: 25px 0;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-3px);
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: var(--primary);
            margin: 10px 0;
        }
        
        .matches-list {
            max-height: 400px;
            overflow-y: auto;
            margin: 20px 0;
        }
        
        .match-item {
            background: white;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 12px;
            border-left: 5px solid var(--info);
            box-shadow: 0 3px 10px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
        }
        
        .match-item:hover {
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.12);
        }
        
        .sources-list {
            margin: 20px 0;
        }
        
        .source-item {
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 3px solid var(--success);
        }
        
        .source-excerpt {
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid var(--warning);
            font-style: italic;
            color: #495057;
        }
        
        .success-message {
            background: var(--success);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin: 20px 0;
        }
        
        .feature-list {
            margin: 20px 0;
        }
        
        .feature-item {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
            padding: 10px;
            background: rgba(67, 97, 238, 0.1);
            border-radius: 8px;
        }
        
        .feature-item i {
            color: var(--primary);
        }
        
        .action-buttons {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-search"></i> Advanced Plagiarism Detector</h1>
            <p>Automata Theory + AI-Powered Source Analysis</p>
        </div>
        
        <div class="content">
            <div class="input-section">
                <h2 class="section-title"><i class="fas fa-upload"></i> Input Methods</h2>
                
                <div class="tab-container">
                    <div class="tabs">
                        <div class="tab active" onclick="switchTab('textTab')">📝 Text Input</div>
                        <div class="tab" onclick="switchTab('fileTab')">📁 File Upload</div>
                    </div>
                    
                    <div id="textTab" class="tab-content active">
                        <div class="form-group">
                            <label for="textInput"><i class="fas fa-align-left"></i> Enter text to analyze:</label>
                            <textarea id="textInput" placeholder="Paste your text here (minimum 50 characters)..."></textarea>
                        </div>
                        
                        <div class="form-group">
                            <label for="topicInput"><i class="fas fa-tag"></i> Main topic :</label>
                            <input type="text" id="topicInput" placeholder="e.g., artificial intelligence, physics, history...">
                            <small style="color: #666; margin-top: 5px; display: block;">Helps find more relevant sources for better accuracy</small>
                        </div>
                    </div>
                    
                    <div id="fileTab" class="tab-content">
                        <div class="form-group">
                            <label for="fileInput"><i class="fas fa-file-upload"></i> Upload document:</label>
                            <div class="file-input" id="fileDropArea">
                                <i class="fas fa-cloud-upload-alt" style="font-size: 2em; color: #4361ee; margin-bottom: 10px;"></i>
                                <p>Click to select or drag & drop your file</p>
                                <p style="font-size: 0.9em; color: #666; margin-top: 5px;">Supported formats: TXT, PDF, DOCX (Max 16MB)</p>
                            </div>
                            <input type="file" id="fileInput" accept=".txt,.pdf,.docx,.doc" style="display: none;">
                            <div id="fileInfo" class="file-info"></div>
                        </div>
                        
                        <div class="form-group">
                            <label for="fileTopicInput"><i class="fas fa-tag"></i> Document topic:</label>
                            <input type="text" id="fileTopicInput" placeholder="e.g., research paper, essay, article topic...">
                        </div>
                    </div>
                </div>
                
                <button class="btn" onclick="analyzeContent()" id="analyzeBtn">
                    <i class="fas fa-search"></i> Analyze for Plagiarism
                </button>
                
                <div class="feature-list">
                    <div class="feature-item">
                        <i class="fas fa-robot"></i>
                        <span>AI-Powered source discovery</span>
                    </div>
                    <div class="feature-item">
                        <i class="fas fa-sitemap"></i>
                        <span>Automata theory pattern matching</span>
                    </div>
                    <div class="feature-item">
                        <i class="fas fa-database"></i>
                        <span>Wikipedia integration</span>
                    </div>
                    <div class="feature-item">
                        <i class="fas fa-chart-bar"></i>
                        <span>Detailed similarity analysis</span>
                    </div>
                </div>
                
                <div id="errorMessage" class="error" style="display: none;"></div>
            </div>
            
            <div class="results-section">
                <h2 class="section-title"><i class="fas fa-chart-bar"></i> Analysis Results</h2>
                
                <div id="results">
                    <div class="loading" id="loading" style="display: none;">
                        <div class="spinner"></div>
                        <p>Analyzing content for plagiarism...</p>
                        <p style="color: #666; margin-top: 10px;">This may take a few moments</p>
                    </div>
                    
                    <div id="resultsContent">
                        <div style="text-align: center; padding: 40px; color: #666;">
                            <i class="fas fa-search" style="font-size: 3em; margin-bottom: 20px; color: #ccc;"></i>
                            <h3>Ready to Analyze</h3>
                            <p>Enter text or upload a file to check for plagiarism</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentTab = 'textTab';
        let currentFile = null;
        let currentReportData = null;
        
        function switchTab(tabName) {
            // Update tabs
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            // Activate selected tab
            event.target.classList.add('active');
            document.getElementById(tabName).classList.add('active');
            currentTab = tabName;
        }
        
        // File upload handling
        document.getElementById('fileInput').addEventListener('change', handleFileSelect);
        document.getElementById('fileDropArea').addEventListener('click', () => document.getElementById('fileInput').click());
        
        // Drag and drop functionality
        const fileDropArea = document.getElementById('fileDropArea');
        fileDropArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            fileDropArea.classList.add('dragover');
        });
        
        fileDropArea.addEventListener('dragleave', () => {
            fileDropArea.classList.remove('dragover');
        });
        
        fileDropArea.addEventListener('drop', (e) => {
            e.preventDefault();
            fileDropArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFiles(files[0]);
            }
        });
        
        function handleFileSelect(e) {
            handleFiles(e.target.files[0]);
        }
        
        function handleFiles(file) {
            if (file && allowedFile(file.name)) {
                currentFile = file;
                document.getElementById('fileInfo').innerHTML = `
                    <i class="fas fa-check-circle" style="color: #27ae60;"></i>
                    <strong>${file.name}</strong> (${formatFileSize(file.size)})
                `;
            } else {
                showError('Please select a valid file (TXT, PDF, DOCX)');
            }
        }
        
        function allowedFile(filename) {
            const allowed = ['txt', 'pdf', 'docx', 'doc'];
            const extension = filename.split('.').pop().toLowerCase();
            return allowed.includes(extension);
        }
        
        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
        
        function analyzeContent() {
            const analyzeBtn = document.getElementById('analyzeBtn');
            const loading = document.getElementById('loading');
            const errorMessage = document.getElementById('errorMessage');
            const resultsContent = document.getElementById('resultsContent');
            
            // Clear previous results and errors
            errorMessage.style.display = 'none';
            resultsContent.innerHTML = '';
            currentReportData = null;
            
            let text, topic;
            
            if (currentTab === 'textTab') {
                text = document.getElementById('textInput').value.trim();
                topic = document.getElementById('topicInput').value.trim() || null;
                
                if (text.length < 50) {
                    showError('Please enter at least 50 characters of text.');
                    return;
                }
            } else {
                if (!currentFile) {
                    showError('Please select a file to upload.');
                    return;
                }
                topic = document.getElementById('fileTopicInput').value.trim() || null;
            }
            
            loading.style.display = 'block';
            analyzeBtn.disabled = true;
            analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
            
            const formData = new FormData();
            if (currentTab === 'fileTab') {
                formData.append('file', currentFile);
                formData.append('topic', topic || '');
            } else {
                formData.append('text', text);
                formData.append('topic', topic || '');
            }
            
            fetch('/analyze', {
                method: 'POST',
                body: currentTab === 'fileTab' ? formData : JSON.stringify({text, topic}),
                headers: currentTab === 'fileTab' ? {} : {'Content-Type': 'application/json'}
            })
            .then(response => response.json())
            .then(data => {
                loading.style.display = 'none';
                analyzeBtn.disabled = false;
                analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze for Plagiarism';
                
                if (data.error) {
                    showError(data.error);
                } else {
                    currentReportData = data;
                    displayResults(data);
                }
            })
            .catch(error => {
                loading.style.display = 'none';
                analyzeBtn.disabled = false;
                analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze for Plagiarism';
                showError('Network error: ' + error.message);
            });
        }
        
        function downloadReport() {
            if (!currentReportData) {
                showError('No report data available to download.');
                return;
            }
            
            fetch('/download-report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(currentReportData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Download failed');
                }
                return response.blob();
            })
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = `plagiarism_report_${new Date().toISOString().slice(0, 10)}.json`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            })
            .catch(error => {
                showError('Download error: ' + error.message);
            });
        }
        
        function showError(message) {
            const errorMessage = document.getElementById('errorMessage');
            errorMessage.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
            errorMessage.style.display = 'block';
        }
        
        function displayResults(data) {
            const resultsContent = document.getElementById('resultsContent');
            const similarity = (data.overall_similarity * 100).toFixed(1);
            const riskLevel = data.risk_level || 'UNKNOWN';
            
            // Update circular progress
            const circumference = 565.48;
            const offset = circumference - (similarity / 100) * circumference;
            
            let riskClass = 'risk-low';
            let riskColor = '#27ae60';
            if (riskLevel === 'HIGH') {
                riskClass = 'risk-high';
                riskColor = '#e74c3c';
            } else if (riskLevel === 'MEDIUM') {
                riskClass = 'risk-medium';
                riskColor = '#f39c12';
            }
            
            let resultsHTML = `
                <div class="progress-container">
                    <svg class="circular-progress" width="200" height="200">
                        <circle class="progress-bg" cx="100" cy="100" r="90"></circle>
                        <circle class="progress-fill" cx="100" cy="100" r="90" 
                                style="stroke-dashoffset: ${offset}; stroke: ${riskColor};"></circle>
                    </svg>
                    <div class="progress-text">
                        <div class="progress-value">${similarity}%</div>
                        <div class="progress-label">Similarity</div>
                    </div>
                </div>
                
                <div class="risk-badge ${riskClass}">
                    <i class="fas fa-${riskLevel === 'HIGH' ? 'exclamation-triangle' : 
                                      riskLevel === 'MEDIUM' ? 'info-circle' : 'check-circle'}"></i>
                    ${riskLevel} RISK
                </div>
                
                <div class="action-buttons">
                    <button class="btn btn-success" onclick="analyzeContent()">
                        <i class="fas fa-redo"></i> Re-analyze
                    </button>
                    <button class="btn btn-secondary" onclick="downloadReport()" ${!currentReportData ? 'disabled' : ''}>
                        <i class="fas fa-download"></i> Download Report
                    </button>
                </div>
            
            `;
            
            // Display Wikipedia source excerpts
            if (data.source_excerpts && data.source_excerpts.length > 0) {
                resultsHTML += `
                    <h3 style="margin: 30px 0 15px 0; color: var(--secondary);">
                        <i class="fas fa-wikipedia-w"></i> Wikipedia Sources Analyzed
                    </h3>
                    <div class="sources-list">
                `;
                
                data.source_excerpts.forEach((source, index) => {
                    resultsHTML += `
                        <div class="source-item">
                            <div class="source-excerpt">
                                <i class="fas fa-quote-left"></i> ${source.excerpt} <i class="fas fa-quote-right"></i>
                            </div>
                        </div>
                    `;
                });
                
                resultsHTML += `</div>`;
            }
            
            if (data.detailed_matches && data.detailed_matches.length > 0) {
                resultsHTML += `
                    <h3 style="margin: 30px 0 15px 0; color: var(--secondary);">
                        <i class="fas fa-search"></i> Detected Pattern Matches
                    </h3>
                    <div class="matches-list">
                `;
                
                data.detailed_matches.slice(0, 5).filter((_, i) => i % 3 === 0).forEach((match, index) => {
                    resultsHTML += `
                        <div class="match-item">
                            <strong>Pattern ${index + 1}:</strong> "${match.pattern}"<br>
                            <small style="color: #666;">
                                <i class="fas fa-map-marker-alt"></i> Position: ${match.position}
                            </small>
                        </div>
                    `;
                });
                
                if (data.detailed_matches.length > 5) {
                    resultsHTML += `<p style="text-align: center; color: #666; margin: 10px 0;">
                        ... and ${data.detailed_matches.length - 5} more matches
                    </p>`;
                }
                
                resultsHTML += `</div>`;
            } else {
                resultsHTML += `
                    <div class="success-message">
                        <i class="fas fa-check-circle" style="font-size: 2em; margin-bottom: 10px;"></i>
                        <h3>No Significant Matches Found</h3>
                        <p>This appears to be original content!</p>
                    </div>
                `;
            }
            
            if (data.sources_used && data.sources_used.length > 0) {

                resultsHTML += `</div>`;
            }
            
            
            resultsContent.innerHTML = resultsHTML;
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                analyzeContent();
            }
        }
        );
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create the HTML template
    with open('templates/index.html', 'w') as f:
        f.write(create_html_template())
    
    print("🚀 Starting Plagiarism Detection Server...")
    print("📍 Local URL: http://localhost:3000")
    print("🌐 Network URL: http://192.0.0.2:3000")
    print("⏹️  Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=3000)