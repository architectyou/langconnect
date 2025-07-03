from mcp.server.fastmcp import FastMCP
from datetime import datetime
import random

mcp = FastMCP(name="personal_assistant", version="0.1.0")

# 날씨 정보를 위한 가상 데이터
WEATHER_DATA = {
    "서울": {"맑음": 25, "흐림": 22, "비": 20},
    "부산": {"맑음": 27, "흐림": 24, "비": 22},
    "제주": {"맑음": 26, "흐림": 23, "비": 21}
}

# 일정 저장을 위한 가상 데이터베이스
SCHEDULE_DB = []

@mcp.tool()
def get_weather(city: str) -> str:
    """도시의 현재 날씨 정보를 반환합니다."""
    if city not in WEATHER_DATA:
        return f"죄송합니다. {city}의 날씨 정보를 찾을 수 없습니다."
    
    weather = random.choice(list(WEATHER_DATA[city].keys()))
    temp = WEATHER_DATA[city][weather]
    return f"{city}의 현재 날씨는 {weather}이며, 기온은 {temp}도입니다."

@mcp.tool()
def add_schedule(date: str, event: str) -> str:
    """새로운 일정을 추가합니다."""
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        SCHEDULE_DB.append({"date": date, "event": event})
        return f"일정이 추가되었습니다: {date}에 {event}"
    except ValueError:
        return "날짜 형식이 잘못되었습니다. YYYY-MM-DD 형식으로 입력해주세요."

@mcp.tool()
def get_schedule(date: str) -> str:
    """특정 날짜의 일정을 조회합니다."""
    events = [s["event"] for s in SCHEDULE_DB if s["date"] == date]
    if not events:
        return f"{date}에 예정된 일정이 없습니다."
    return f"{date}의 일정:\n" + "\n".join(f"- {event}" for event in events)

@mcp.resource("file://summary/{date}")
def get_daily_summary(date: str) -> str:
    """특정 날짜의 일정과 날씨 정보를 종합적으로 제공합니다."""
    schedule = get_schedule(date)
    weather = get_weather("서울")  # 기본값으로 서울 날씨 제공
    
    return f"[일일 요약 - {date}]\n\n" \
           f"🌤 날씨 정보:\n{weather}\n\n" \
           f"📅 일정 정보:\n{schedule}"

@mcp.resource("greeting://{name}")
def get_greeting(name : str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

@mcp.prompt("greeting")
def get_greeting_prompt(name : str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!!"

if __name__ == "__main__":
    mcp.run()