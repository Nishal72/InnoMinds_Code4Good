# Green Audit Setup Guide

This guide will help you set up the Green Audit feature for your Django application.

## Features Implemented

✅ **Backend (Django)**
- Model to store audit data, images, and analysis results
- OpenAI GPT-3.5-turbo integration for sustainability analysis
- OCR text extraction from images using Tesseract
- RESTful API endpoints for analyze and extract-text operations
- User-specific audit history tracking

✅ **Frontend (HTML/CSS/JavaScript)**
- Modern gradient UI matching the Flutter design
- Information cards about green audit
- Text input area for audit details
- Image capture/upload functionality
- Real-time text extraction from images
- Loading states and error handling
- Responsive design

## Installation Steps

### 1. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

### 2. Install Tesseract OCR (Required for image text extraction)

**Windows:**
1. Download Tesseract installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install Tesseract (default location: `C:\Program Files\Tesseract-OCR\`)
3. Add Tesseract to your system PATH, or add this to your Django settings:

```python
# In settings.py
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### 3. Configure OpenAI API Key

1. Get your API key from: https://platform.openai.com/api-keys
2. Create a `.env` file in the project root:

```bash
cp .env.example .env
```

3. Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 4. Run Database Migrations

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Media Directory

The media directory will be created automatically, but you can create it manually:

```powershell
mkdir media
mkdir media\audit_images
mkdir media\temp
```

### 6. Run the Development Server

```powershell
python manage.py runserver
```

### 7. Access the Green Audit Page

Navigate to: http://127.0.0.1:8000/green_audit/green_audit/

## Usage

### Analyzing Text Audit Data

1. Enter sustainability audit details in the text area
2. Click "🔍 Analyze Audit" button
3. Wait for AI analysis (may take 5-15 seconds)
4. View the comprehensive sustainability analysis results

### Using Image OCR

1. Click "📷 Capture Image" button
2. Select an image from your device or capture using camera
3. The system will automatically extract text from the image
4. The extracted text will appear in the text area
5. Click "🔍 Analyze Audit" to analyze the extracted text

## API Endpoints

### POST `/green_audit/api/analyze/`
Analyzes audit text using OpenAI.

**Request Body:**
```json
{
  "audit_text": "Your sustainability audit details here..."
}
```

**Response:**
```json
{
  "success": true,
  "result": "AI-generated analysis..."
}
```

### POST `/green_audit/api/extract-text/`
Extracts text from uploaded image using OCR.

**Request:** FormData with 'image' file

**Response:**
```json
{
  "success": true,
  "extracted_text": "Extracted text from image..."
}
```

## Database Models

### GreenAudit Model
- `user`: ForeignKey to User (optional)
- `audit_text`: TextField for audit details
- `image`: ImageField for uploaded audit images
- `analysis_result`: TextField for AI analysis results
- `created_at`: DateTime (auto)
- `updated_at`: DateTime (auto)

## Admin Panel

Access the admin panel to view all audits:
1. Create superuser: `python manage.py createsuperuser`
2. Navigate to: http://127.0.0.1:8000/admin/
3. View/manage audits under "Green audit" section

## Troubleshooting

### Import Errors
- Make sure all packages are installed: `pip install -r requirements.txt`
- Verify virtual environment is activated

### Tesseract Not Found
- Install Tesseract OCR for your OS
- Add to PATH or configure in settings.py

### OpenAI API Errors
- Verify API key is correct in `.env` file
- Check API quota/billing at OpenAI dashboard
- Ensure `.env` file is in project root

### Image Upload Issues
- Ensure MEDIA_ROOT and MEDIA_URL are configured
- Check folder permissions for media directory
- Verify Pillow is installed: `pip install Pillow`

## Technologies Used

- **Django 5.2.8**: Web framework
- **OpenAI API**: GPT-3.5-turbo for analysis
- **Tesseract OCR**: Text extraction from images
- **Pillow**: Image processing
- **python-dotenv**: Environment variable management

## Notes

- The analysis uses OpenAI's GPT-3.5-turbo model (cost-effective)
- Audit text is truncated to 2000 characters for API efficiency
- Images are temporarily stored during OCR processing
- User authentication is optional but recommended for tracking
- All API calls include error handling and user feedback

## Next Steps

1. Customize the AI prompt for specific industry needs
2. Add export functionality (PDF reports)
3. Implement audit comparison features
4. Add data visualization for metrics
5. Create scheduled audit reminders
6. Add multi-language support

## Support

For issues or questions, check:
- Django documentation: https://docs.djangoproject.com/
- OpenAI API docs: https://platform.openai.com/docs
- Tesseract OCR: https://github.com/tesseract-ocr/tesseract
