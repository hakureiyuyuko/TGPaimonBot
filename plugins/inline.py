from typing import cast
from uuid import uuid4

from telegram import InlineQueryResultArticle, InputTextMessageContent, Update, InlineQuery
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import CallbackContext

from apps.wiki import WikiService
from logger import Log
from utils.apps.inject import inject


class Inline:
    """Inline模块"""

    @inject
    def __init__(self, wiki_service: WikiService):
        self.wiki_service = wiki_service

    async def inline_query(self, update: Update, _: CallbackContext) -> None:
        user = update.effective_user
        ilq = cast(InlineQuery, update.inline_query)
        query = ilq.query
        switch_pm_text = "需要帮助嘛？"
        results_list = []
        args = query.split(" ")
        if args[0] == "":
            pass
        else:
            if "查看武器列表并查询" == args[0]:
                weapons_list = await self.wiki_service.get_weapons_name_list()
                for weapons_name in weapons_list:
                    results_list.append(
                        InlineQueryResultArticle(
                            id=str(uuid4()),
                            title=weapons_name,
                            description=f"查看武器列表并查询 {weapons_name}",
                            input_message_content=InputTextMessageContent(f"武器查询{weapons_name}",
                                                                          parse_mode=ParseMode.MARKDOWN_V2)
                        ))
            elif "查看角色攻略列表并查询" == args[0]:
                characters_list = await self.wiki_service.get_characters_name_list()
                for role_name in characters_list:
                    results_list.append(
                        InlineQueryResultArticle(
                            id=str(uuid4()),
                            title=role_name,
                            description=f"查看角色攻略列表并查询 {role_name}",
                            input_message_content=InputTextMessageContent(f"角色攻略查询{role_name}",
                                                                          parse_mode=ParseMode.MARKDOWN_V2)
                        ))

        if len(results_list) == 0:
            results_list.append(
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title="好像找不到问题呢",
                    description="这个问题我也不知道，因为我就是个应急食品。",
                    input_message_content=InputTextMessageContent("这个问题我也不知道，因为我就是个应急食品。"),
                ))
        try:
            await ilq.answer(
                results=results_list,
                switch_pm_text=switch_pm_text,
                switch_pm_parameter="inline_message",
                cache_time=0,
                auto_pagination=True,
            )
        except BadRequest as exc:
            if "Query is too old" in exc.message:  # 过时请求全部忽略
                Log.warning(f"用户 {user.full_name}[{user.id}] inline_query请求过时")
                return
            if "can't parse entities" not in exc.message:
                raise exc
            Log.warning("inline_query发生BadRequest错误", exc_info=exc)
            await ilq.answer(
                results=[],
                switch_pm_text="糟糕，发生错误了。",
                switch_pm_parameter="inline_message",
            )