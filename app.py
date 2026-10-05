"""
RAG-MCP Intelligent Assistant - Streamlit UI
Professional, classy, interactive interface
"""

import streamlit as st
import asyncio
import os
import sys
from datetime import datetime







# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))





from orchestrator import CollegeAssistantOrchestrator
from ui.styles import get_custom_css, get_chat_message_html, get_tool_badge_html, get_metric_card_html




# Page Configuration
st.set_page_config(
    page_title="RAG-MCP Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = None
    
if "query_count" not in st.session_state:
    st.session_state.query_count = 0
    
if "tools_used" not in st.session_state:
    st.session_state.tools_used = []


def initialize_orchestrator():
    """Initialize the orchestrator with API key."""
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not groq_api_key:
        st.error("🔑 GROQ_API_KEY not found in environment variables!")
        st.info("Please set your GROQ_API_KEY environment variable and restart the app.")
        st.stop()
    
    try:
        with st.spinner("🔧 Initializing AI Assistant..."):
            st.session_state.orchestrator = CollegeAssistantOrchestrator(groq_api_key)
        st.success("✅ Assistant ready!")
        return True
    except Exception as e:
        st.error(f"❌ Failed to initialize: {str(e)}")
        return False


async def process_query_async(query: str):
    """Process user query asynchronously."""
    return await st.session_state.orchestrator.process_query(query, verbose=False)


def process_query(query: str):
    """Wrapper to run async query in sync context."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        response = loop.run_until_complete(process_query_async(query))
        return response
    finally:
        loop.close()


# Sidebar
with st.sidebar:
    st.markdown("# 🤖 RAG-MCP Assistant")
    st.markdown("---")
    
    # Stats Section
    st.markdown("### 📊 Session Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(get_metric_card_html("Queries", str(st.session_state.query_count), "💬"), unsafe_allow_html=True)
    with col2:
        st.markdown(get_metric_card_html("Tools", str(len(set(st.session_state.tools_used))), "🔧"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # System Info
    st.markdown("### ⚙️ System Info")
    st.markdown("""
    <div class="glass-card">
        <p><strong>Model:</strong> llama-3.3-70b-versatile</p>
        <p><strong>Provider:</strong> Groq</p>
        <p><strong>Servers:</strong> 3 MCP</p>
        <p><strong>Tools:</strong> 9 Available</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    
    if st.button("🔄 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        if st.session_state.orchestrator:
            st.session_state.orchestrator.reset_conversation()
        st.rerun()
    
    st.markdown("---")
    
    # Sample Queries
    st.markdown("### 💡 Try These")
    sample_queries = [
        "What holidays are coming up?",
        "Who works in Engineering?",
        "What's the sick leave policy?",
        "Search for John",
        "Team events in 2025?"
    ]
    
    for query in sample_queries:
        if st.button(query, key=f"sample_{query}", use_container_width=True):
            st.session_state.pending_query = query


# Main Content Area
st.markdown("# 🎓 RAG-MCP Intelligent Assistant")
st.markdown("### Ask me anything about employees, policies, or announcements!")

# Initialize orchestrator if not done
if st.session_state.orchestrator is None:
    initialize_orchestrator()

# Tabs for different sections
tab1, tab2, tab3 = st.tabs(["💬 Chat", "🔍 System Details", "📈 Analytics"])

with tab1:
    # Chat Interface
    chat_container = st.container()
    
    # Display chat messages
    with chat_container:
        if not st.session_state.messages:
            st.markdown("""
            <div class="glass-card">
                <h3>👋 Welcome!</h3>
                <p>I can help you with:</p>
                <ul>
                    <li>🔍 <strong>Employee Information:</strong> Search by name, department, or ID</li>
                    <li>📢 <strong>Announcements:</strong> Holidays, events, policy updates</li>
                    <li>📚 <strong>Policy Questions:</strong> Leave, salary, HR policies</li>
                    <li>🔗 <strong>Complex Queries:</strong> Combine multiple data sources</li>
                </ul>
                <p>Try asking: <em>"What are the upcoming holidays?"</em></p>
            </div>
            """, unsafe_allow_html=True)
        
        for message in st.session_state.messages:
            is_user = message["role"] == "user"
            st.markdown(get_chat_message_html(message["content"], is_user), unsafe_allow_html=True)
            
            # Show tools used if assistant message
            if not is_user and "tools" in message:
                tools_html = "".join([get_tool_badge_html(tool) for tool in message["tools"]])
                st.markdown(f'<div style="margin-left: 52px; margin-top: -8px;">{tools_html}</div>', unsafe_allow_html=True)
    
    # Input area
    st.markdown("---")
    
    # Use a form to prevent auto-rerun
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([6, 1])
        
        with col1:
            user_input = st.text_input(
                "Your question:",
                key="user_input_form",
                placeholder="Ask me anything...",
                label_visibility="collapsed"
            )
        
        with col2:
            send_button = st.form_submit_button("Send 🚀", use_container_width=True)
    
    # Handle pending query from sidebar
    if "pending_query" in st.session_state:
        user_input = st.session_state.pending_query
        del st.session_state.pending_query
        send_button = True
    
    # Process input
    if send_button and user_input:
        # Check if we're already processing
        if "processing" not in st.session_state:
            st.session_state.processing = True
            
            # Add user message
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now().isoformat()
            })
            
            # Show thinking indicator
            with st.spinner("🤔 Thinking..."):
                try:
                    # Process query - but we need to track tools used
                    # Store the conversation history before processing
                    hist_before = len(st.session_state.orchestrator.conversation_history)
                    
                    response = process_query(user_input)
                    
                    # Extract tools used from conversation history
                    tools_in_this_query = []
                    hist_after = st.session_state.orchestrator.conversation_history
                    
                    # Find the assistant message with tool_calls
                    for msg in hist_after[hist_before:]:
                        if msg.get("role") == "assistant" and "tool_calls" in msg:
                            for tc in msg["tool_calls"]:
                                tool_name = tc["function"]["name"]
                                tools_in_this_query.append(tool_name)
                                # Add to global tools used list
                                st.session_state.tools_used.append(tool_name)
                    
                    # Update stats
                    st.session_state.query_count += 1
                    
                    # Add assistant message
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "timestamp": datetime.now().isoformat(),
                        "tools": tools_in_this_query
                    })
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            
            # Clear processing flag
            del st.session_state.processing
            
            # Rerun to update UI
            st.rerun()

with tab2:
    # System Details
    st.markdown("## 🏗️ System Architecture")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="glass-card">
            <h3>💾 Database Server</h3>
            <p><strong>Purpose:</strong> Employee records</p>
            <p><strong>Storage:</strong> SQLite</p>
            <p><strong>Tools:</strong> 4</p>
            <ul>
                <li>get_employee</li>
                <li>search_employees</li>
                <li>get_by_department</li>
                <li>get_all_employees</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="glass-card">
            <h3>📁 Filesystem Server</h3>
            <p><strong>Purpose:</strong> Announcements</p>
            <p><strong>Storage:</strong> Text files</p>
            <p><strong>Tools:</strong> 3</p>
            <ul>
                <li>list_announcements</li>
                <li>read_announcement</li>
                <li>search_announcements</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="glass-card">
            <h3>🧠 RAG Server</h3>
            <p><strong>Purpose:</strong> Policy docs</p>
            <p><strong>Storage:</strong> ChromaDB</p>
            <p><strong>Tools:</strong> 2</p>
            <ul>
                <li>query_policies</li>
                <li>get_policy_summary</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("## 🎼 Orchestration Flow")
    st.markdown("""
    <div class="glass-card">
        <pre>
User Query
    ↓
Groq LLM (llama-3.3-70b-versatile)
    ↓
Function Calling & Tool Selection
    ↓
┌──────────────┬─────────────────┬──────────────┐
│   Database   │   Filesystem    │     RAG      │
│  MCP Server  │   MCP Server    │  MCP Server  │
└──────────────┴─────────────────┴──────────────┘
    ↓
Results Aggregation
    ↓
Natural Language Response
        </pre>
    </div>
    """, unsafe_allow_html=True)

with tab3:
    # Analytics
    st.markdown("## 📈 Usage Analytics")
    
    if st.session_state.query_count > 0:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(get_metric_card_html("Total Queries", str(st.session_state.query_count), "💬"), unsafe_allow_html=True)
        
        with col2:
            st.markdown(get_metric_card_html("Unique Tools", str(len(set(st.session_state.tools_used))), "🔧"), unsafe_allow_html=True)
        
        with col3:
            st.markdown(get_metric_card_html("Messages", str(len(st.session_state.messages)), "📨"), unsafe_allow_html=True)
        
        with col4:
            avg_response = "< 2s"  # Placeholder
            st.markdown(get_metric_card_html("Avg Response", avg_response, "⚡"), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Query History
        st.markdown("### 📜 Query History")
        
        if st.session_state.messages:
            for i, msg in enumerate(reversed(st.session_state.messages)):
                if msg["role"] == "user":
                    with st.expander(f"Query {st.session_state.query_count - i//2}: {msg['content'][:50]}..."):
                        st.markdown(f"**Question:** {msg['content']}")
                        # Find corresponding response
                        if i > 0:
                            response = st.session_state.messages[-(i)]
                            if response["role"] == "assistant":
                                st.markdown(f"**Answer:** {response['content'][:200]}...")
    else:
        st.info("📊 Analytics will appear after you start chatting!")


# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #808080; font-size: 0.9rem;">
    Made with ❤️ using RAG + MCP • Powered by Groq (llama-3.3-70b-versatile)
</div>
""", unsafe_allow_html=True)