const baseUrl = 'http://localhost:3000/news/';

// Write in mjs that is ES6 format

// const getAggregatedNews = require('./utils.js');
import { getAggregatedNews } from './utils.mjs';

// Example parameters
const startDate = new Date('2024-08-09');
const endDate = new Date('2024-08-15');
const keyWords = ['climate change', 'environment'];
const endPoint = 'everything';
const language = 'en';
const threshold = 10;
const page = 1;
const perPage = 10;

// Convert dates to YYYY-MM-DD format
const formattedStartDate = startDate.toISOString().split('T')[0];
const formattedEndDate = endDate.toISOString().split('T')[0];

const apiURL = `${baseUrl}?startDate=${formattedStartDate}&endDate=${formattedEndDate}&endPoint=${endPoint}&language=${language}&threshold=${threshold}&page=${page}&perPage=${perPage}`;

// Call the function
const aggregatedNews = await getAggregatedNews(apiURL, keyWords); //.then((data) => {
// aggregatedNews = data;
// console.log(aggregatedNews);
// });

console.log(aggregatedNews);

