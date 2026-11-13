'use strict';


document.addEventListener("DOMContentLoaded", () => {
  let gameLetters= [];
  let guesses= [];
  let score = 0;
  let is_over = false;
  let gameId= 1;
  let streak;
  const streakTxt= document.getElementById("streak");

  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);

  // FETCH INITIAL DATA --------------------------------------------------
  fetch('/api/spelling-bee')
    .then(res => res.json())
    .then(data => {
      //If user is a guest, use local storage
      if(!data.user){
        if(!window.localStorage.getItem("spellingBeeData")){
          window.localStorage.setItem("spellingBeeData", JSON.stringify(data));
          window.localStorage.setItem("spellingBeeStreak", 0);
          streak = JSON.parse(window.localStorage.getItem("spellingBeeStreak"));
          streakTxt.textContent = "Spelling Bee streak: " + streak;
        }
        else if(JSON.parse(window.localStorage.getItem("spellingBeeDate")) != new Date().toDateString()){
          window.localStorage.setItem("spellingBeeData", JSON.stringify(data));
          if(JSON.parse(window.localStorage.getItem("spellingBeeDate")) == yesterday.toDateString()){
            streak = JSON.parse(window.localStorage.getItem("spellingBeeStreak"));
            streakTxt.textContent = "Spelling Bee streak: " + streak;
          }
          else{
            window.localStorage.setItem("spellingBeeStreak", 0);
            streak = JSON.parse(window.localStorage.getItem("spellingBeeStreak"));
            streakTxt.textContent = "Spelling Bee streak: " + streak;
          }
        }
        else{
          streak = JSON.parse(window.localStorage.getItem("spellingBeeStreak"));
          streakTxt.textContent = "Spelling Bee streak: " + streak;
          data = JSON.parse(window.localStorage.getItem("spellingBeeData"));
          score = data.spellingBee.score;
          is_over = data.spellingBee.is_over;
        }
      }

      gameLetters= [...data.spellingBee.letters];
      gameId= data.spellingBee.game_id;
      guesses= [...data.spellingBee.guesses];
      score = data.spellingBee.score;
      is_over = data.spellingBee.is_over;

      renderHive();
      updateWordCount(data.spellingBee.guesses.length);
      scoreDisplay.textContent= data.spellingBee.score;
      tierDisplay.textContent= data.spellingBee.tier.replaceAll('-', ' ');

      if (streakTxt && data.spelling_bee_streak !== undefined) {
        streakTxt.textContent= "Spelling Bee streak: "+ data.spelling_bee_streak;
      }
      
      guesses.forEach(word => addGuessToList(word, true, false));

      if (data.spellingBee.tier === 'Queen-Bee')
        showQueenBeePopup();

    })
    .catch(err => console.error('Error loading game: ', err));
  

  // RENDER HIVE HEXAGONS -----------------------------------------------
  const hive= document.getElementById('hive');

  function renderHive() {
    document.querySelectorAll('[data-idx]').forEach(hex => {
      const idx= hex.getAttribute('data-idx');
      const letter= gameLetters[idx];

      const letterEl= hex.querySelector('.hive_letter');
      letterEl.textContent= letter;

      hex.addEventListener('click', () => {
        inputBox.value+= letter;
      });
    });
  }


  // SHUFFLE LETTERS LOGIC (FISHER-YATES) --------------------------------
  // swaps last element with a randomly selected element
  function shuffleLetters() {
    let center= gameLetters[0];
    let outer= gameLetters.slice(1);

    for (let i = outer.length-1; i>0; i--) {
      const j= Math.floor(Math.random() * (i+1));
      [outer[i], outer[j]]= [outer[j], outer[i]]; // destructuring assignment
    }
    gameLetters= [center, ...outer];
    renderHive();
  }


  // SUBMIT A GUESS ----------------------------------------------------
  const inputBox= document.getElementById('userInput_SpellingBee');
  const guessList= document.querySelector('#guesses ul');
  const scoreDisplay= document.getElementById('score');
  const tierDisplay= document.getElementById('tier');
  const errMsg= document.getElementById('error-msg');
  
  function submitGuess() {
    const guess= inputBox.value.toUpperCase();

    if (!guess)
      return;

    fetch('/api/spelling-bee', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_guess: guess,
        guesses: guesses,
        score: score,
        is_over : is_over
      })
    })
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          errMsg.textContent = data.error;
          errMsg.style.color = "rgb(240, 75, 75)";
          inputBox.value= '';
          return;
        }

        addGuessToList(data.guess_state.guess, false, data.guess_state.pangram);
        
        if(!data.user){
          let update = JSON.parse(window.localStorage.getItem("spellingBeeData"));
          score = data.guess_state.score
          is_over = data.guess_state.is_over
          update.spellingBee.score = score;
          update.spellingBee.tier = data.guess_state.tier;
          update.spellingBee.guesses = guesses;
          update.spellingBee.is_over = data.guess_state.is_over;
          update.spellingBee.status = data.guess_state.status;
          window.localStorage.setItem("spellingBeeData", JSON.stringify(update));

          scoreDisplay.textContent= update.spellingBee.score;
          tierDisplay.textContent= data.guess_state.tier.replaceAll('-', ' ');

          if(JSON.parse(window.localStorage.getItem("spellingBeeDate")) == yesterday.toDateString() || !window.localStorage.getItem("spellingBeeDate")){
            streak = JSON.parse(window.localStorage.getItem("spellingBeeStreak")) + 1;
            window.localStorage.setItem("spellingBeeStreak", streak);
            streakTxt.textContent= "Spelling Bee streak: "+ streak;
          }

          window.localStorage.setItem("spellingBeeDate", JSON.stringify(new Date().toDateString()));
        }

        else{
          scoreDisplay.textContent= data.guess_state.score;
          tierDisplay.textContent= data.guess_state.tier.replaceAll('-', ' ');
        }

        if (data.guess_state.pangram)
          showPangramPopup();

        if (data.guess_state.tier === 'Queen-Bee')
          showQueenBeePopup();
        
        errMsg.textContent= '';
        inputBox.value= '';

        if (streakTxt && data.spelling_bee_streak !== undefined) {
          streakTxt.textContent= "Spelling Bee streak: "+ data.spelling_bee_streak;
        }
      })
      .catch(err => console.error(err));
  }

  // helper - adds guess to the list and updates the word count if not skipping
  function addGuessToList(word, skipPush=false, isPangram=false) {
    const li= document.createElement('li');
    li.className= 'guessed_word_SpellingBee';
      li.textContent= word;

    if (isPangram) {
      li.classList.add('pangramWord');
    }

    guessList.appendChild(li);

    // skips adding the word to the guesses array if it was already loaded from the server (avoids dupes)
    if (!skipPush) {
      guesses.push(word);
      updateWordCount(guesses.length);
    }
  }


  // WORD COUNTER ------------------------------------------------------
  const foundTitle= document.getElementById('foundWordsTitle');

  function updateWordCount(count) {
    if (count === 1)
      foundTitle.textContent= "You have found 1 word";
    else
      foundTitle.textContent= "You have found "+ count +" words";
  }


  // BUTTONS -----------------------------------------------------------
  const buttons= document.querySelectorAll('.control_button');
  const deleteBtn= buttons[0];
  const shuffleBtn= buttons[1];
  const enterBtn= buttons[2];

  function deleteLetter() {
    inputBox.value= inputBox.value.slice(0, -1);
  }

  deleteBtn.addEventListener('click', deleteLetter);
  shuffleBtn.addEventListener('click', shuffleLetters);
  enterBtn.addEventListener('click', submitGuess);


  // KEYBOARD INPUT ----------------------------------------------------
  document.addEventListener('keydown', handleKeydown);

  function handleKeydown(e){
    const key= e.key.toUpperCase();

    if (key === 'ENTER') {
      e.preventDefault();
      submitGuess();
      return;
    }
    if (key === 'BACKSPACE') {
      e.preventDefault();
      deleteLetter();
      return;
    }
    if (gameLetters.includes(key)) {
      inputBox.value+= key;
    }
  }


  // POPUPS ----------------------------------------------
  const queenBeePopup= document.getElementById('queenBeePopup');
  const pangramPopup = document.getElementById('pangramPopup');

  function showQueenBeePopup() {
    queenBeePopup.classList.add('show');

    setTimeout(() => {
      queenBeePopup.classList.remove('show');
    }, 2500);
  }

  function showPangramPopup() {
    pangramPopup.classList.add('show');

    setTimeout(() => {
      pangramPopup.classList.remove('show');
    }, 1800);
  }
});
