import asyncio
import json
import logging
from typing import AsyncGenerator
from crewai import Crew, Process

from src.agents.crew.agents import (
    create_router_agent,
    create_scraper_agent,
    create_insight_agent,
    get_llm,
)
from src.agents.crew.tasks import (
    create_intent_task,
    create_scrape_task,
    create_insight_task,
)

from src.database.supabase_db import supabase_db

logger = logging.getLogger(__name__)


class HierarchicalMarketCrew:
    """Đội ngũ Đa tác tử Phản biện (Hierarchical Crew) phân tích thị trường với khả năng Streaming."""

    def __init__(self, query: str):
        self.query = query
        self.queue: asyncio.Queue = asyncio.Queue()

    def _step_callback(self, step_output):
        """Callback được gọi sau mỗi bước suy luận hoặc hành động của Agent."""
        try:
            agent_name = getattr(step_output, "agent", "CrewAgent")
            thought = getattr(step_output, "thought", str(step_output))
            message = {
                "type": "agent_step",
                "agent": str(agent_name),
                "thought": str(thought)[:300],
            }
            # Put message into event loop queue
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.call_soon_threadsafe(self.queue.put_nowait, message)
            except Exception as e:
                logger.warning(f"Could not queue step callback message: {e}")
        except Exception as e:
            logger.error(f"Error in step callback: {e}")

    def run_crew_sync(self) -> str:
        """Chạy Crew trong thread riêng."""
        router = create_router_agent()
        scraper = create_scraper_agent()
        insight = create_insight_agent()

        t1 = create_intent_task(router, self.query)
        t2 = create_scrape_task(scraper)
        t3 = create_insight_task(insight)

        manager_llm = get_llm()

        crew = Crew(
            agents=[router, scraper, insight],
            tasks=[t1, t2, t3],
            process=Process.hierarchical,
            manager_llm=manager_llm,
            verbose=True,
            step_callback=self._step_callback,
        )

        result = crew.kickoff()
        return str(result)

    async def stream_analysis(self, user_id: str = "anonymous") -> AsyncGenerator[str, None]:
        """Stream tiến trình suy luận và kết quả phân tích của Crew về cho client."""
        # Thông báo bắt đầu
        yield f"data: {json.dumps({'type': 'status', 'content': f'Kích hoạt CrewAI cho câu hỏi: {self.query}'})}\n\n"

        loop = asyncio.get_running_loop()

        # Execute kickoff in thread pool to prevent blocking asyncio loop
        future = loop.run_in_executor(None, self.run_crew_sync)

        # Stream messages from queue while crew is running
        while not future.done():
            while not self.queue.empty():
                msg = await self.queue.get()
                yield f"data: {json.dumps(msg)}\n\n"
            await asyncio.sleep(0.5)

        # Flush any remaining messages
        while not self.queue.empty():
            msg = await self.queue.get()
            yield f"data: {json.dumps(msg)}\n\n"

        try:
            final_result = await future
            parsed_result = {"raw_result": final_result}
            try:
                parsed_result = json.loads(final_result)
            except Exception:
                pass

            # Save session log asynchronously to Supabase
            try:
                await supabase_db.save_session_log(
                    user_id=user_id,
                    prompt=self.query,
                    results=parsed_result,
                    status="success",
                    source_links=[]
                )
            except Exception as se:
                logger.error(f"Failed to save session log to Supabase: {se}")

            yield f"data: {json.dumps({'type': 'final_result', 'content': final_result})}\n\n"
        except Exception as e:
            logger.error(f"Lỗi khi thực thi Hierarchical Crew: {e}")

            # Save failed session log
            try:
                await supabase_db.save_session_log(
                    user_id=user_id,
                    prompt=self.query,
                    results={"error": str(e)},
                    status="error",
                    source_links=[]
                )
            except Exception:
                pass

            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

