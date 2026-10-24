"""Conversations, including the cart, survive a restart (a new connection to the same file)."""

from langchain_core.messages import AIMessage, HumanMessage

from kapruka_agent.agent import build_agent
from kapruka_agent.agent.persistence import open_checkpointer
from kapruka_agent.agent.tools import build_tools
from kapruka_agent.kapruka.models import Money
from kapruka_agent.kapruka.orders import Cart, CartItem

from .test_events import ScriptedChatModel


async def test_cart_is_still_there_after_restart(tmp_path, fake_kapruka):
    db = tmp_path / "conversations.sqlite"
    config = {"configurable": {"thread_id": "thread-persist"}}
    cart = Cart().with_item(CartItem(product_id="CAKE1", name="Cake", price=Money(amount=5950)))

    async with open_checkpointer(db) as saver:
        agent = build_agent(
            ScriptedChatModel(replies=iter([AIMessage("hi")])), build_tools(fake_kapruka), saver
        )
        await agent.ainvoke({"messages": [HumanMessage("hello")], "cart": cart}, config)

    # "Restart": a brand-new connection and graph reading the same file.
    async with open_checkpointer(db) as saver:
        agent = build_agent(ScriptedChatModel(replies=iter([])), build_tools(fake_kapruka), saver)
        state = (await agent.aget_state(config)).values

    assert state["cart"].items[0].name == "Cake"
    assert state["messages"][-1].content == "hi"
