import asyncio
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from pydantic import SecretStr
from browser_use import Agent, Browser, BrowserConfig
load_dotenv()

apiKey = os.getenv('DEEPSEEK_API_KEY')
# Initialize the model
llm = ChatOpenAI(base_url='https://api.deepseek.com/v1', model='deepseek-chat',
                 api_key=SecretStr(apiKey))

# Configure the browser to connect to your Chrome instance
browser = Browser(
    config=BrowserConfig(chrome_instance_path="C:\Program Files\Google\Chrome\Application\chrome.exe",
                         disable_security=True,
                         ))


async def main():
    agent = Agent(
        task="Open the browser enter this link https://www.zhipin.com then in the website link search the term '大型语言模型实习' then collect 5 internship post, summary skills demands and each position salary",
        llm=llm,
        browser=browser,
        use_vision=False
    )
    result = await agent.run()
    print(result)
    input('Press Enter to close the browser...')
    await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
