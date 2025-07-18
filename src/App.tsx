import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import DocumentUpload from './components/DocumentUpload';
import DocumentManagement from './components/DocumentManagement';
import TrainingCard from './components/TrainingCard';
import InferenceCard from './components/InferenceCard';
import ProfilePopup from './components/ProfilePopup';
import TrainingPopup from './components/TrainingPopup';
import Logs from './components/Logs';
import ResponseDisplay from './components/ResponseDisplay';
import KnowledgeGraphD3, { KnowledgeGraphHandle } from './components/KnowledgeGraphD3';
import { getTrainingCategories } from './utils/api';

const App: React.FC = () => {
    const [response, setResponse] = useState<string>('');
    const [error, setError] = useState<string>('');
    const [logs, setLogs] = useState<string[]>([]);
    const [dragActive, setDragActive] = useState<boolean>(false);
    const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
    const [selectedTraining, setSelectedTraining] = useState<string>('');
    const [showTrainingDropdown, setShowTrainingDropdown] = useState<boolean>(false);
    const [selectedUploadType, setSelectedUploadType] = useState<string>('');
    const [showUploadDropdown, setShowUploadDropdown] = useState<boolean>(false);
    const [selectedCategory, setSelectedCategory] = useState<string>('');
    const [showCategoryDropdown, setShowCategoryDropdown] = useState<boolean>(false);
    const [documents, setDocuments] = useState<any[]>([]);
    const [showDocuments, setShowDocuments] = useState<boolean>(false);
    const [showPopup, setShowPopup] = useState<boolean>(false);
    const [popupContent, setPopupContent] = useState<string>('');
    const [popupTitle, setPopupTitle] = useState<string>('');
    const [showTrainingPopup, setShowTrainingPopup] = useState<boolean>(false);
    const [trainingCategories, setTrainingCategories] = useState<any[]>([]);
    const [loadingCategories, setLoadingCategories] = useState<boolean>(false);

    const dropdownRef = useRef<HTMLDivElement>(null);
    const uploadDropdownRef = useRef<HTMLDivElement>(null);
    const categoryDropdownRef = useRef<HTMLDivElement>(null);
    const knowledgeGraphRef = useRef<KnowledgeGraphHandle>(null);

    const API_BASE_URL = 'http://localhost:8089';

    const trainingOptions = [
        'Questions about my knowledge',
        'Questions about my feelings and 5 personalities',
        'Question about the importance of people in my life',
        'Iteratively add to a knowledge graph',
        'Preferences',
        'Moral questions',
        'Automatic questions to extend known knowledge'
    ];

    const uploadTypeOptions = [
        'Text written information',
        'File',
        'Folder',
        'Chat history',
        'Voice recording',
        'Voice transcription',
        'Image'
    ];

    const categoryOptions = [
        'Search history',
        'Whatsapp chats',
        'Conversations during day',
        'Journals',
        'Essays',
        'CV',
        'Image',
        'Other'
    ];

    const popupCategories = [
        'Contacts',
        'Character',
        'Knowledge',
        'Morals',
        '5 Personalities',
        'Memories',
        'History',
        'Facts'
    ];

    const mockContent: Record<string, string> = {
        'Contacts': `
            👥 Important Contacts in My Life
            
            • Family Members:
              - Mom: Always supportive, calls every Sunday
              - Dad: Great advice giver, loves discussing current events
              - Sister: Best friend, shares my love for movies
            
            • Close Friends:
              - Alex: College roommate, now works in tech
              - Sarah: Childhood friend, amazing baker
              - Mike: Gym buddy, always motivates me
            
            • Professional Network:
              - Dr. Johnson: Mentor from university
              - Lisa: Former colleague, now at startup
              - David: Industry contact, great networker
            
            • Community Connections:
              - Local coffee shop owner
              - Neighbor who helps with garden
              - Volunteer coordinator at animal shelter
        `,
        'Character': `
            🎭 Character Profile
            
            Core Values:
            • Integrity - Always strive to do the right thing
            • Empathy - Understanding others' perspectives
            • Growth - Continuous learning and improvement
            • Authenticity - Being true to myself
            
            Personality Traits:
            • Naturally curious and inquisitive
            • Optimistic outlook on life
            • Organized and detail-oriented
            • Enjoys helping others succeed
            
            Strengths:
            • Problem-solving abilities
            • Good listener and communicator
            • Adaptable to new situations
            • Reliable and trustworthy
            
            Areas for Growth:
            • Sometimes overthink decisions
            • Can be too hard on myself
            • Need to work on saying "no" more often
        `,
        'Knowledge': `
            🧠 Knowledge Areas
            
            Technical Skills:
            • Programming languages: Python, JavaScript, React
            • Database management: MongoDB, PostgreSQL
            • Machine learning basics and AI concepts
            • Web development and API design
            
            Academic Background:
            • Computer Science degree
            • Mathematics and statistics
            • Research methodology
            • Data analysis and visualization
            
            Interests & Hobbies:
            • Reading about emerging technologies
            • Photography and visual arts
            • Cooking and trying new recipes
            • Hiking and outdoor activities
            
            Professional Experience:
            • Software development projects
            • Team leadership and collaboration
            • Project management
            • Client communication and support
        `,
        'Morals': `
            ⚖️ Moral Framework
            
            Ethical Principles:
            • Honesty and transparency in all dealings
            • Respect for others' rights and dignity
            • Responsibility for my actions and their consequences
            • Fairness and equality in treatment of others
            
            Decision-Making Guidelines:
            • Consider impact on all stakeholders
            • Choose actions that align with core values
            • Seek to minimize harm while maximizing benefit
            • Take responsibility for mistakes and learn from them
            
            Social Responsibilities:
            • Environmental consciousness
            • Supporting community initiatives
            • Advocating for justice and equality
            • Mentoring and helping others grow
            
            Personal Standards:
            • Keep promises and commitments
            • Treat everyone with respect
            • Stand up for what's right
            • Practice gratitude and humility
        `,
        '5 Personalities': `
            🎨 Five Personality Aspects
            
            1. The Analyst 🔍
            - Loves solving complex problems
            - Methodical and systematic approach
            - Enjoys research and data analysis
            - Thrives on intellectual challenges
            
            2. The Creator 🎨
            - Enjoys building and making things
            - Imaginative and innovative
            - Sees possibilities everywhere
            - Loves artistic expression
            
            3. The Connector 🤝
            - Values relationships and community
            - Empathetic and understanding
            - Good at bringing people together
            - Enjoys collaborative work
            
            4. The Explorer 🌍
            - Curious about the world
            - Loves trying new experiences
            - Adaptable and flexible
            - Enjoys travel and adventure
            
            5. The Nurturer 🌱
            - Cares deeply about others' wellbeing
            - Protective and supportive
            - Enjoys helping others grow
            - Values stability and security
        `,
        'Memories': `
            💭 Significant Memories
            
            Childhood Moments:
            • First day of school - mix of excitement and nervousness
            • Learning to ride a bike with Dad's patient encouragement
            • Family camping trips in the summer
            • Grandmother's homemade cookies and bedtime stories
            
            Educational Milestones:
            • Graduating from high school - sense of accomplishment
            • First programming project that actually worked
            • Presenting research at university conference
            • Mentor's advice that changed my perspective
            
            Personal Achievements:
            • Completing first marathon
            • Solo travel adventure to new country
            • Learning to cook family recipe
            • Overcoming public speaking fear
            
            Relationship Memories:
            • Meeting best friend in college
            • Important conversations with family
            • Moments of connection with colleagues
            • Times when I helped someone through difficulty
        `,
        'History': `
            📚 Personal History Timeline
            
            Early Years (Childhood):
            • Born in small town, close-knit community
            • Moved to city for better opportunities
            • Developed love for reading and learning
            • Participated in school science fairs
            
            Education Phase:
            • High school: Discovered passion for technology
            • University: Studied computer science
            • Internships: Gained practical experience
            • Thesis project: AI-related research
            
            Career Development:
            • First job: Junior developer position
            • Skill building: Learned multiple technologies
            • Leadership roles: Led small team projects
            • Current focus: AI and machine learning
            
            Personal Growth:
            • Overcame challenges with persistence
            • Developed strong work ethic
            • Built meaningful relationships
            • Continuous learning mindset
        `,
        'Facts': `
            📊 Quick Facts About Me
            
            Basic Information:
            • Prefers morning productivity over night work
            • Coffee enthusiast - tries new cafes regularly
            • Keeps a daily journal for reflection
            • Enjoys both fiction and non-fiction books
            
            Preferences:
            • Favorite season: Spring (new beginnings)
            • Preferred work environment: Quiet with natural light
            • Communication style: Direct but considerate
            • Problem-solving approach: Methodical and collaborative
            
            Habits & Routines:
            • Morning exercise or walk
            • Weekly meal planning and prep
            • Regular check-ins with friends and family
            • Continuous learning through online courses
            
            Interesting Details:
            • Can solve a Rubik's cube in under 2 minutes
            • Speaks two languages fluently
            • Has visited 15 different countries
            • Volunteers at local animal shelter monthly
        `
    };

    const log = (message: string) => {
        const timestamp = new Date().toISOString();
        const logEntry = `[${timestamp}] ${message}`;
        console.log(logEntry);
        setLogs(prev => [...prev, logEntry]);
    };

    const loadTrainingCategories = async () => {
        try {
            setLoadingCategories(true);
            log('Loading training categories from backend...');
            
            const data = await getTrainingCategories();
            setTrainingCategories(data.categories);
            
            log(`Training categories loaded: ${data.categories.length} categories`);
            data.categories.forEach((category: any) => {
                log(`  - ${category.category}: ${category.total_questions} questions`);
            });
            
        } catch (error: any) {
            log(`Error loading training categories: ${error.message}`);
            setError(error.message);
        } finally {
            setLoadingCategories(false);
        }
    };

    useEffect(() => {
        log('Frontend application started');
        log('Hello World from Frontend!');
        log('MongoDB integration enabled - port 8088');
        
        // Load training categories on startup
        loadTrainingCategories();
    }, []);

    // Handle click outside dropdown to close it
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setShowTrainingDropdown(false);
            }
            if (uploadDropdownRef.current && !uploadDropdownRef.current.contains(event.target as Node)) {
                setShowUploadDropdown(false);
            }
            if (categoryDropdownRef.current && !categoryDropdownRef.current.contains(event.target as Node)) {
                setShowCategoryDropdown(false);
            }
        };

        // Add event listener when any dropdown is open
        if (showTrainingDropdown || showUploadDropdown || showCategoryDropdown) {
            document.addEventListener('mousedown', handleClickOutside);
        }

        // Cleanup event listener
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [showTrainingDropdown, showUploadDropdown, showCategoryDropdown]);

    const callBackend = async () => {
        try {
            log('Calling backend API...');
            setError('');
            setResponse('');
            
            const result = await axios.get(`${API_BASE_URL}/hello`);
            
            log(`Backend response received: ${JSON.stringify(result.data)}`);
            setResponse(result.data.message);
            
        } catch (err: any) {
            const errorMessage = err.response?.data?.detail || err.message || 'Unknown error';
            log(`Error calling backend: ${errorMessage}`);
            setError(errorMessage);
        }
    };

    const loadDocuments = async () => {
        try {
            log('Loading documents from MongoDB...');
            setError('');
            
            const result = await axios.get(`${API_BASE_URL}/documents`);
            
            log(`Documents loaded: ${result.data.documents.length} documents`);
            setDocuments(result.data.documents);
            setShowDocuments(true);
            
        } catch (err: any) {
            const errorMessage = err.response?.data?.detail || err.message || 'Unknown error';
            log(`Error loading documents: ${errorMessage}`);
            setError(errorMessage);
        }
    };

    const deleteDocument = async (documentId: string, filename: string) => {
        try {
            log(`Deleting document: ${filename}`);
            setError('');
            
            const result = await axios.delete(`${API_BASE_URL}/documents/${documentId}`);
            
            log(`Document deleted successfully: ${filename}`);
            setResponse(result.data.message);
            
            // Refresh documents list
            await loadDocuments();
            
        } catch (err: any) {
            const errorMessage = err.response?.data?.detail || err.message || 'Unknown error';
            log(`Error deleting document: ${errorMessage}`);
            setError(errorMessage);
        }
    };

    const downloadDocument = async (documentId: string, filename: string) => {
        try {
            log(`Downloading document: ${filename}`);
            setError('');
            
            const result = await axios.get(`${API_BASE_URL}/documents/${documentId}`, {
                responseType: 'blob'
            });
            
            // Create download link
            const url = window.URL.createObjectURL(new Blob([result.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
            
            log(`Document downloaded successfully: ${filename}`);
            setResponse(`Downloaded: ${filename}`);
            
        } catch (err: any) {
            const errorMessage = err.response?.data?.detail || err.message || 'Unknown error';
            log(`Error downloading document: ${errorMessage}`);
            setError(errorMessage);
        }
    };

    // File upload handlers
    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true);
        } else if (e.type === 'dragleave') {
            setDragActive(false);
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        
        const files = Array.from(e.dataTransfer.files);
        handleFiles(files);
    };

    const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files ? Array.from(e.target.files) : [];
        handleFiles(files);
    };

    const handleFiles = (files: File[]) => {
        log(`Processing ${files.length} files for upload`);
        setUploadedFiles(prev => [...prev, ...files]);
        
        files.forEach(file => {
            log(`File added: ${file.name} (${file.type}, ${file.size} bytes)`);
        });
    };

    const uploadFiles = async () => {
        if (uploadedFiles.length === 0) {
            log('No files to upload');
            return;
        }

        try {
            log(`Uploading ${uploadedFiles.length} files to MongoDB...`);
            setError('');
            const formData = new FormData();
            
            uploadedFiles.forEach((file) => {
                formData.append(`files`, file);
            });

            // Add category information if selected
            if (selectedCategory) {
                formData.append('category', selectedCategory);
                log(`Upload category: ${selectedCategory}`);
            }

            const result = await axios.post(`${API_BASE_URL}/upload`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            log(`Upload successful: ${JSON.stringify(result.data)}`);
            setResponse(`Uploaded ${uploadedFiles.length} files to MongoDB successfully`);
            setUploadedFiles([]);
            
            // Refresh documents list
            await loadDocuments();
            
        } catch (err: any) {
            const errorMessage = err.response?.data?.detail || err.message || 'Upload failed';
            log(`Upload error: ${errorMessage}`);
            setError(errorMessage);
        }
    };

    const handleTrainingSelect = (option: string) => {
        setSelectedTraining(option);
        setShowTrainingDropdown(false);
        log(`Training option selected: ${option}`);
    };

    const handleUploadTypeSelect = (option: string) => {
        setSelectedUploadType(option);
        setShowUploadDropdown(false);
        log(`Upload type selected: ${option}`);
        // TODO: Implement upload type functionality
    };

    const handleCategorySelect = (option: string) => {
        setSelectedCategory(option);
        setShowCategoryDropdown(false);
        log(`Category selected: ${option}`);
    };

    const handleInference = () => {
        log('Inference button clicked - functionality not implemented yet');
        setResponse('Inference functionality coming soon!');
    };

    const handleStartTraining = () => {
        if (!selectedTraining) {
            log('No training category selected');
            setError('Please select a training category first');
            return;
        }
        
        log(`Starting training for category: ${selectedTraining}`);
        setShowTrainingPopup(true);
    };

    const handleTrainingComplete = () => {
        log('Training completed - refreshing knowledge graph...');
        if (knowledgeGraphRef.current) {
            knowledgeGraphRef.current.refresh();
            log('Knowledge graph refreshed successfully');
        }
        // Refresh categories to update question counts
        loadTrainingCategories();
    };

    const formatFileSize = (bytes: number): string => {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    const formatDate = (dateString: string): string => {
        return new Date(dateString).toLocaleString();
    };

    const openPopup = (category: string) => {
        setPopupTitle(category);
        setPopupContent(mockContent[category]);
        setShowPopup(true);
        log(`Opened popup for category: ${category}`);
    };

    const closePopup = () => {
        setShowPopup(false);
        setPopupTitle('');
        setPopupContent('');
        log('Closed popup');
    };

    return (
        <div className="container">
            <h1>Model Myself - MongoDB Document Storage</h1>
            <p>Welcome to the Model Myself platform with MongoDB integration!</p>
            <div className="cards-container">
                <DocumentUpload
                    categoryOptions={categoryOptions}
                    selectedCategory={selectedCategory}
                    showCategoryDropdown={showCategoryDropdown}
                    setShowCategoryDropdown={setShowCategoryDropdown}
                    handleCategorySelect={handleCategorySelect}
                    handleDrag={handleDrag}
                    handleDrop={handleDrop}
                    handleFileInput={handleFileInput}
                    uploadedFiles={uploadedFiles}
                    uploadFiles={uploadFiles}
                    formatFileSize={formatFileSize}
                    categoryDropdownRef={categoryDropdownRef}
                />
                <DocumentManagement
                    documents={documents}
                    showDocuments={showDocuments}
                    loadDocuments={loadDocuments}
                    deleteDocument={deleteDocument}
                    downloadDocument={downloadDocument}
                    formatFileSize={formatFileSize}
                    formatDate={formatDate}
                />
                <TrainingCard
                    trainingOptions={trainingCategories.map(cat => `${cat.category} (${cat.total_questions} questions)`)}
                    selectedTraining={selectedTraining}
                    showTrainingDropdown={showTrainingDropdown}
                    setShowTrainingDropdown={setShowTrainingDropdown}
                    handleTrainingSelect={handleTrainingSelect}
                    onStartTraining={handleStartTraining}
                    loadingCategories={loadingCategories}
                />
                <InferenceCard
                    onInferenceClick={handleInference}
                />
            </div>
            <KnowledgeGraphD3 ref={knowledgeGraphRef} />
            <div className="central-action">
                <button 
                    onClick={() => setShowPopup(true)}
                    className="explore-btn"
                >
                    🔍 Explore My Profile
                </button>
            </div>
            <ProfilePopup
                showPopup={showPopup}
                closePopup={closePopup}
                popupTitle={popupTitle}
                popupContent={popupContent}
                popupCategories={popupCategories}
                openPopup={openPopup}
                setPopupTitle={setPopupTitle}
                setPopupContent={setPopupContent}
            />
            <TrainingPopup
                showPopup={showTrainingPopup}
                category={selectedTraining.split(' (')[0]} // Extract category name without question count
                onClose={() => setShowTrainingPopup(false)}
                onLog={log}
                onTrainingComplete={handleTrainingComplete}
            />
            <div className="bottom-sections">
                <ResponseDisplay response={response} error={error} />
                <Logs logs={logs} />
            </div>
        </div>
    );
};

export default App; 