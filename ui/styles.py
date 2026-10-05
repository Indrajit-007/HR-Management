"""
Custom CSS styles for the RAG-MCP Streamlit UI
"""

def get_custom_css():
    """Return custom CSS for the app with modern, classy design."""
    return """
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main App Background - Dark with gradient */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        background-attachment: fixed;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: rgba(15, 12, 41, 0.95);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        color: #e0e0e0;
    }
    
    /* Main Content Area */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Card/Container Styling - Glassmorphism */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Headers */
    h1 {
        color: #ffffff;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    h2 {
        color: #e0e0e0;
        font-weight: 600;
        font-size: 1.8rem;
        margin-top: 1.5rem;
    }
    
    h3 {
        color: #d0d0d0;
        font-weight: 500;
        font-size: 1.3rem;
    }
    
    /* Text Styling */
    p, li, span {
        color: #c0c0c0;
        line-height: 1.6;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        color: #ffffff;
        padding: 12px 16px;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid #6C63FF;
        box-shadow: 0 0 0 3px rgba(108, 99, 255, 0.1);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 32px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px 0 rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(102, 126, 234, 0.6);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Chat Messages */
    .chat-message {
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 12px;
        display: flex;
        align-items: flex-start;
        animation: slideIn 0.3s ease;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .chat-message.user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        margin-left: 20%;
    }
    
    .chat-message.assistant {
        background: rgba(255, 255, 255, 0.08);
        margin-right: 20%;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .chat-message .message-content {
        color: #ffffff;
        line-height: 1.6;
        margin-left: 12px;
    }
    
    .chat-message .avatar {
        font-size: 1.5rem;
        min-width: 40px;
    }
    
    /* Metrics/Stats Cards */
    [data-testid="stMetricValue"] {
        color: #ffffff;
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        color: #b0b0b0;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        color: #ffffff;
        font-weight: 500;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(255, 255, 255, 0.08);
    }
    
    /* Select Box */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        color: #ffffff;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #b0b0b0;
        font-weight: 500;
        padding: 12px 24px;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.08);
        color: #ffffff;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #ffffff !important;
    }
    
    /* Success/Info/Warning/Error Messages */
    .stSuccess {
        background: rgba(0, 200, 83, 0.15);
        border-left: 4px solid #00c853;
        border-radius: 8px;
        color: #00c853;
    }
    
    .stInfo {
        background: rgba(33, 150, 243, 0.15);
        border-left: 4px solid #2196f3;
        border-radius: 8px;
        color: #2196f3;
    }
    
    .stWarning {
        background: rgba(255, 152, 0, 0.15);
        border-left: 4px solid #ff9800;
        border-radius: 8px;
        color: #ff9800;
    }
    
    .stError {
        background: rgba(244, 67, 54, 0.15);
        border-left: 4px solid #f44336;
        border-radius: 8px;
        color: #f44336;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.3);
    }
    
    /* Code blocks */
    code {
        background: rgba(255, 255, 255, 0.1);
        padding: 2px 6px;
        border-radius: 4px;
        color: #ff79c6;
        font-size: 0.9em;
    }
    
    pre {
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 16px;
    }
    
    /* Loading Animation */
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
    
    .loading {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    /* Tool Badge */
    .tool-badge {
        display: inline-block;
        background: rgba(102, 126, 234, 0.2);
        color: #667eea;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 4px;
        border: 1px solid rgba(102, 126, 234, 0.3);
    }
    
    /* Response Container */
    .response-container {
        background: rgba(255, 255, 255, 0.05);
        border-left: 4px solid #667eea;
        border-radius: 8px;
        padding: 16px;
        margin: 12px 0;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    </style>
    """


def get_chat_message_html(message: str, is_user: bool = False):
    """Generate HTML for a chat message with avatars."""
    avatar = "👤" if is_user else "🤖"
    message_class = "user" if is_user else "assistant"
    
    return f"""
    <div class="chat-message {message_class}">
        <div class="avatar">{avatar}</div>
        <div class="message-content">{message}</div>
    </div>
    """


def get_tool_badge_html(tool_name: str):
    """Generate HTML for a tool badge."""
    return f'<span class="tool-badge">🔧 {tool_name}</span>'


def get_metric_card_html(title: str, value: str, icon: str = "📊"):
    """Generate HTML for a metric card."""
    return f"""
    <div class="glass-card" style="padding: 12px; margin-bottom: 8px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.5rem;">{icon}</span>
            <div style="flex: 1;">
                <div style="font-size: 0.75rem; color: #b0b0b0; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px;">{title}</div>
                <div style="font-size: 1.4rem; color: #ffffff; font-weight: 700;">{value}</div>
            </div>
        </div>
    </div>
    """