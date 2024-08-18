async function getAggregatedNews(apiURL, keyWords) {
    try {
        // Make the POST request
        let response = await fetch(apiURL, {
            method: 'POST',
            headers: {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(keyWords)
        });

        if (!response.ok) {
            alert('No news found for the given criteria');
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        let data = await response.json();

        return data['results'];
    } catch (error) {
        console.log(apiURL);
        console.error('Error while calling news aggregator:', error);
    }

}

export { getAggregatedNews };