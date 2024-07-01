document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('tax-form');
    const resultDiv = document.getElementById('result');
    const countrySelect = document.getElementById('country');
    const stateContainer = document.getElementById('state-container');
    const stateSelect = document.getElementById('state');
    const cityContainer = document.getElementById('city-container');
    const citySelect = document.getElementById('city');
    const taxYearSelect = document.getElementById('tax-year');
    const residencyStatusSelect = document.getElementById('residency-status');
    const singaporeFields = document.getElementById('singapore-fields');
    const usFields = document.getElementById('us-fields');
    const chinaFields = document.getElementById('china-fields');

    function formatCurrency(amount) {
        return amount && typeof amount === 'number' 
            ? '$' + amount.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')
            : '$0.00';
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
                    toggleCountrySpecificFields(selectedCountry, residencyStatusSelect.value === 'resident');
                } else {
                    stateContainer.style.display = 'none';
                    cityContainer.style.display = 'none';
                    toggleCountrySpecificFields('');
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

            residencyStatusSelect.addEventListener('change', () => {
                const selectedCountry = countrySelect.value;
                if (selectedCountry) {
                    toggleCountrySpecificFields(selectedCountry, residencyStatusSelect.value === 'resident');
                }
            });
        });

    function toggleCountrySpecificFields(country, isResident) {
        if (country === 'Singapore') {
            singaporeFields.style.display = 'block';
            usFields.style.display = 'none';
            chinaFields.style.display = 'none';
        } else if (country === 'United States') {
            singaporeFields.style.display = 'none';
            usFields.style.display = isResident ? 'block' : 'none';
            chinaFields.style.display = 'none';
        } else if (country === 'China') {
            singaporeFields.style.display = 'none';
            usFields.style.display = 'none';
            chinaFields.style.display = 'block';
        } else {
            singaporeFields.style.display = 'none';
            usFields.style.display = 'none';
            chinaFields.style.display = 'none';
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
                createCharts(result);
            } else {
                resultDiv.innerHTML = '<p>Error calculating tax</p>';
            }
        } catch (error) {
            console.error('Error:', error);
            resultDiv.innerHTML = '<p>An error occurred</p>';
        }
    });

    function displayResults(result) {
        let resultHTML = `<h2>Results</h2>
                          <table class="result-table">
                            <tr>
                              <th>Category</th>
                              <th>Amount</th>
                            </tr>`;


            // Define ordered keys for each country
            const orderedKeysUS = [
                'gross_income',
                'federal_tax',
                'state_tax',
                'local_tax',
                'medicare_tax',
                'social_security_tax',
                'employee_401k_contribution',
                'net_income',
                'total_compensation',
                'employer_401k_contribution'
            ];

            const orderedKeysSG = [
                'gross_income',
                'income_tax',
                'employee_cpf_contribution',
                'employer_cpf_contribution',
                'net_income',
                'total_compensation'
            ];

            const orderedKeysCN = [
                'gross_income',
                'income_tax',
                'employee_social_insurance',
                'employer_social_insurance',
                'net_income',
                'total_compensation'
            ];

            // Determine the appropriate ordered keys based on the country
            let orderedKeys;
            switch (result.country) {
                case 'United States':
                    orderedKeys = orderedKeysUS;
                    break;
                case 'Singapore':
                    orderedKeys = orderedKeysSG;
                    break;
                case 'China':
                    orderedKeys = orderedKeysCN;
                    break;
                default:
                    orderedKeys = Object.keys(result);
            }

            // Filter and format each key in the result object
            orderedKeys.forEach(key => {
                if (key in result) {
                    // Format the key name from snake_case to Title Case
                    let formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

                    // Determine if the value should be formatted as currency
                    let value = result[key];
                    value = formatCurrency(value);

                    resultHTML += `<tr>
                                     <td>${formattedKey}</td>
                                     <td>${value}</td>
                                   </tr>`;
                }
            });

            resultHTML += `</table>`;
            document.getElementById('result').innerHTML = resultHTML;
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

        if (result.country === 'Singapore') {
            // Singapore breakdown
            labels = ['Net Income', 'Income Tax', 'Employee CPF'];
            data = [
                result.net_income,
                result.income_tax,
                result.employee_cpf_contribution
            ];
        } else if (result.country === 'United States') {
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
        } else if (result.country === 'China') {
            // China breakdown
            labels = ['Net Income', 'Income Tax', 'Employee Social Insurance'];
            data = [
                result.net_income,
                result.income_tax,
                result.employee_social_insurance
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
        } else if ('employer_401k_contribution' in result) {
            // US
            labels = ['Employer 401(k) Contribution'];
            data = [(result.employer_401k_contribution / result.gross_income) * 100];
        } else if ('employer_social_insurance' in result) {
            // China
            labels = ['Employer Social Insurance'];
            data = [(result.employer_social_insurance / result.gross_income) * 100];
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