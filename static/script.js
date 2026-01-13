const weatherMaster = {
    "1": { name: "晴れ", emoji: "☀️" }, "2": { name: "曇り", emoji: "☁️" },
    "3": { name: "雨", emoji: "☔" }, "4": { name: "雪", emoji: "❄️" }
};

async function init() {
    const res = await fetch('/api/areas');
    const data = await res.json();
    const select = document.getElementById('areaSelect');
    data.areas.forEach(a => {
        const opt = document.createElement('option');
        opt.value = a.code; opt.textContent = a.name;
        select.appendChild(opt);
    });
}

async function fetchWeather(code) {
    if(!code) return;
    const resArea = document.getElementById('weatherResult');
    resArea.innerHTML = '<div class="loader"></div>';
    
    const res = await fetch(`/api/weather/${code}`);
    const data = await res.json();
    
    if(!data.forecasts || data.forecasts.length === 0) {
        resArea.innerHTML = "お天気が見つからなかったよ";
        return;
    }

    let html = '';
    data.forecasts.forEach(fc => {
        const firstDigit = fc.weather_code ? fc.weather_code.substring(0, 1) : "0";
        const info = weatherMaster[firstDigit] || { name: "予報中", emoji: "✨" };
        const dateObj = new Date(fc.date);
        const dayName = ['日','月','火','水','木','金','土'][dateObj.getDay()];

        html += `
            <div class="day-card" onclick="this.classList.toggle('active')">
                <div class="day-summary">
                    <div class="date-box">${dateObj.getMonth()+1}/${dateObj.getDate()}<span>(${dayName})</span></div>
                    <div class="emoji-box">${info.emoji}</div>
                    <div class="temp-box">
                        <span class="high">${fc.temp_max||'--'}°</span> / <span class="low">${fc.temp_min||'--'}°</span>
                    </div>
                </div>
                <div class="details">
                    <div class="info-pill"><span>かぜ</span>${fc.wind}</div>
                    <div class="info-pill"><span>あめ</span>${fc.pop}%</div>
                </div>
            </div>`;
    });
    resArea.innerHTML = html;
}

document.getElementById('areaSelect').addEventListener('change', (e) => fetchWeather(e.target.value));
init();