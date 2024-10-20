// Step 1: Function to get the token
async function getToken(username, password) {
    const response = await fetch('http://localhost:3000/user/token', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'username': username,
            'password': password
        })
    });

    if (!response.ok) {
        throw new Error('Failed to obtain token');
    }

    const data = await response.json();
    return data.access_token; // Assuming the token is in "access_token" field
}

// Step 2: Function to call login endpoint with the token
async function loginWithToken(token) {
    const response = await fetch('http://localhost:3000/user/login', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    });

    console.log(response);

    if (!response.ok) {
        throw new Error('Login failed');
    }

    const userData = await response.json();
    return userData;
}

// Example: Using both functions
(async () => {
    try {
        // Replace with real username and password
        const username = 'siddhesh@gmail.com';
        const password = 'sid123456';

        // Step 1: Get the token
        const token = await getToken(username, password);
        console.log('Token:', token);

        // Step 2: Use the token to log in
        const user = await loginWithToken(token);
        console.log('User Data:', user);
    } catch (error) {
        console.error('Error:', error);
    }
})();
