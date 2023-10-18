document.addEventListener("DOMContentLoaded", () => {
    // Check if a user is already logged in
    let loggedIn = getCookie("username");
    let loginPage = document.getElementById("login-page");
    let contentPage = document.getElementById("content-page");
    
    if (loggedIn) {
        // If a user gives a cookie, then it is already logged in
        showContentPage();
        getTweets();
    } else {
        // If no user is logged in, show the login page
        showLoginPage();
    }
    

    // hide the content and show login
    function showLoginPage() {
        loginPage.style.display = "block";
        contentPage.style.display = "none";
    }
    
    // hide the login and show the content
    function showContentPage() {
        loginPage.style.display = "none";
        contentPage.style.display = "block";
    }
    
    
    // Function to get a cookie by name
    function getCookie(name) {
        let cookies = document.cookie.split("; ");
        for (let cookie of cookies) {
            let [cookieName, cookieValue] = cookie.split("=");
            if (cookieName === name) {
                return cookieValue;
            }
        }
        return null;
    }



    // Handle the login button click
    let loginButton = document.getElementById("login-button");
    loginButton.addEventListener("click", () => {

        let usernameInput = document.getElementById("username");
        let username = usernameInput.value;

        if (username) {
            // Set a request to the server to send a cookie
            let xhr = new XMLHttpRequest();
            xhr.open('POST', '/api/login',true );
            xhr.setRequestHeader('Content-Type', 'text/plain');
            let data = username;
            xhr.send("name:" + data +"\n")

            xhr.onload = function()
            {
                if(xhr.status === 200)
                {
                    showContentPage();
                    getTweets();
                } else
                {
                    document.getElementById("login-page").textContent = "COULD NOT LOGIN, PLEASE TRY AGAIN LATER"
                }
                
            }

            
            
        }
    });

    let postButton = document.getElementById("post-button");
    postButton.addEventListener("click", () => {

        let tweetInput = document.getElementById("post-input");
        let tweet = tweetInput.value;

        if(tweet) {
            //send a request to add this tweet to the database to the server
            let xhr = new XMLHttpRequest();
            xhr.open('POST', '/api/tweet', true);
            xhr.setRequestHeader('Content-Type', 'application/json')
            let user = getCookie("username");
             

            let data = { //turn the tweet into json
                input : tweet,
                username : user
            }

            data = JSON.stringify(data);
            xhr.send(data);

            xhr.onload = function()
            {
                getTweets();
            }


        }


    });

    //get the tweets from the server
    function getTweets()
    {
        let xhr = new XMLHttpRequest();
        xhr.open('GET', '/api/tweet', true);
        xhr.send();

        xhr.onload = function() {
            if ( xhr.status === 200)
            {
                let tweets = JSON.parse(xhr.response);
                let id = 0
                let HTML = '';
                for(var key in tweets){
                    id++;
                    console.log(tweets[key] + id)

                    HTML += '<div>'
                    let inputHTML = `<input type="text" id="post${id}" value="${tweets[key]}">`;
                    let buttonHTML =`<button type="button" id="update-button${id}">Update Tweet</button>`;    
                    HTML += inputHTML
                    HTML += buttonHTML
                    HTML += '</div>'
                }

                document.getElementById("content").innerHTML = HTML ;
            } else
            {
                document.getElementById("content").textContent = 'Error fetching data';
            }
        }
    }
    
});