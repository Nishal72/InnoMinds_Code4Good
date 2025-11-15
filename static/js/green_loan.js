let uploadedImage = null;
let extractedText = '';

// Capture button click
document.getElementById('captureBtn').addEventListener('click', function() {
    document.getElementById('payslipInput').click();
});

// Handle image selection
document.getElementById('payslipInput').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        uploadedImage = file;
        
        // Show preview
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('previewImg').src = e.target.result;
            document.getElementById('imagePreview').style.display = 'block';
            document.getElementById('analyzeBtn').style.display = 'block';
        };
        reader.readAsDataURL(file);

        // Extract text immediately
        extractTextFromImage(file);
    }
});

// Extract text from image
async function extractTextFromImage(file) {
    const formData = new FormData();
    formData.append('image', file);

    try {
        const response = await fetch('/green_loan/api/extract-payslip/', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        
        if (data.success) {
            extractedText = data.extracted_text;
            console.log('Extracted text:', extractedText);
        } else {
            console.error('OCR extraction failed:', data.error);
        }
    } catch (error) {
        console.error('Error extracting text:', error);
    }
}

// Analyze button click
document.getElementById('analyzeBtn').addEventListener('click', async function() {
    // Show loading immediately
    document.getElementById('loadingIndicator').style.display = 'block';
    this.disabled = true;
    
    // If extraction is still in progress, wait for it
    if (!extractedText) {
        let attempts = 0;
        const maxAttempts = 10; // Wait up to 5 seconds
        
        const checkInterval = setInterval(async () => {
            attempts++;
            
            if (extractedText) {
                clearInterval(checkInterval);
                await analyzePayslip.call(this);
            } else if (attempts >= maxAttempts) {
                clearInterval(checkInterval);
                document.getElementById('loadingIndicator').style.display = 'none';
                this.disabled = false;
                // Still extracting - continue waiting silently
                this.textContent = 'Still extracting... Please wait';
                setTimeout(() => {
                    this.innerHTML = '<i class="fas fa-chart-line"></i> Analyze Payslip';
                    this.disabled = false;
                }, 2000);
            }
        }, 500);
        return;
    }

    await analyzePayslip.call(this);
});

async function analyzePayslip() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    // Show loading
    document.getElementById('loadingIndicator').style.display = 'block';
    analyzeBtn.disabled = true;

    try {
        const formData = new FormData();
        formData.append('payslip_text', extractedText);
        formData.append('image', uploadedImage);

        const response = await fetch('/green_loan/api/analyze-payslip/', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            displayAnalysis(data.analysis, data.extracted_data);
        } else {
            alert('Analysis failed: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error analyzing payslip:', error);
        alert('Failed to analyze payslip. Please try again.');
    } finally {
        document.getElementById('loadingIndicator').style.display = 'none';
        analyzeBtn.disabled = false;
    }
}

// Display analysis results
function displayAnalysis(analysis, extractedData) {
    const resultDiv = document.getElementById('analysisResult');
    
    // Loan status
    const statusHtml = `
        <div class="loan-status ${analysis.loan_available ? 'approved' : 'pending'}">
            <i class="fas fa-${analysis.loan_available ? 'check-circle' : 'clock'}"></i>
            ${analysis.loan_available ? 'Loan Approved!' : 'Under Review'}
        </div>
    `;
    document.getElementById('loanStatus').innerHTML = statusHtml;

    // Metrics
    let metricsHtml = '';
    
    if (extractedData.monthly_salary) {
        metricsHtml += `
            <div class="col-md-6">
                <div class="metric-card">
                    <h6>Monthly Salary</h6>
                    <div class="value">MUR ${parseFloat(extractedData.monthly_salary).toLocaleString()}</div>
                </div>
            </div>
        `;
    }

    if (analysis.max_loan_amount) {
        metricsHtml += `
            <div class="col-md-6">
                <div class="metric-card">
                    <h6>Max Loan Amount</h6>
                    <div class="value">MUR ${parseFloat(analysis.max_loan_amount).toLocaleString()}</div>
                </div>
            </div>
        `;
    }

    if (analysis.interest_rate) {
        metricsHtml += `
            <div class="col-md-6">
                <div class="metric-card">
                    <h6>Interest Rate</h6>
                    <div class="value">${analysis.interest_rate}% p.a.</div>
                </div>
            </div>
        `;
    }

    if (analysis.monthly_payment) {
        metricsHtml += `
            <div class="col-md-6">
                <div class="metric-card">
                    <h6>Monthly Payment</h6>
                    <div class="value">MUR ${parseFloat(analysis.monthly_payment).toLocaleString()}</div>
                </div>
            </div>
        `;
    }

    if (analysis.loan_term_years) {
        metricsHtml += `
            <div class="col-md-6">
                <div class="metric-card">
                    <h6>Loan Term</h6>
                    <div class="value">${analysis.loan_term_years} years</div>
                </div>
            </div>
        `;
    }

    document.getElementById('metricsSection').innerHTML = metricsHtml;

    // Banks
    if (analysis.recommended_banks && analysis.recommended_banks.length > 0) {
        let banksHtml = '';
        analysis.recommended_banks.forEach(bank => {
            banksHtml += `
                <div class="bank-card">
                    <div class="bank-name">
                        <i class="fas fa-university"></i> ${bank.name}
                    </div>
                    <div class="bank-rate">${bank.rate}</div>
                    <p style="color: #6b7280; margin: 0.5rem 0;">
                        <i class="fas fa-calendar-alt"></i> ${bank.terms}
                    </p>
                    <p style="color: var(--primary-green); margin: 0;">
                        <i class="fas fa-star"></i> ${bank.special}
                    </p>
                </div>
            `;
        });
        document.getElementById('banksList').innerHTML = banksHtml;
        document.getElementById('banksSection').style.display = 'block';
    } else {
        document.getElementById('banksSection').style.display = 'none';
    }

    // Documentation
    if (analysis.documentation && analysis.documentation.length > 0) {
        let docsHtml = '';
        analysis.documentation.forEach(doc => {
            docsHtml += `<li>${doc}</li>`;
        });
        document.getElementById('docsList').innerHTML = docsHtml;
        document.getElementById('documentationSection').style.display = 'block';
    } else {
        document.getElementById('documentationSection').style.display = 'none';
    }

    // Tips
    if (analysis.approval_tips && analysis.approval_tips.length > 0) {
        let tipsHtml = '';
        analysis.approval_tips.forEach(tip => {
            tipsHtml += `<li>${tip}</li>`;
        });
        document.getElementById('tipsList').innerHTML = tipsHtml;
        document.getElementById('tipsSection').style.display = 'block';
    } else {
        document.getElementById('tipsSection').style.display = 'none';
    }

    // Eco Impact
    if (analysis.eco_impact) {
        document.getElementById('ecoImpactText').textContent = analysis.eco_impact;
        document.getElementById('ecoImpactSection').style.display = 'block';
    } else {
        document.getElementById('ecoImpactSection').style.display = 'none';
    }

    // Detailed Analysis
    if (analysis.detailed_analysis) {
        document.getElementById('detailedAnalysisText').textContent = analysis.detailed_analysis;
        document.getElementById('detailedAnalysisSection').style.display = 'block';
    } else {
        document.getElementById('detailedAnalysisSection').style.display = 'none';
    }

    // Show result
    resultDiv.classList.add('show');
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}