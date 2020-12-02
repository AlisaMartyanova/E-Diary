const id = 1
const url = 'http://localhost:5000/users'
const url2 = 'http://localhost:5000/add_post'
const request = new XMLHttpRequest()
request.open('GET', url, false)
request.setRequestHeader('id', "1")
    // Send request
request.send()
JSON.parse(request.responseText).forEach(user => {
    if(id == user['id']){
        const newData = {
			date: 2,
            title: "My first post",
            text: 'Hey! This is my first post to test the system.'
			}
		// user['posts'].push(newData)

        //send new data to API
        fetch(url2, {
            method: 'PATCH',
            body: JSON.stringify(newData),
            headers:
                {
                    "Content-type": "application/json; charset=UTF-8",
                    'Authorization': `Token ${token}`
                }
        })

    }
})
