from langchain.agents import create_agent
from model.factory import chat_model
from utils.prompt_loader import load_system_prompts
from agent.tools.agent_tools import (
    rag_summarize,
    get_weather,
    get_user_location,
    get_user_id,
    get_current_month,
    fetch_external_data,
    fill_context_for_report,
)
from agent.tools.middleware import monitor_tool, log_before_model, report_prompt_switch
from utils.logger_handler import logger
from utils.config_handler import agent_conf
import subprocess


class ReactAgent:
    def __init__(self):
        self.agent = create_agent(
            model=chat_model,
            system_prompt=load_system_prompts(),
            tools=[
                rag_summarize,
                get_weather,
                get_user_location,
                get_user_id,
                get_current_month,
                fetch_external_data,
                fill_context_for_report,
            ],
            middleware=[monitor_tool, log_before_model, report_prompt_switch],
        )

    def execute_stream(self, query: str):
        input_dict = {
            "messages": [
                {"role": "user", "content": query},
            ]
        }

        # 第三个参数context就是上下文runtime中的信息，就是我们做提示词切换的标记
        try:
            for chunk in self.agent.stream(
                input_dict, stream_mode="values", context={"report": False}
            ):
                latest_message = chunk["messages"][-1]
                if latest_message.content:
                    yield latest_message.content.strip() + "\n"
        except Exception as e:
            # 记录详细错误，向前端返回可读提示并安全结束流
            logger.exception("模型流式调用出错")
            msg = str(e)
            if "Arrearage" in msg or "Access denied" in msg or "overdue-payment" in msg:
                user_msg = (
                    "模型调用被拒：账户可能欠费或无权限。请检查模型服务（例如阿里云Model Studio）的账单与配额，"
                    "或切换到本地模型/其他云模型后重试。"
                )
            else:
                user_msg = "模型调用出错：%s" % (
                    msg if len(msg) < 300 else msg[:300] + "..."
                )

            # 尝试回退到本地 Ollama（如果可用）
            try:
                ollama_model = agent_conf.get("ollama_model", "")  # 从配置中读取模型名
                prompt = query
                ollama_resp = None
                # 使用 ollama CLI 调用（需要本机已安装并在 PATH）
                cmd = ["ollama", "run"]
                if ollama_model:
                    cmd.append(ollama_model)
                cmd.extend(["--quiet", "--prompt", prompt])
                logger.info(f"尝试调用本地 Ollama: {' '.join(cmd[:3])} ...")
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                if proc.returncode == 0 and proc.stdout:
                    ollama_resp = proc.stdout.strip()
                elif proc.returncode == 0 and proc.stderr:
                    ollama_resp = proc.stderr.strip()
                else:
                    logger.warning(
                        "Ollama 调用未返回内容或返回非零退出码: %s %s",
                        proc.returncode,
                        proc.stderr,
                    )

                if ollama_resp:
                    yield "(已回退到本地 Ollama 模型)\n"
                    yield ollama_resp + "\n"
                    return
            except FileNotFoundError:
                logger.info("本地 Ollama CLI 未安装或不在 PATH，跳过回退")
            except Exception:
                logger.exception("尝试调用本地 Ollama 时出错，回退失败")

            yield user_msg + "\n"
            return


if __name__ == "__main__":
    agent = ReactAgent()

    for chunk in agent.execute_stream("给我生成我的使用报告"):
        print(chunk, end="", flush=True)
