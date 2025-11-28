# LeetCode GitHub Agent

A production-ready application that automatically generates comprehensive notes for your LeetCode solutions and pushes them to GitHub.

## 🌟 Features

- **AI-Powered Analysis**: Uses Google Gemini to analyze your solutions
- **Comprehensive Notes**: Generates detailed explanations, complexity analysis, hints, and more
- **GitHub Integration**: Automatically pushes solutions to your GitHub repository
- **Professional UI**: Beautiful Streamlit frontend with modern design
- **Production Ready**: Built with best practices for deployment

## 📋 What Gets Generated?

For each solution, the tool creates:

1. **Solution Code File** - Your code with proper formatting
2. **Detailed Notes** including:
   - Problem description with examples
   - Detailed explanation
   - Key insights
   - Helpful hints
   - Algorithm and approach
   - Visual step-by-step walkthrough
   - Time & space complexity analysis
   - Edge cases
   - Common mistakes to avoid
   - Optimization tips

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google API Key (for Gemini)
- GitHub Personal Access Token

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd Leetcode_agent
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### Running the Application

1. **Start the Backend (FastAPI)**
```bash
uvicorn app:app --reload --port 8000
```

2. **Start the Frontend (Streamlit)** (in a new terminal)
```bash
streamlit run frontend.py
```

3. **Access the Application**
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 🔐 GitHub Setup

1. Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select `repo` scope
4. Copy the token
5. Configure in the Streamlit sidebar

## 📁 Project Structure

```
Leetcode_agent/
├── app.py              # FastAPI backend
├── frontend.py         # Streamlit frontend
├── llm.py             # LLM configuration and prompts
├── models.py          # Pydantic models
├── utils.py           # Utility functions
├── requirements.txt   # Python dependencies
├── .env.example       # Environment variables template
└── README.md          # This file
```

## 🎯 Usage

1. **Configure GitHub** (one-time setup)
   - Enter your GitHub credentials in the sidebar
   - Save configuration

2. **Submit a Solution**
   - Paste the LeetCode problem statement
   - Paste your solution code
   - Select programming language
   - Click "Generate & Push to GitHub"

3. **Wait for Processing**
   - AI analyzes your solution (~30-60 seconds)
   - Generates comprehensive notes
   - Pushes to GitHub automatically

4. **Check Your Repository**
   - Solutions are organized by problem number
   - Each folder contains code and notes

## 🌐 Deployment

### Deploy Backend (FastAPI)

**Heroku:**
```bash
heroku create your-app-name
heroku config:set GOOGLE_API_KEY=your_key
git push heroku main
```

**Railway/Render:**
- Connect your GitHub repository
- Set environment variables in dashboard
- Deploy automatically

### Deploy Frontend (Streamlit)

**Streamlit Cloud:**
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Set secrets in dashboard
5. Deploy

**Docker:**
```bash
docker build -t leetcode-agent .
docker run -p 8501:8501 -p 8000:8000 leetcode-agent
```

## 🔧 Configuration

### Environment Variables

- `GOOGLE_API_KEY` - Your Google API key (required)
- `API_BASE_URL` - Backend API URL (default: http://localhost:8000)

### Supported Languages

- Python
- JavaScript
- TypeScript
- Java
- C++
- C
- C#
- Go
- Rust
- SQL
- Swift

## 📊 Features Breakdown

### Backend (FastAPI)
- RESTful API endpoints
- GitHub API integration
- LLM-powered analysis
- Error handling and validation
- CORS support

### Frontend (Streamlit)
- Modern, responsive UI
- Real-time status updates
- Progress indicators
- Session management
- Error handling
- Statistics tracking

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Google Gemini for AI capabilities
- Streamlit for the amazing frontend framework
- FastAPI for the robust backend framework
- LangChain for LLM integration

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

**Made with ❤️ for LeetCode enthusiasts**
