# server.py
import json
import asyncio
from mcp.server.fastmcp import FastMCP

# Create FastMCP server with custom port
mcp = FastMCP("example-server", port=6277)

# Add a simple tool for demonstration (optional)
@mcp.tool()
def hello(name: str) -> str:
    """Say hello to someone"""
    return f"Hello {name}!"


@mcp.tool()
def get_weather(city: str)  -> str:
    """获取指定城市的天气信息，当用户输入中文城市时，把中文城市换成接口可以识别的拼音，例如：北京 -> beijing"""
    # api_key = "992************704"
    # url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=no"

    # response = requests.get(url)
    # if response.status_code == 200:
    #     data = response.json()
    #     # print(json.dumps(data, indent=2, ensure_ascii=False))
        
    #     # 获取当前日期
    #     today = datetime.datetime.now()
    #     date_str = today.strftime("%Y年%m月%d日")
        
    #     weather_info = {
    #         "date": date_str,
    #         "location": data["location"]["name"],
    #         "temperature": data["current"]["temp_c"],
    #         "condition": data["current"]["condition"]["text"].lower(),
    #         "localtime": data["location"]["localtime"]
    #     }        
    
    weather_info = {
            "date": "12",
            "location": "123",
            "temperature": 11,
            "condition": "111",
            "localtime": "111"
        }        
            
    # return weather_info
    return json.dumps(weather_info, indent=2, ensure_ascii=False)
    # else:
    #     return {"error": "无法获取天气信息"}

@mcp.tool()
def say_hello(name: str) -> str:
    """生成个性化问候语（中英双语版）"""
    return f"  你好 {name}! (Hello {name}!)"

async def main():
    # Run the server with streamable-http transport
    # This will start an HTTP server on 0.0.0.0:6277
    print(f"Server running on http://0.0.0.0:6277")
    
    # 介绍下该方法：该方法用于启动一个基于流式HTTP的MCP服务器，允许客户端通过HTTP协议与服务器进行交互。
    await mcp.run_streamable_http_async() 
    
    

if __name__ == "__main__":
    asyncio.run(main()) # 外面包一层 asyncio.run，实现异步运行
