# 🌱 Green Audit - Quick Start Guide

## ✅ What's Been Implemented

### Backend (Django)
- ✅ `GreenAudit` model with user tracking, image storage, and analysis results
- ✅ OpenAI GPT-3.5-turbo integration for sustainability analysis
- ✅ OCR text extraction using Tesseract (pytesseract)
- ✅ Two API endpoints: `/api/analyze/` and `/api/extract-text/`
- ✅ Admin panel integration
- ✅ Database migrations completed

### Frontend (HTML/CSS/JavaScript)
- ✅ Beautiful gradient UI matching Flutter design
- ✅ Information cards about green audit
- ✅ Text input area with focus effects
- ✅ Image upload/capture functionality
- ✅ Real-time OCR text extraction
- ✅ Loading spinners and error handling
- ✅ Results display with animation
- ✅ Fully responsive design

## 🚀 Setup Steps

### 1. Configure OpenAI API Key

Edit the `.env` file in your project root:

```bash
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

**Get your API key:** https://platform.openai.com/api-keys

### 2. Install Tesseract OCR (for image text extraction)

**Windows:**
1. Download: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to default location: `C:\Program Files\Tesseract-OCR\`
3. Add to system PATH

**Or configure in settings.py:**
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### 3. Restart Development Server

The server should automatically reload, or manually restart:

```powershell
python manage.py runserver
```

### 4. Access the Page

Navigate to: **http://127.0.0.1:8000/green_audit/green_audit/**

## 📝 How to Use

### Analyze Text Audit
1. Enter sustainability audit details in the text area
2. Click "🔍 Analyze Audit"
3. Wait for AI analysis (5-15 seconds)
4. View comprehensive results

### Extract Text from Image
1. Click "📷 Capture Image"
2. Select/capture an image
3. Text automatically extracted
4. Click "🔍 Analyze Audit" to analyze

## 🔧 Features

- **AI-Powered Analysis**: Uses GPT-3.5-turbo for sustainability insights
- **OCR Text Extraction**: Extract text from images automatically
- **User Tracking**: Saves audit history (if logged in)
- **Beautiful UI**: Modern gradient design with animations
- **Error Handling**: Comprehensive error messages
- **Responsive**: Works on all screen sizes

## 📡 API Endpoints

### Analyze Audit
```
POST /green_audit/api/analyze/
Body: {"audit_text": "Your audit details..."}
Response: {"success": true, "result": "AI analysis..."}
```

### Extract Text from Image
```
POST /green_audit/api/extract-text/
Body: FormData with 'image' file
Response: {"success": true, "extracted_text": "..."}
```

## 🐛 Troubleshooting

### If Tesseract is not found:
- Install Tesseract OCR
- Add to PATH or configure in settings.py

### If OpenAI API fails:
- Check `.env` file has correct API key
- Verify API quota at OpenAI dashboard
- Ensure `.env` is in project root

### If imports fail:
- Packages are already installed
- Restart development server
- Check virtual environment is activated

## 📦 Installed Packages

All required packages are already installed:
- ✅ openai
- ✅ python-dotenv
- ✅ Pillow
- ✅ pytesseract
- ✅ Django 5.2.8

## 🎯 Next Steps

1. **Add your OpenAI API key** to `.env` file
2. **Install Tesseract OCR** (optional, for image text extraction)
3. **Test the page** - visit the URL above
4. **Create a superuser** to view audits in admin:
   ```powershell
   python manage.py createsuperuser
   ```

## 📚 Files Modified/Created

- ✅ `green_audit/models.py` - GreenAudit model
- ✅ `green_audit/views.py` - Views with OpenAI & OCR
- ✅ `green_audit/urls.py` - API endpoints
- ✅ `green_audit/admin.py` - Admin configuration
- ✅ `templates/green_audit/green_audit.html` - Frontend
- ✅ `MoLenerzi/settings.py` - Media files config
- ✅ `MoLenerzi/urls.py` - Media URL routing
- ✅ `requirements.txt` - Updated dependencies
- ✅ `.env` - Environment variables
- ✅ Database migrations - Completed

## 💡 Tips

- Press **Ctrl+Enter** in text area to analyze quickly
- Images are temporarily stored during OCR processing
- Audit text is truncated to 2000 characters for API efficiency
- Login to track your audit history
- All API calls have proper error handling

---

**Status:** ✅ **Ready to Use!**

Just add your OpenAI API key and start analyzing! 🎉
