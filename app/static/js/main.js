document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('tax-form');
    const resultDiv = document.getElementById('result');
    const countrySelect = document.getElementById('country');
    const stateContainer = document.getElementById('state-container');
    const stateSelect = document.getElementById('state');
    const cityContainer = document.getElementById('city-container');
    const citySelect = document.getElementById('city');
    const taxYearSelect = document.getElementById('tax-year');
    const singaporeFields = document.getElementById('singapore-fields');
    const usFields = document.getElementById('us-fields');

    function formatCurrency(amount) {
        return '$' + amount.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
    }

    function populateDropdown(selectElement, options) {
        selectElement.innerHTML = '<option value="">Select</option>';
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option;
            optionElement.textContent = option;
            selectElement.appendChild(optionElement);
        });
    }

    fetch('/api/get_options')
        .then(response => response.json())
        .then(data => {
            populateDropdown(countrySelect, data.countries);
            populateDropdown(taxYearSelect, data.taxYears);

            countrySelect.addEventListener('change', () => {
                const selectedCountry = countrySelect.value;
                if (selectedCountry) {
                    updateStates(selectedCountry);
                    toggleCountrySpecificFields(selectedCountry);
                } else {
                    stateContainer.style.display = 'none';
                    cityContainer.style.display = 'none';
                    singaporeFields.style.display = 'none';
                    usFields.style.display = 'none';
                }
            });

            stateSelect.addEventListener('change', () => {
                const selectedCountry = countrySelect.value;
                const selectedState = stateSelect.value;
                if (selectedCountry && selectedState) {
                    updateCities(selectedCountry, selectedState);
                } else {
                    cityContainer.style.display = 'none';
                }
            });
        });

    function toggleCountrySpecificFields(country) {
        if (country === 'Singapore') {
            singaporeFields.style.display = 'block';
            usFields.style.display = 'none';
        } else if (country === 'United States') {
            singaporeFields.style.display = 'none';
            usFields.style.display = 'block';
        } else {
            singaporeFields.style.display = 'none';
            usFields.style.display = 'none';
        }
    }

    function updateStates(country) {
        fetch(`/api/get_states/${country}`)
            .then(response => response.json())
            .then(data => {
                populateDropdown(stateSelect, data.states);
                stateContainer.style.display = 'block';
                
                if (data.states.length === 1) {
                    stateSelect.value = data.states[0];
                    stateSelect.disabled = true;
                    updateCities(country, data.states[0]);
                } else {
                    stateSelect.disabled = false;
                    cityContainer.style.display = 'none';
                }
            });
    }

    function updateCities(country, state) {
        fetch(`/api/get_cities/${country}/${state}`)
            .then(response => response.json())
            .then(data => {
                populateDropdown(citySelect, data.cities);
                cityContainer.style.display = 'block';
                
                if (data.cities.length === 1) {
                    citySelect.value = data.cities[0];
                    citySelect.disabled = true;
                } else {
                    citySelect.disabled = false;
                }
            });
    }

    let breakdownChart = null;
    let additionalCompensationChart = null;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        // Convert residency status to boolean
        data.is_resident = data['residency-status'] === 'resident';
        delete data['residency-status'];

        try {
            const response = await fetch('/api/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            if (response.ok) {
                const result = await response.json();
                displayResults(result);
                createCharts(result);  // Make sure this line is here
            } else {
                resultDiv.innerHTML = '<p>Error calculating tax</p>';
            }
        } catch (error) {
            console.error('Error:', error);
            resultDiv.innerHTML = '<p>An error occurred</p>';
        }
    });

    function displayResults(result) {
        let resultHTML = `
            <h2>Results</h2>
            <table class="result-table">
                <tr>
                    <th>Category</th>
                    <th>Amount</th>
                </tr>
                <tr>
                    <td>Residency Status</td>
                    <td>${result.is_resident ? 'Resident' : 'Non-Resident'}</td>
                </tr>
                <tr>
                    <td>Annual Gross Income</td>
                    <td>${formatCurrency(result.gross_income)}</td>
                </tr>
        `;

        if ('income_tax' in result) {
            // Singapore-specific fields
            resultHTML += `
                <tr>
                    <td>Annual Income Tax</td>
                    <td>${formatCurrency(result.income_tax)}</td>
                </tr>
                <tr>
                    <td>Total Annual Employee CPF Contribution</td>
                    <td>${formatCurrency(result.employee_cpf_contribution)}</td>
                </tr>
                <tr>
                    <td>Annual Take-Home Income</td>
                    <td>${formatCurrency(result.net_income)}</td>
                </tr>
                <tr>
                    <td>Total Annual Employer CPF Contribution</td>
                    <td>${formatCurrency(result.employer_cpf_contribution)}</td>
                </tr>
                <tr>
                    <td>Total Annual Compensation</td>
                    <td>${formatCurrency(result.total_compensation)}</td>
                </tr>
            `;
        } else if ('federal_tax' in result) {
            // US-specific fields
            resultHTML += `
                <tr>
                    <td>Federal Tax</td>
                    <td>${formatCurrency(result.federal_tax)}</td>
                </tr>
                <tr>
                    <td>State Tax</td>
                    <td>${formatCurrency(result.state_tax)}</td>
                </tr>
                <tr>
                    <td>Local Tax</td>
                    <td>${formatCurrency(result.local_tax)}</td>
                </tr>
                <tr>
                    <td>Social Security Tax</td>
                    <td>${formatCurrency(result.social_security_tax)}</td>
                </tr>
                <tr>
                    <td>Medicare Tax</td>
                    <td>${formatCurrency(result.medicare_tax)}</td>
                </tr>
                <tr>
                    <td>Total Tax</td>
                    <td>${formatCurrency(result.total_tax)}</td>
                </tr>
                <tr>
                    <td>401(k) Contribution</td>
                    <td>${formatCurrency(result.employee_401k_contribution)}</td>
                </tr>
                <tr>
                    <td>Employer 401(k) Contribution</td>
                    <td>${formatCurrency(result.employer_401k_contribution)}</td>
                </tr>
                <tr>
                    <td>Annual Take-Home Income</td>
                    <td>${formatCurrency(result.net_income)}</td>
                </tr>
                <tr>
                    <td>Total Annual Compensation</td>
                    <td>${formatCurrency(result.total_compensation)}</td>
                </tr>
            `;
        }

        resultHTML += `
            </table>
        `;

        resultDiv.innerHTML = resultHTML;
    }

    function createCharts(result) {
        const chartsContainer = document.getElementById('charts-container');
        chartsContainer.style.display = 'block';

        createBreakdownChart(result);
        createAdditionalCompensationChart(result);
    }

    function createBreakdownChart(result) {
        const ctx = document.getElementById('breakdown-chart').getContext('2d');
        
        if (breakdownChart) {
            breakdownChart.destroy();
        }

        let labels, data;

        if ('income_tax' in result) {
            // Singapore breakdown
            labels = ['Net Income', 'Income Tax', 'Employee CPF'];
            data = [
                result.net_income,
                result.income_tax,
                result.employee_cpf_contribution
            ];
        } else {
            // US breakdown
            labels = ['Net Income', 'Federal Tax', 'State Tax', 'Local Tax', 'Social Security Tax', 'Medicare Tax', '401(k) Contribution'];
            data = [
                result.net_income,
                result.federal_tax,
                result.state_tax,
                result.local_tax,
                result.social_security_tax,
                result.medicare_tax,
                result.employee_401k_contribution
            ];
        }

        breakdownChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(153, 102, 255, 0.8)',
                        'rgba(255, 159, 64, 0.8)',
                        'rgba(199, 199, 199, 0.8)'
                    ],
                    hoverOffset: 30
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: 'Income Breakdown'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(2);
                                return `${label}: ${percentage}% (${formatCurrency(value)})`;
                            }
                        }
                    }
                }
            }
        });
    }

    function createAdditionalCompensationChart(result) {
        const ctx = document.getElementById('additional-compensation-chart').getContext('2d');
        
        if (additionalCompensationChart) {
            additionalCompensationChart.destroy();
        }

        let labels, data;

        if ('employer_cpf_contribution' in result) {
            // Singapore
            labels = ['Employer CPF Contribution'];
            data = [(result.employer_cpf_contribution / result.gross_income) * 100];
        } else {
            // US
            labels = ['Employer 401(k) Contribution'];
            data = [(result.employer_401k_contribution / result.gross_income) * 100];
        }

        additionalCompensationChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: '% of Annual Income',
                    data: data,
                    backgroundColor: 'rgba(153, 102, 255, 0.8)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Additional Compensation'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.parsed.y || 0;
                                const absoluteValue = (value / 100) * result.gross_income;
                                return `${value.toFixed(2)}% of Annual Income (${formatCurrency(absoluteValue)})`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Percentage of Annual Income'
                        },
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }
});