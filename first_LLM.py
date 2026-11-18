from openai import OpenAI, OpenAIError
import os,json
#chat_history.json文件将保存聊天记录，确保在同一目录下运行此脚本

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "chat_history.json")
total_input_tokens, total_output_tokens, total_tokens = 0, 0, 0
client = None
MAX_TURNS = 5

def get_history():
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                        return json.load(f)
            except json.JSONDecodeError:
                print("聊天记录文件读取错误，将创建新的聊天记录。")
        messages=[
            {"role": "system", "content": "你是一个AI助手，使用中文回答问题，但你要假装自己是一条会说话的大鲸鱼。"}
        ]
        save_history(messages)
        return messages

def save_history(messages):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(messages, f, ensure_ascii=False, indent=4)

def ask_ai(messages,question):
        messages[:] = trim_history(messages)
        response = client.chat.completions.create(
            model="deepseek-flash",
            messages=messages + [
                {"role": "user", "content": question}
            ],
            stream=True,
            stream_options={"include_usage": True}
        )
        answer = ""
        print("AI：", end="", flush=True)
        for chunk in response:
            if chunk.choices:
                content = chunk.choices[0].delta.content
                if content:
                    print(content, end="", flush=True)
                    answer += content
            if chunk.usage:
                print(f"\n本次请求输入Token数: {chunk.usage.prompt_tokens}")
                print(f"本次请求输出Token数: {chunk.usage.completion_tokens}")
                print(f"本次请求总Token数: {chunk.usage.total_tokens}")
                global total_input_tokens, total_output_tokens, total_tokens
                total_input_tokens += chunk.usage.prompt_tokens
                total_output_tokens += chunk.usage.completion_tokens
                total_tokens += chunk.usage.total_tokens
        messages.append({"role": "user", "content": question})
        messages.append({"role": "assistant", "content": answer})
        save_history(messages)
        return answer

def trim_history(messages, max_turns=MAX_TURNS):
       if len(messages) > MAX_TURNS * 2 + 1:
                system_message = messages[0]
                history = messages[1:]
                history = history[-max_turns * 2:]
                return [system_message] + history

def main():
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
                raise SystemExit("未设置 DEEPSEEK_API_KEY 环境变量")
        global client
        client = OpenAI(api_key=api_key,base_url="https://api.deepseek.com")
        print("测试Deepseek API。输入'exit'以结束。保存上下文。")
        messages = get_history()
        while True:
                question = input("请输入你的问题: ")
                if question.strip().lower() == "exit":
                        print("退出程序。")
                        break
                elif not question.strip():
                        print("问题不能为空，请重新输入。")
                        continue
                try:
                        ask_ai(messages, question)
                except OpenAIError as e:
                        print(f"发生错误: {e}")
if __name__ == "__main__":
        main()                        