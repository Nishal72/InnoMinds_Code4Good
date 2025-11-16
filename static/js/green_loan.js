let uploadedImage = null;
let extractedText = '';

// Capture button click
document.getElementById('captureBtn').addEventListener('click', function() {
    document.getElementById('payslipInput').click();
});

// Handle image selection
document.getElementById('payslipInput').addEventListener('change', async function(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    uploadedImage = file;
    
    // Show upload spinner
    const uploadBtnText = document.getElementById('uploadBtnText');
    const uploadSpinner = document.getElementById('uploadSpinner');
    uploadBtnText.style.display = 'none';
    uploadSpinner.style.display = 'block';
    
    // Show preview image
    const reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById('previewImg').src = e.target.result;
        document.getElementById('resultsRow').style.display = 'flex';
    };
    reader.readAsDataURL(file);

    // Extract and analyze automatically
    document.getElementById('loadingIndicator').style.display = 'block';
    
    try {
        // Extract text from image
        await extractTextFromImage(file);
        
        // Wait a moment for extraction to complete
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Analyze the payslip
        await analyzePayslip();
    } catch (error) {
        console.error('Error processing payslip:', error);
        alert('Failed to process payslip. Please try again.');
    } finally {
        // Hide spinners
        uploadBtnText.style.display = 'inline';
        uploadSpinner.style.display = 'none';
        document.getElementById('loadingIndicator').style.display = 'none';
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
            return true;
        } else {
            console.error('OCR extraction failed:', data.error);
            return false;
        }
    } catch (error) {
        console.error('Error extracting text:', error);
        return false;
    }
}

async function analyzePayslip() {
    console.log('Analyzing payslip with text:', extractedText);
    
    if (!extractedText) {
        console.error('No extracted text available');
        alert('Please wait for text extraction to complete');
        return;
    }

    try {
        const formData = new FormData();
        formData.append('payslip_text', extractedText);
        formData.append('image', uploadedImage);

        console.log('Sending request to analyze-payslip API...');
        const response = await fetch('/green_loan/api/analyze-payslip/', {
            method: 'POST',
            body: formData
        });

        console.log('Response status:', response.status);
        const data = await response.json();
        console.log('Response data:', data);

        if (data.success) {
            console.log('Analysis successful, displaying results');
            displayAnalysis(data.analysis, data.extracted_data);
        } else {
            console.error('Analysis failed:', data.error);
            alert('Analysis failed: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error analyzing payslip:', error);
        alert('Failed to analyze payslip. Please try again. Error: ' + error.message);
    }
}

// Display analysis results
function displayAnalysis(analysis, extractedData) {
    console.log('displayAnalysis called with:', analysis, extractedData);
    
    const resultDiv = document.getElementById('analysisResult');
    
    // Show the results row
    document.getElementById('resultsRow').style.display = 'flex';
    
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

    // Show result and scroll to it
    resultDiv.style.display = 'block';
    resultDiv.classList.add('show');
    
    // Create visualizations if we have data
    if (extractedData.monthly_salary && analysis.max_loan_amount) {
        setTimeout(() => {
            createLoanCharts(extractedData, analysis);
        }, 500);
    }
    
    // Scroll to results
    setTimeout(() => {
        document.getElementById('resultsRow').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 300);
}

// Create loan visualization charts
function createLoanCharts(extractedData, analysis) {
    const salary = parseFloat(extractedData.monthly_salary) || 0;
    const maxLoan = parseFloat(analysis.max_loan_amount) || 0;
    const monthlyPayment = parseFloat(analysis.monthly_payment) || 0;
    const interestRate = parseFloat(analysis.interest_rate) || 5.5;
    const loanTermYears = parseFloat(analysis.loan_term_years) || 10;
    
    // Add chart containers after the analysis result
    const chartsHtml = `
        <div class="upload-section mt-4">
            <h4 style="color: var(--dark-green); margin-bottom: 1.5rem;">
                <i class="fas fa-chart-bar"></i> Financial Analytics
            </h4>
            <div class="row">
                <div class="col-md-6">
                    <div class="chart-container">
                        <div class="chart-title">Loan Affordability</div>
                        <canvas id="affordabilityChart"></canvas>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="chart-container">
                        <div class="chart-title">Monthly Budget Impact</div>
                        <canvas id="budgetChart"></canvas>
                    </div>
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-md-12">
                    <div class="chart-container">
                        <div class="chart-title">Loan Repayment Timeline (${loanTermYears} Years)</div>
                        <canvas id="repaymentChart"></canvas>
                    </div>
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-md-6">
                    <div class="chart-container">
                        <div class="chart-title">Green Project Options</div>
                        <canvas id="projectsChart"></canvas>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="chart-container">
                        <div class="chart-title">Environmental Impact (10 Years)</div>
                        <canvas id="impactChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Insert charts after the analysisResult div
    const resultsRow = document.getElementById('resultsRow');
    resultsRow.insertAdjacentHTML('afterend', chartsHtml);
    
    // Calculate values
    const disposableIncome = salary - monthlyPayment;
    const totalRepayment = monthlyPayment * loanTermYears * 12;
    const totalInterest = totalRepayment - maxLoan;
    
    // 1. Affordability Chart (Doughnut)
    new Chart(document.getElementById('affordabilityChart'), {
        type: 'doughnut',
        data: {
            labels: ['Available for Loan', 'Already Used', 'Reserve Buffer'],
            datasets: [{
                data: [maxLoan, salary * 2, salary * 1],
                backgroundColor: ['#10b981', '#f5576c', '#ffd700']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.label + ': MUR ' + context.parsed.toLocaleString();
                        }
                    }
                }
            }
        }
    });
    
    // 2. Budget Impact Chart (Bar)
    new Chart(document.getElementById('budgetChart'), {
        type: 'bar',
        data: {
            labels: ['Monthly Salary', 'After Loan Payment', 'Recommended Minimum'],
            datasets: [{
                label: 'MUR',
                data: [salary, disposableIncome, salary * 0.6],
                backgroundColor: ['#10b981', '#14b8a6', '#ffd700']
            }]
        },
        options: {
            responsive: true,
            plugins: { 
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'MUR ' + context.parsed.y.toLocaleString();
                        }
                    }
                }
            },
            scales: { 
                y: { 
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return 'MUR ' + value.toLocaleString();
                        }
                    }
                } 
            }
        }
    });
    
    // 3. Repayment Timeline (Line)
    const years = [];
    const principalData = [];
    const interestData = [];
    let remainingPrincipal = maxLoan;
    const monthlyRate = interestRate / 100 / 12;
    
    for (let year = 0; year <= loanTermYears; year++) {
        years.push('Year ' + year);
        principalData.push(remainingPrincipal);
        
        // Calculate interest paid this year
        let yearlyInterest = 0;
        for (let month = 0; month < 12 && remainingPrincipal > 0; month++) {
            const interestPayment = remainingPrincipal * monthlyRate;
            const principalPayment = monthlyPayment - interestPayment;
            yearlyInterest += interestPayment;
            remainingPrincipal -= principalPayment;
        }
        interestData.push(yearlyInterest);
    }
    
    new Chart(document.getElementById('repaymentChart'), {
        type: 'line',
        data: {
            labels: years,
            datasets: [
                {
                    label: 'Remaining Principal (MUR)',
                    data: principalData,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true,
                    yAxisID: 'y'
                },
                {
                    label: 'Annual Interest Paid (MUR)',
                    data: interestData,
                    borderColor: '#f5576c',
                    backgroundColor: 'rgba(245, 87, 108, 0.1)',
                    fill: true,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { position: 'bottom' },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': MUR ' + context.parsed.y.toLocaleString();
                        }
                    }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    position: 'left',
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return 'MUR ' + value.toLocaleString();
                        }
                    }
                },
                y1: {
                    type: 'linear',
                    position: 'right',
                    beginAtZero: true,
                    grid: { drawOnChartArea: false },
                    ticks: {
                        callback: function(value) {
                            return 'MUR ' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
    
    // 4. Green Project Options (Bar - Horizontal)
    new Chart(document.getElementById('projectsChart'), {
        type: 'bar',
        data: {
            labels: ['Solar Panels (5kW)', 'Energy Efficient AC', 'Solar Water Heater', 'LED Lighting', 'Insulation'],
            datasets: [{
                label: 'Estimated Cost (MUR)',
                data: [400000, 80000, 60000, 30000, 50000],
                backgroundColor: [
                    maxLoan >= 400000 ? '#10b981' : '#94a3b8',
                    maxLoan >= 80000 ? '#10b981' : '#94a3b8',
                    maxLoan >= 60000 ? '#10b981' : '#94a3b8',
                    maxLoan >= 30000 ? '#10b981' : '#94a3b8',
                    maxLoan >= 50000 ? '#10b981' : '#94a3b8'
                ]
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'MUR ' + context.parsed.x.toLocaleString();
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return 'MUR ' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
    
    // 5. Environmental Impact (Doughnut)
    const solarCapacity = Math.min(maxLoan / 80000, 5); // Assuming MUR 80k per kW
    const co2Reduction = solarCapacity * 0.7; // tons per year per kW
    const treesEquivalent = co2Reduction * 16; // 1 ton CO2 = ~16 trees
    const plasticBottles = co2Reduction * 3000; // bottles saved
    
    new Chart(document.getElementById('impactChart'), {
        type: 'bar',
        data: {
            labels: ['CO2 Reduction\n(tons)', 'Trees\nEquivalent', 'Plastic Bottles\nSaved (000s)'],
            datasets: [{
                label: 'Environmental Savings',
                data: [co2Reduction * 10, treesEquivalent, plasticBottles / 1000],
                backgroundColor: ['#10b981', '#38ef7d', '#14b8a6']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.parsed.y.toFixed(1);
                        }
                    }
                }
            },
            scales: { y: { beginAtZero: true } }
        }
    });
}