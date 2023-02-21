
// check for auth token in session storage
// if none
//  redirect to login page
// else
//  return the token, continue

const API_DOMAIN = 'http://localhost:8000'


function getAccessToken() {
    const {access, refresh} = _loadTokens();
    if (access != null) {
        return access;
    } else if (refresh != null) {
        const {access, refresh} = _authWithRefreshToken(refresh)
        _storeTokens(access, refresh);
        return access;
    } else {
        let url = new URL(window.location);
        let searchParams = new URLSearchParams({next: url.toString()});
        let loginUrl = new URL(`${url.origin}/login.html?${searchParams.toString()}`);
        window.location.replace(loginUrl.toString());
    }
}

function authenticate(username, password) {
    const {access, refresh} = _authWithCredentials(username, password);
    _storeTokens(access, refresh);
    let next = (new URL(window.location)).searchParams.get("next") || "/";
    window.location = next;
}

async function _authWithRefreshToken(refresh) {
    const response = await fetch(
        API_DOMAIN + '/api/auth/refresh', 
        {method: "POST", body: {refresh: refresh}}
    );
    if (!response.ok) {
        console.error("Error refreshing auth token");
        return
    }
    return response.json();
}

async function _authWithCredentials(username, password) {
    const response = await fetch(
        API_DOMAIN + '/api/auth/login', 
        {method: "POST", body: {username: username, password: password}},
    );
    if (!response.ok) {
        console.error("Error authenticating");
        return
    }
    return response.json();
}

function _storeTokens(access, refresh) {
    window.sessionStorage.setItem("auth.accessToken", access);
    window.sessionStorage.setItem("auth.refreshToken", refresh);
}

function _loadTokens() {
    let accessToken = window.sessionStorage.getItem("auth.accessToken");
    let refreshToken = window.sessionStorage.getItem("auth.refreshToken");
    return {accessToken, refreshToken};
}

function handleLogin(event) {
    event.preventDefault();
    authenticate(document.forms.login.username, document.forms.login.password);
    return false;
}