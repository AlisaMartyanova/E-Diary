document.getElementById('register-button').onclick = async function validation() {
    var name = document.getElementById('username').value;
    var password = document.getElementById('password').value;
    
    

    // if (password != password_conf) {
    //     alert("Passwords do not match!\nPlease, try again.");
    //     return 0;
    // }

    let result = await registerStudent(name, password)

    if (result) {
        alert("You successfully registered");

        window.location.href = 'notes.html';
    } else {
        alert("Error")
        return
    }
}

async function registerStudent(name, password) {
    const url = `http://52.89.142.217:5000/registration`
    //
    const data = {
        username: name,
        password: password
    }

    const json = JSON.stringify(data);

    let response = await fetch(url, {
        method: 'POST',
        body: JSON.stringify(data),
        headers:
            {
                "Content-type": "application/json; charset=UTF-8"
            }
    });

    let text = await response.json()

    let result = response.ok

    if (result) {
        window.localStorage.setItem('token', text['access_token']);
        return true
    } else {
        alert(response.statusText)
        return false
    }
}