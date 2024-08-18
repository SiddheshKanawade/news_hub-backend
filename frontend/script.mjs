// Initial Keywords
const initialKeywords = ['climate change', 'environment'];
import { getAggregatedNews } from './utils.mjs';


window.onload = function () {
    const keywordList = document.getElementById('keyword-list');
    initialKeywords.forEach(keyword => {
        const keywordItem = document.createElement('div');
        keywordItem.className = 'keyword-item';
        keywordItem.innerHTML = `
            <span>${keyword}</span>
            <button class="remove-keyword-btn" onclick="removeKeyword(this)">x</button>
        `;
        keywordList.appendChild(keywordItem);
    });
}

export function showKeywordInput() {
    document.getElementById('keyword-input-container').style.display = 'block';
    document.getElementById('keyword-input').focus();
}

export function addKeyword(event) {
    if (event.key === 'Enter') {
        const keywordInput = document.getElementById('keyword-input');
        const keyword = keywordInput.value.trim();
        if (keyword) {
            const keywordList = document.getElementById('keyword-list');
            const keywordItem = document.createElement('div');
            keywordItem.className = 'keyword-item';
            keywordItem.innerHTML = `
                <span>${keyword}</span>
                <button class="remove-keyword-btn" onclick="removeKeyword(this)">x</button>
            `;
            keywordList.appendChild(keywordItem);
            keywordInput.value = '';
            document.getElementById('keyword-input-container').style.display = 'none';
        }
    }
}

export function removeKeyword(button) {
    const keywordItem = button.parentNode;
    keywordItem.parentNode.removeChild(keywordItem);
}

export async function handleSubmit() {
    // Gather form data
    const startDate = new Date(document.getElementById('start-date').value);
    const endDate = new Date(document.getElementById('end-date').value);
    const endPoint = document.getElementById('endpoint').value;
    const language = document.getElementById('language').value;
    const threshold = document.getElementById('threshold').value;
    const page = document.getElementById('page').value;
    const perPage = document.getElementById('per-page').value;

    // Gather keywords
    const keywordElements = document.querySelectorAll('.keyword-item span');
    const keyWords = Array.from(keywordElements).map(elem => elem.textContent);

    // Create the form data object
    const formData = {
        startDate,
        endDate,
        keyWords,
        endPoint,
        language,
        threshold,
        page,
        perPage
    };

    // Call custom function and handle the response
    const response = await customFunction(formData);
    renderCards(response);
}

// Example custom function that returns a list of dictionaries
async function customFunction(formData) {
    // Don't expose the base URL in the frontend
    const baseUrl = 'http://localhost:3000/news/';
    const formattedStartDate = formData.startDate.toISOString().split('T')[0];
    const formattedEndDate = formData.endDate.toISOString().split('T')[0];
    const apiURL = `${baseUrl}?startDate=${formattedStartDate}&endDate=${formattedEndDate}&endPoint=${formData.endPoint}&language=${formData.language}&threshold=${formData.threshold}&page=${formData.page}&perPage=${formData.perPage}`;
    // Example data returned (simulate your function's return)
    console.log('Calling API:', apiURL);

    const aggregatedNews = await getAggregatedNews(apiURL, formData.keyWords);
    console.log(aggregatedNews);
    return aggregatedNews;
}

// Function to render the cards based on response data
async function renderCards(data) {
    const cardsContainer = document.getElementById('cards-container');
    cardsContainer.innerHTML = ''; // Clear previous cards
    data.forEach(item => {
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <h4>${item.title}</h4>
            <p>${item.description}</p>
            <a href="${item.url}" target="_blank">Read More</a>
            <p>published at: ${item.publishedAt}<p>
        `;
        cardsContainer.appendChild(card);
    });
}


// the module, mjs are not automatically loaded in the browser.
// Attach the function to the global window object
window.showKeywordInput = showKeywordInput;
window.addKeyword = addKeyword;
window.removeKeyword = removeKeyword;
window.handleSubmit = handleSubmit;

