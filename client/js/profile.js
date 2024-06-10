const steamId = getCookie("steamId")
const socket = io(':8080');

checkSteamID(steamId);

function checkSteamID(steamID) {
    if (!steamID) {
        window.location.href = "/"
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

function toggleMenu() {
    const mobileMenuContent = document.querySelector('.mobile_menu_content');
    const link = document.querySelector('.bottom_menu_button a');

    mobileMenuContent.style.display = (mobileMenuContent.style.display === 'none') ? 'block' : 'none';
    link.style.borderColor = (mobileMenuContent.style.display === 'block') ? '#49f625' : '#262626';
}

function changeTradeLink() {
    const inputValue = document.getElementById("profileSteamInput").value
    if (inputValue) {
        socket.emit('change_link', {"steamId": steamId, "trade_link": inputValue});
    }
}

function logout() {
    document.cookie = "steamId=";
    window.location.href = "/"
}

socket
    .on('connect', function (data) {
        socket.emit("profile", {"steamId": steamId});
    })
    .on('userProfile', function (data) {
        let userProfile = document.getElementById("userProfile");
        let userProfileID = document.getElementById("userProfileID");

        const userAvatar = document.createElement('div');
        userAvatar.className = 'user_avatar';
        userAvatar.style.backgroundImage = `url(${data.avatar_url})`;

        const userNickname = document.createElement('div');
        userNickname.className = 'user_nickname';
        userNickname.innerHTML = data.nickname;

        const userProfileIdValue = document.createElement('div');
        userProfileIdValue.className = 'user_profile_id_value';
        userProfileIdValue.innerHTML = data.steam_id;

        userProfile.insertBefore(userNickname, userProfile.firstChild);
        userProfile.insertBefore(userAvatar, userProfile.firstChild);

        userProfileID.appendChild(userProfileIdValue);

        document.getElementById("userSteamProfileLink").href = `https://steamcommunity.com/profiles/${data.steam_id}`;
        document.getElementById("profileSteamInput").value = data.trade_link;
        document.getElementById("participantsNum").innerHTML = data.participation_num;
        document.getElementById("winNum").innerHTML = data.max_win;
        document.getElementById("winRateNum").innerHTML = `${data.win_percent}%`;
        document.getElementById("bankSum").innerHTML = data.win_count;

        document.body.classList.remove("loading");
    })