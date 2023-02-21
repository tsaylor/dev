
// check for auth token in session storage
// if none
//  redirect to login page
// else
//  return the token, continue

const API_DOMAIN = 'http://localhost:8000'


function _storeAuth(data) {
    window.sessionStorage.setItem("auth", JSON.stringify(data));
}

function _loadAuth() {
    let auth = window.sessionStorage.getItem("auth");
    if (auth) {
        auth = JSON.parse(auth);
    }
    return auth;
}

function _removeAuth() {
    window.sessionStorage.removeItem("auth")
}

function _authWithRefreshToken(refresh) {
    fetch(
        API_DOMAIN + '/api/auth/refresh', 
        {
            method: "POST",
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({refresh: refresh})
        }
    ).then((response)=>{
        if (!response.ok) {
            _removeAuth();
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    }).then((data)=>{
        _storeAuth(data);
    }).catch((error)=>{
        console.error("Error: ", error);
    })
}

function _authWithCredentials(username, password) {
    fetch(
        API_DOMAIN + '/api/auth/login', 
        {
            method: "POST",
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: username, password: password})
        },
    ).then((response)=>{
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    }).then((data)=>{
        _storeAuth(data);
        _redirectToNext();
    }).catch((error)=>{
        console.error("Error: ", error);
    })
}

function _redirectToNext() {
    let next = (new URL(window.location)).searchParams.get("next") || "/";
    window.location = next;   
}

function _redirectToLogin() {
    let url = new URL(window.location);
    let searchParams = new URLSearchParams({next: url.toString()});
    let loginUrl = new URL(`${url.origin}/login.html?${searchParams.toString()}`);
    window.location.replace(loginUrl.toString());
}

function handleLogin(event) {
    event.preventDefault();
    _authWithCredentials(
        document.forms.login.username.value,
        document.forms.login.password.value
    );
    return false;
}

function getAccessToken() {
    const auth = _loadAuth();
    if (auth?.access) {
        return auth.access;
    } else if (auth?.refresh) {
        _authWithRefreshToken(auth.refresh)
    } else {
        _redirectToLogin();
    }
}

function init(event) {
    const access = getAccessToken();
    if (access) {
        console.log(access);
    }
}