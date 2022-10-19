import httpx

from core.config import config


class PbClient:
    def __init__(self):
        self.client = httpx.AsyncClient()
        self.PB_API = config.error_pb_url
        self.sunset: int = config.error_pb_sunset  # 自动销毁时间 秒
        self.private: bool = True
        self.max_lines: int = config.error_pb_max_lines

    async def create_pb(self, content: str) -> str:
        if not self.PB_API:
            return ""
        content = "\n".join(content.splitlines()[-self.max_lines :]) + "\n"
        data = {
            "c": content,
        }
        if self.private:
            data["p"] = "1"
        if self.sunset:
            data["sunset"] = self.sunset
        data = await self.client.post(self.PB_API, data=data)  # 需要错误处理
        return data.headers["location"]