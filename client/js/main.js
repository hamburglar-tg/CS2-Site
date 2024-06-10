const steamId = getCookie("steamId")
const socket = io(':8080');
const roulettePanel = document.getElementById("roulettePanel")
const progressTimeBar = document.getElementById("progressTimeBar")


function showForm() {
    const accountButtons = document.querySelectorAll("#accountButton");

    accountButtons.forEach((button) => {
        button.innerHTML = `
            <button id="steamLoginBtn" class="steam-login"><img src="../img/steam-logo.png" class="steam-logo" alt="#">Login with Steam</button>
        `;
    });

    document.getElementById("steamLoginBtn").addEventListener("click", loginUser);
}

function showContent(steamId) {
    const accountButtons = document.querySelectorAll("#accountButton");

    accountButtons.forEach((button) => {
        let contentHTML = steamId ? `<button id="openProfileBtn" class="steam-login">Профиль</button>` : `<button id="steamLoginBtn" class="steam-login"><img src="../img/steam-logo.png" class="steam-logo" alt="#">Login with Steam</button>`;

        if (button.innerHTML !== contentHTML) {
            button.innerHTML = contentHTML;
        }
    });

    if (steamId) {
        document.getElementById("topPanelBtn").innerHTML = `<a id="depositButton" style="display: flex;" onclick="sendItems()">УЧАВСТВОВАТЬ</a>`
        document.getElementById("openProfileBtn").addEventListener("click", openProfile);
    }
}

function openProfile() {
    window.location.href = "/profile.html"
}

function backMainPage() {
    history.replaceState({}, document.title, window.location.origin);
    location.reload()
}

function loginUser() {
    const redirectUrl = window.location.origin;
    window.location.href = 'https://steamcommunity.com/openid/login' +
        '?openid.ns=http://specs.openid.net/auth/2.0' +
        '&openid.mode=checkid_setup' +
        '&openid.return_to=' + redirectUrl +
        '&openid.realm=' + redirectUrl +
        '&openid.identity=http://specs.openid.net/auth/2.0/identifier_select' +
        '&openid.claimed_id=http://specs.openid.net/auth/2.0/identifier_select';
}

function checkOpenIdMode() {
    const urlParams = new URLSearchParams(window.location.search);
    const openidMode = urlParams.get('openid.mode');

    if (openidMode === 'id_res') {
        const steamIdUrl = urlParams.get('openid.claimed_id');
        const steamId = steamIdUrl.split('/').pop();
        history.replaceState({}, document.title, window.location.origin);
        document.cookie = 'steamId=' + steamId;
        showContent(steamId);
        socket.emit('login', {"steamId": steamId});
        console.log('[LOG] User successfully logged in');
    }
}

function getCookie(name) {
    let cookies = document.cookie.split("; ");
    for (let i = 0; i < cookies.length; i++) {
        let cookie = cookies[i].split("=");
        if (cookie[0] === name) {
            return cookie[1];
        }
    }
    return null;
}

function sendItems() {
    socket.emit('bot_trade_link')
}

function changeText() {
    socket.emit('get_online')

    const randomTime = Math.floor(Math.random() * (60000 - 20000 + 1)) + 20000;

    setTimeout(changeText, randomTime);
}

steamId ? showContent(steamId) : showForm();
checkOpenIdMode();
changeText();

function addScrollPlayer(avatarUrl, userNickname, userChance, userSteamId) {
    const parentElement = document.getElementById('depUsers');
    const newItem = document.createElement('div');
    newItem.className = 'scroll_item';
    newItem.title = userNickname;

    const avatar = document.createElement('div');
    avatar.className = 'scroll_user_avatar';
    avatar.style.backgroundImage = `url(${avatarUrl})`;
    newItem.appendChild(avatar);

    const chanceDiv = document.createElement('div');
    chanceDiv.className = 'scroll_item_chance';

    const chance = document.createElement('div');
    chance.className = `chance`;
    chance.id = `chance ${userSteamId}`;
    chance.textContent = `${userChance}%`;

    const text = document.createTextNode('возможность');
    chanceDiv.appendChild(chance);
    chanceDiv.appendChild(text);
    newItem.appendChild(chanceDiv);

    parentElement.appendChild(newItem);
}

function addGameItems(avatarUrl, itemsCount, itemsSum, useChance, itemsList, userNickname, userSteamId) {
    const parentElement = document.getElementById('gameItemsContainer');
    const newItem = document.createElement('div');
    newItem.className = 'game_user';

    const gameUserInfo = document.createElement('div');
    gameUserInfo.className = 'game_user_info';

    const userLeft = document.createElement('div');
    userLeft.className = 'user-left';

    const userAvatar = document.createElement('div');
    userAvatar.className = 'game_user_avatar';
    userAvatar.style.backgroundImage = `url(${avatarUrl})`;
    userLeft.appendChild(userAvatar);

    const rightInfo = document.createElement('div');
    rightInfo.className = 'right_info';

    const userNicknameDiv = document.createElement('div');
    userNicknameDiv.className = 'game_user_nickname';
    userNicknameDiv.textContent = userNickname;

    const rightInfoText = document.createElement('div');
    rightInfoText.className = 'right_info_text';
    rightInfoText.innerHTML = `Закинул <strong>${itemsCount}</strong> предметов на сумму<span class="price">${itemsSum} р.</span> Возможность <strong id="chance ${userSteamId}">${useChance}</strong>%`;
    rightInfoText.id = `rightUserInfoText${steamId}`

    rightInfo.appendChild(userNicknameDiv);
    rightInfo.appendChild(rightInfoText);
    userLeft.appendChild(rightInfo);

    const gameUserItems = document.createElement('div');
    gameUserItems.className = `game_user_items`;
    gameUserItems.id = `userItems${userSteamId}`

    for (const key in itemsList) {
        if (itemsList.hasOwnProperty(key)) {
            const item = itemsList[key];
            const gameUserItem = document.createElement('div');
            gameUserItem.className = 'game_user_item';

            const itemImage = document.createElement('div');
            itemImage.className = 'item_image';
            itemImage.style.backgroundImage = `url(${item.icon_url})`;

            const itemCost = document.createElement('div');
            itemCost.className = 'item_cost';
            itemCost.innerHTML = `<strong>${item.item_cost}</strong> р`;

            gameUserItem.appendChild(itemImage);
            gameUserItem.appendChild(itemCost);

            gameUserItems.appendChild(gameUserItem);
        }
    }

    gameUserInfo.appendChild(userLeft);
    newItem.appendChild(gameUserInfo);
    newItem.appendChild(gameUserItems);

    parentElement.appendChild(newItem);
}

function updateUser(steamID, itemsList, itemsCount, chance, itemsCost, trade_items_count) {
    let existingContainer = document.getElementById(`userItems${steamID}`);
    let userInfo = document.getElementById(`rightUserInfoText${steamId}`);
    userInfo.innerHTML = `Закинул <strong>${itemsCount}</strong> предметов на сумму<span class="price">${itemsCost} р.</span> Возможность <strong id="chance ${steamID}">${chance}</strong>%`;

    if (existingContainer) {
        const itemsKeys = Object.keys(itemsList);
        const lastItemsKeys = itemsKeys.slice(-trade_items_count);

        for (const key of lastItemsKeys) {
            const item = itemsList[key];
            const gameUserItem = document.createElement('div');
            gameUserItem.className = 'game_user_item';

            const itemImage = document.createElement('div');
            itemImage.className = 'item_image';
            itemImage.style.backgroundImage = `url(${item.icon_url})`;

            const itemCost = document.createElement('div');

            itemCost.className = 'item_cost';
            itemCost.innerHTML = `<strong>${item.item_cost}</strong> р`;

            gameUserItem.appendChild(itemImage);
            gameUserItem.appendChild(itemCost);
            existingContainer.appendChild(gameUserItem);

        }
    }
}

function spin(winners, rouletteTimerValue) {
    let winnerIndex = 112;

    const carousel = document.getElementById('rouletteUsersScroll');
    const fragment = document.createDocumentFragment();

    winners.forEach((userObj, idx) => {
        const user = Object.keys(userObj)[0];
        const userValue = userObj[user];

        const activeClass = idx === winnerIndex ? 'winner' : '';

        const rouletteItem = document.createElement('div');
        rouletteItem.className = `roulette_item ${activeClass}`;

        const rouletteItemAvatar = document.createElement('div');
        rouletteItemAvatar.className = 'roulette_item_avatar';

        const img = document.createElement('img');
        img.src = userValue.avatar;
        img.alt = '';

        rouletteItemAvatar.appendChild(img);
        rouletteItem.appendChild(rouletteItemAvatar);

        fragment.appendChild(rouletteItem);
    });

    carousel.appendChild(fragment);

    roulettePanel.style.display = "block";
    progressTimeBar.style.display = "none";

    const itemWidth = carousel.children[0].offsetWidth + 14;
    const visibleWidth = document.getElementById('roulettePanel').clientWidth;
    const centerOffset = (visibleWidth / 2) - (itemWidth / 2);
    const currentScroll = carousel.scrollLeft || 0;

    carousel.style.transition = `margin-left ${rouletteTimerValue}s`;
    carousel.style.marginLeft = `${-winnerIndex * itemWidth + centerOffset - currentScroll}px`;

    setTimeout(() => {
        carousel.style.transition = 'margin-left 0s';
        carousel.style.marginLeft = '0px';
        roulettePanel.style.display = "none";
        progressTimeBar.style.display = "flex";
    }, 25000);
}

function showWinner(nickname, avatar, bank) {
    document.getElementById('last-avatar-winner').src = avatar;
    document.getElementById('last-name-winner').textContent = nickname;
    document.getElementById('last-price-winner').textContent = bank;
}

function updateGameInfo(games_today, last_winner, last_game_id, game_bank, items_count, timerValue, strike, peak_online) {
    const widthPercentage = (items_count / 200) * 100;
    let minutes = Math.floor(timerValue / 60);
    let seconds = timerValue % 60;

    minutes = minutes < 10 ? "0" + minutes : minutes;
    seconds = seconds < 10 ? "0" + seconds : seconds;

    document.getElementById("gamesToday").innerHTML = games_today;
    document.getElementById("last-avatar-winner").src = last_winner["avatar"];
    document.getElementById("last-name-winner").innerHTML = last_winner["nickname"];
    document.getElementById("last-price-winner").innerHTML = last_winner["bank"];
    document.getElementById("roundId").innerHTML = last_game_id;
    document.getElementById("roundBank").innerHTML = game_bank;
    document.getElementById("progressTextContainer").innerHTML = `${items_count} / 200<span> предметов</span>`
    document.getElementById("progressBarContainer").style.width = `${widthPercentage}%`;
    document.getElementById("gameTimer").textContent = minutes + ":" + seconds;
    document.getElementById("strikeNum").textContent = strike;
    document.getElementById("playersPeak").textContent = peak_online;
}

function deleteUsers() {
    const parentElement2 = document.getElementById('depUsers');
    const parentElement = document.getElementById('gameItemsContainer');
    const parentElement3 = document.getElementById('rouletteUsersScroll');

    while (parentElement2.firstChild) {
        parentElement2.removeChild(parentElement2.firstChild);
    }

    while (parentElement.firstChild) {
        parentElement.removeChild(parentElement.firstChild);
    }

    while (parentElement3.firstChild) {
        parentElement3.removeChild(parentElement3.firstChild);
    }
}

function updateUsersChances(new_users_chances) {
    new_users_chances.forEach(user => {
        const steamid = user['steamid'];
        const chance = user['chance'];

        const elements = document.querySelectorAll(`[id^="chance ${steamid}"]`);
        elements.forEach(element => {
            if (element.tagName === 'STRONG') {
                element.textContent = chance;
            } else {
                element.textContent = chance + "%";
            }
        });
    });
}

socket
    .on('connect', function () {
        socket.emit("project_info")
    })
    .on('disconnect', function () {
        deleteUsers();
    })
    .on('online', function (data) {
        document.getElementById("currentOnline").innerHTML = data.online
    })
    .on("projectInfo", function (data) {
        let { games_today, last_winner, last_game_id, game_bank, items_count, isRouletteStarted, current_game_users, shuffle_winners, roulette_timer_value, timer_value, strike, peak_online } = data;

        if (isRouletteStarted) {
            document.getElementById("progressTimeBar").style.display = "none";
            document.getElementById("roulettePanel").style.display = "flex";

            spin(shuffle_winners, roulette_timer_value)
        } else {
            document.getElementById("progressTimeBar").style.display = "flex";
            document.getElementById("roulettePanel").style.display = "none";
        }

        updateGameInfo(games_today, last_winner, last_game_id, game_bank, items_count, timer_value, strike, peak_online)

        current_game_users.forEach(userObj => {
            const userSteamId = Object.keys(userObj)[0];

            const userData = userObj[userSteamId];

            const { avatar, nickname, user_bank, user_items_count, chance, items } = userData;

            addGameItems(avatar, user_items_count, user_bank, chance, items, nickname, userSteamId);
            addScrollPlayer(avatar, nickname, chance, userSteamId)
        });

        document.body.classList.remove("loading");
    })
    .on('updateBet', function (data) {
        console.log("BET UPDATE")

        let trade_items_count = data["items_count"]
        let user_data = data["user_dict"]

        let steamID = Object.keys(user_data)[0];
        let { status, user_bank, user_items_count, chance, items } = user_data[steamID];

        updateUser(steamID, items, user_items_count, chance, user_bank, trade_items_count)
    })
    .on('newDeposit', function (data) {
        console.log("NEW DEPOSIT")

        let steamID = Object.keys(data)[0];
        let { status, avatar, nickname, user_bank, user_items_count, chance, items } = data[steamID];

        addGameItems(avatar, user_items_count, user_bank, chance, items, nickname, steamID)
        addScrollPlayer(avatar, nickname, chance, steamID)
    })
    .on('gameInfo', function (data) {
        console.log("NEW PROJECT INFO")

        let { games_today, last_winner, last_game_id, game_bank, items_count, timer_value, strike, peak_online, new_users_chances } = data;

        updateGameInfo(games_today, last_winner, last_game_id, game_bank, items_count, timer_value, strike, peak_online);
        updateUsersChances(new_users_chances);
    })
    .on('newGame', function () {
        console.log("new game started")
        deleteUsers()
        socket.emit("project_info")
        document.getElementById("gameTimer").textContent = "00:05";
    })
    .on('botTradeLink', function (data) {
        window.location.href = data['bot_trade_link'];
    })
    .on('timer', function (data) {
        let display = document.getElementById("gameTimer");
        let minutes = Math.floor(data / 60);
        let seconds = data % 60;

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.textContent = minutes + ":" + seconds;
    })
    .on('startRoulette', function (data) {
        document.getElementById("progressTimeBar").style.display = "none";
        document.getElementById("roulettePanel").style.display = "flex";

        spin(data, 15)
    })
    .on('winner_data', function (data) {
        showWinner(data["winner_nickname"], data["winner_avatar"], data["winner_user_bank"])
    })


window.addEventListener('pageshow', function(event) {
    if (event.persisted) {
        socket.disconnect();
        socket.connect();
    }
});