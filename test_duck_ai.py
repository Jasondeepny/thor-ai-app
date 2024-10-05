import pytest
import asyncio
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from duck_ai import init_chat, Chat, ModelAlias

@pytest.fixture
async def mock_session():
    with patch('aiohttp.ClientSession') as mock:
        yield mock


# @pytest_asyncio.fixture
async def test_init_chat(mock_session):
    mock_response = AsyncMock()
    mock_response.headers = {'x-vqd-4': 'test_vqd'}
    mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response

    chat = await init_chat('gpt-4o-mini')
    print(chat)

    assert isinstance(chat, Chat)
    assert chat.old_vqd == 'test_vqd'
    assert chat.new_vqd == 'test_vqd1'
    assert chat.model == 'gpt-4o-mini'


# @pytest_asyncio.fixture
# async def test_chat_fetch_full():
    # chat = Chat('test_vqd', 'gpt-4o-mini')
    # chat = await init_chat('gpt-4o-mini')
    # print(chat)
    # mock_response = AsyncMock()
    # mock_response.ok = True
    # mock_response.content.__aiter__.return_value = [
    #     b'data: {"message": "Hello"}',
    #     b'data: {"message": " World"}',
    #     b'data: {}'
    # ]
    # mock_response.headers = {'x-vqd-4': 'new_test_vqd'}

    # mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response

    # result = await chat.fetch_full('Hello')

    # assert result == 'Hello World'
    # assert chat.new_vqd == 'new_test_vqd'
    # assert chat.messages == [
    #     {'content': 'Test message', 'role': 'user'},
    #     {'content': 'Hello World', 'role': 'assistant'}
    # ]
    # print(result)


# @pytest_asyncio.fixture
# async def test_chat_fetch_stream(mock_session):
#     chat = Chat('test_vqd', 'gpt-4o-mini')
#     mock_response = AsyncMock()
#     mock_response.ok = True
#     mock_response.content.__aiter__.return_value = [
#         b'data: {"message": "Hello"}',
#         b'data: {"message": " World"}',
#         b'data: {}'
#     ]
#     mock_response.headers = {'x-vqd-4': 'new_test_vqd'}
    
#     mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response

#     chunks = []
#     async for chunk in chat.fetch_stream('Test message'):
#         chunks.append(chunk)

#     assert chunks == ['Hello', ' World']
#     assert chat.new_vqd == 'new_test_vqd'
#     assert chat.messages == [
#         {'content': 'Test message', 'role': 'user'},
#         {'content': 'Hello World', 'role': 'assistant'}
#     ]

# def test_chat_redo():
#     chat = Chat('test_vqd', 'gpt-4o-mini')
#     chat.messages = [
#         {'content': 'Message 1', 'role': 'user'},
#         {'content': 'Response 1', 'role': 'assistant'},
#         {'content': 'Message 2', 'role': 'user'},
#         {'content': 'Response 2', 'role': 'assistant'}
#     ]
#     chat.new_vqd = 'new_test_vqd'

#     chat.redo()

#     assert chat.new_vqd == 'test_vqd'
#     assert chat.messages == [
#         {'content': 'Message 1', 'role': 'user'},
#         {'content': 'Response 1', 'role': 'assistant'}
#     ]
