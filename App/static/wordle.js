document.addEventListener("DOMContentLoaded", ()=>{
    const guessGrid = document.getElementById("guessGrid");
    const keyboard = document.getElementById("keyboard");
    const allKeyboardKeys = document.querySelectorAll(".key");
    const completed_rows = [];
    let userGuesses = {};
    let message = document.getElementById("message");
    const streakTxt= document.getElementById("streak");
    let streak;

    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);

    // ----------------------------------------------
    // Load user data - Fill GuessGrid Dynamically
    // ----------------------------------------------

    // Fetches JSON from API
    fetch('/api/wordle')
        .then((r) => r.json())
        .then((userData) => {

            //If user is a guest, use local storage
            if(!userData.user){
                if(!window.localStorage.getItem("wordleData")){
                    window.localStorage.setItem("wordleData", JSON.stringify(userData));
                    window.localStorage.setItem("wordleStreak", 0);
                    streak = JSON.parse(window.localStorage.getItem("wordleStreak"));
                    streakTxt.textContent = "Wordle streak: " + streak;
                }
                else if(JSON.parse(window.localStorage.getItem("wordleDate")) != new Date().toDateString()){
                    window.localStorage.setItem("wordleData", JSON.stringify(userData));
                    if(JSON.parse(window.localStorage.getItem("wordleDate")) == yesterday.toDateString()){
                        streak = JSON.parse(window.localStorage.getItem("wordleStreak"));
                        streakTxt.textContent = "Wordle streak: " + streak;
                    }
                    else{
                        window.localStorage.setItem("wordleStreak", 0);
                        streak = JSON.parse(window.localStorage.getItem("wordleStreak"));
                        streakTxt.textContent = "Wordle streak: " + streak;
                    }
                }
                else{
                    streak = JSON.parse(window.localStorage.getItem("wordleStreak"));
                    userData = JSON.parse(window.localStorage.getItem("wordleData"));
                    streakTxt.textContent = "Wordle streak: " + streak;
                }
            }
            userGuesses = userData.wordle.guesses;
            let keys = Object.keys(userGuesses);

            // Load guesses in Letterboxes
            // Loops through each row
            for(let i = 0; i < 6; i++){
                let row = document.createElement("form");
                row.method = "POST";
                row.action = "/wordle";
                row.classList.add("row");
                row.id = "row"+(i+1);
                // Loops through each letterbox
                for(let p = 0; p < 5; p++){
                    let letterbox = document.createElement("div");
                    letterbox.classList.add("letterbox");
                    let input = document.createElement("input");
                    input.classList.add("userInput_Wordle");
                    input.name = "row"+(i+1);
                    input.type = "text";
                    input.maxLength = 1;
                    input.readOnly = true;
                    if(keys[i] !== undefined){
                        input.value = keys[i][p];
                    }
                    else{
                        input.value = "";
                    }
                    letterbox.appendChild(input);
                    row.appendChild(letterbox);
                }   
                    
                if(keys[i] !== undefined){
                    completed_rows.push(true);
                    checkWord(keys[i], userData.wordle.guesses[keys[i]], row.children);
                }
                else{
                    completed_rows.push(false);
                }

                if(userData.wordle.won == true){
                    document.removeEventListener("keydown", goNextLetterBox);
                    allKeyboardKeys.forEach((button) => {
                        button.removeEventListener("mousedown", goNextLetterBox)
                    });
                    message.textContent = "Congratulations, you found the word! "+userData.wordle.word;
                    message.style.color = "rgb(57, 201, 141)";
                }
            guessGrid.appendChild(row);
            }
            if(userData.wordle.is_over && !userData.wordle.won){
                message.textContent = "You couldn't find the word. The word is: "+userData.wordle.word;
                message.style.color = "rgb(240, 75, 75)";
            }

            if (streakTxt && result.wordle_streak !== undefined) {
                streakTxt.textContent= "Wordle streak: "+ result.wordle_streak;
            }
    });


    // ----------------------------------------------
    // Game functionality
    // ----------------------------------------------
    
    document.addEventListener("keydown", goNextLetterBox);

    // Checks word and color animate the letter boxes
    function checkWord(inputWord, letterState, row_letterboxes){
        let delay = 0;
        for(let i = 0; i < 5; i++){
            let buttonLetter;
            if(letterState[i] == "correct"){
                row_letterboxes[i].querySelector("input").style.backgroundColor = "rgb(57, 201, 141)";
                row_letterboxes[i].querySelector("input").style.animationName = "userInput_animation";
                row_letterboxes[i].querySelector("input").style.animationDelay = delay+"s";
                row_letterboxes[i].querySelector("input").style.transitionDelay = delay+"s";
                buttonLetter = document.getElementById(inputWord[i]).style.backgroundColor = "rgb(57, 201, 141)";
                delay += 0.2;
            }
            else if(letterState[i] == "present"){
                row_letterboxes[i].querySelector("input").style.backgroundColor = "rgb(219, 195, 58)";
                row_letterboxes[i].querySelector("input").style.animationName = "userInput_animation";
                row_letterboxes[i].querySelector("input").style.animationDelay = delay+"s";
                row_letterboxes[i].querySelector("input").style.transitionDelay = delay+"s";
                buttonLetter = document.getElementById(inputWord[i]).style.backgroundColor = "rgb(219, 195, 58)";
                delay += 0.2;
            }
            else{
                row_letterboxes[i].querySelector("input").style.backgroundColor = "rgb(219, 58, 58)";
                row_letterboxes[i].querySelector("input").style.animationName = "userInput_animation";
                row_letterboxes[i].querySelector("input").style.animationDelay = delay+"s";
                row_letterboxes[i].querySelector("input").style.transitionDelay = delay+"s";
                buttonLetter = document.getElementById(inputWord[i]).style.backgroundColor = "rgb(219, 58, 58)";
                delay += 0.2;
            }
        }
    }

    function goNextLetterBox(e){
        let keyPressed = e.key;
        if(e.type === 'mousedown'){
            keyPressed = e.currentTarget.id;
        }
        let rows = document.getElementsByClassName("row");
        if(keyPressed === 'Backspace'){
            e.preventDefault();
            rowLoop : for(let i = 0; i < 6; i++){
                if(!completed_rows[i]){
                    let row = rows[i];
                    let row_letterboxes = row.children;
                    for(let p = 4; p > -1; p--){
                        let input = row_letterboxes[p].querySelector("input");
                        if(input.value != ""){
                            input.value = "";
                            break rowLoop;
                        }
                    }
                    break rowLoop;
                }
                continue;
            }
        }
        else if(keyPressed === 'Enter'){
            e.preventDefault();
            rowLoop : for(let i = 0; i < 6; i++){
                if(!completed_rows[i]){ 
                    let word = "";
                    let row = rows[i];
                    let row_letterboxes = row.children;
                    for(let p = 0; p < 5; p++){
                        let input = row_letterboxes[p].querySelector("input");
                        word += input.value;
                    }
                    
                    // temp = { ...userGuesses };
                    // temp[word.toUpperCase()] = "";

                    fetch("/api/wordle",{
                        method: "POST",
                        headers:{
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            guesses : userGuesses,
                            currentGuess : word.toUpperCase()
                        })
                    })
                    .then(r => r.json())
                        .then((result) => {
                            if(result.error){
                                message.textContent = result.error;
                                message.style.color = "rgb(240, 75, 75)";
                                row.style.animationName = "shake_animation";
                                message.style.animationName = "shake_animation";
                                setTimeout(() => {
                                    row.style.animationName = "none"
                                    message.style.animationName = "shake_animation";
                                }, 200);
                            }
                            else{
                                message.textContent = "";
                                userGuesses = {
                                    ...userGuesses,
                                    [word.toUpperCase()]: result.guess_state.letter_states
                                };

                                if(!result.user){
                                    let update = JSON.parse(window.localStorage.getItem("wordleData"));
                                    update.wordle.status = result.guess_state.status;
                                    update.wordle.won = result.guess_state.won;
                                    update.wordle.is_over = result.guess_state.is_over;
                                    update.wordle.attempts_left = result.guess_state.attempts_left;
                                    update.wordle.guesses = userGuesses;
                                    window.localStorage.setItem("wordleData", JSON.stringify(update));
                                    
                                    if(Object.keys(userGuesses).length > 0 && (JSON.parse(window.localStorage.getItem("wordleDate")) == yesterday.toDateString() || !window.localStorage.getItem("wordleDate"))){
                                        streak = JSON.parse(window.localStorage.getItem("wordleStreak")) + 1;
                                        window.localStorage.setItem("wordleStreak", streak);
                                        streakTxt.textContent = "Wordle streak: " + streak;
                                    }

                                    window.localStorage.setItem("wordleDate", JSON.stringify(new Date().toDateString()));
                                }

                                checkWord(word.toUpperCase() ,userGuesses[word.toUpperCase()], row_letterboxes);
                                completed_rows[i] = true;
                                // If the word is found, stop the game
                                if(result.guess_state.won){
                                    document.removeEventListener("keydown", goNextLetterBox);
                                    allKeyboardKeys.forEach((button) => {
                                        button.removeEventListener("mousedown", goNextLetterBox)
                                    });
                                    message.textContent = "Congratulations, you found the word! "+result.guess_state.word;
                                    message.style.color = "rgb(57, 201, 141)";
                                }

                                if(result.guess_state.is_over && !result.guess_state.won){
                                    message.textContent = "You couldn't find the word. The word is: "+result.guess_state.word;
                                    message.style.color = "rgb(240, 75, 75)";
                                }
                            }

                            if (streakTxt && result.wordle_streak !== undefined) {
                                streakTxt.textContent= "Wordle streak: "+ result.wordle_streak;
                            }
                        });
                    break rowLoop;
                }
            }
        }
        else if(/^[a-zA-Z]$/.test(keyPressed)){   
            rowLoop : for(let i = 0; i < 6; i++){
                if(!completed_rows[i]){
                    let row = rows[i];
                    let row_letterboxes = row.children;
                    for(let p = 0; p < 5; p++){
                        let input = row_letterboxes[p].querySelector("input");
                        if(input.value == ""){
                            input.value = keyPressed;
                            break rowLoop;
                        }
                    }
                    break rowLoop;
                }
                continue;
            }
        }
    }

    // Keyboard
    allKeyboardKeys.forEach((button) => {
        button.addEventListener("mousedown", goNextLetterBox)
    });
});