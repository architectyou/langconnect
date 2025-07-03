from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from openai import AsyncOpenAI
from datetime import datetime

# vLLM OpenAI compatible API 클라이언트 설정
client = AsyncOpenAI(
    base_url="https://chatbot.kcsoftmax.com/llm_2/v1",  # vLLM 서버 주소
    api_key="my-api-key"  # vLLM에서는 실제 API 키가 필요하지 않음
)

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="python",  # Executable
    args=["test_server_1.py"],  # Optional command line arguments
    env=None,  # Optional environment variables
)


# Optional: create a sampling callback
async def handle_sampling_message(
    message: types.CreateMessageRequestParams,
) -> types.CreateMessageResult:
    try:
        # vLLM 서버에 실제 요청 보내기
        response = await client.chat.completions.create(
            model="/home/chatbot/llm-chatbot/models/Qwen3-32B-AWQ",
            messages=[{"role": "user", "content": str(message.messages)}],
            max_tokens=512,
            temperature=0.7
        )
        
        response_text = response.choices[0].message.content
        
        return types.CreateMessageResult(
            role="assistant",
            content=types.TextContent(
                type="text",
                text=response_text,
            ),
            model="/home/chatbot/llm-chatbot/models/Qwen3-32B-AWQ",
            stopReason="endTurn",
        )
    except Exception as e:
        # 오류 발생 시 기본 응답
        return types.CreateMessageResult(
            role="assistant",
            content=types.TextContent(
                type="text",
                text=f"Error: {str(e)}",
            ),
            model="/home/chatbot/llm-chatbot/models/Qwen3-32B-AWQ",
            stopReason="endTurn",
        )


async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read, write, sampling_callback=handle_sampling_message
        ) as session:
            # Initialize the connection
            await session.initialize()
            print("서버 연결 완료!")

            # List available tools
            tools = await session.list_tools()
            print("\n사용 가능한 도구:", tools)

            # 날씨 정보 확인
            weather_seoul = await session.call_tool("get_weather", arguments={"city": "서울"})
            print("\n서울 날씨:", weather_seoul)
            
            weather_jeju = await session.call_tool("get_weather", arguments={"city": "제주"})
            print("제주 날씨:", weather_jeju)

            # 일정 추가
            today = datetime.now().strftime("%Y-%m-%d")
            add_result = await session.call_tool(
                "add_schedule", 
                arguments={
                    "date": today,
                    "event": "오후 3시 - 팀 미팅"
                }
            )
            print("\n일정 추가:", add_result)

            add_result2 = await session.call_tool(
                "add_schedule", 
                arguments={
                    "date": today,
                    "event": "오후 6시 - 저녁 약속"
                }
            )
            print("일정 추가:", add_result2)

            # 일정 조회
            schedule = await session.call_tool("get_schedule", arguments={"date": today})
            print("\n일정 조회:", schedule)

            # 일일 요약 리소스 조회
            content, mime_type = await session.read_resource(f"file://summary/{today}")
            print("\n일일 요약:")
            print(content)


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())