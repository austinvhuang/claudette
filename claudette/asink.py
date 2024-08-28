# AUTOGENERATED! DO NOT EDIT! File to edit: ../02_async.ipynb.

# %% auto 0
__all__ = ['AsyncClient', 'AsyncChat']

# %% ../02_async.ipynb
import inspect, typing, mimetypes, base64, json
from collections import abc
try: from IPython import display
except: display=None

from anthropic import AsyncAnthropic
from toolslm.funccall import get_schema
from fastcore.meta import delegates
from fastcore.utils import *
from .core import *

# %% ../02_async.ipynb
class AsyncClient(Client):
    def __init__(self, model, cli=None, log=False):
        "Async Anthropic messages client."
        super().__init__(model,cli,log)
        if not cli: self.c = AsyncAnthropic(default_headers={'anthropic-beta': 'prompt-caching-2024-07-31'})

# %% ../02_async.ipynb
@patch
async def _stream(self:AsyncClient, msgs:list, prefill='', **kwargs):
    async with self.c.messages.stream(model=self.model, messages=mk_msgs(msgs), **kwargs) as s:
        if prefill: yield prefill
        async for o in s.text_stream: yield o
        self._log(await s.get_final_message(), prefill, msgs, kwargs)

# %% ../02_async.ipynb
@patch
@delegates(Client)
async def __call__(self:AsyncClient,
             msgs:list, # List of messages in the dialog
             sp='', # The system prompt
             temp=0, # Temperature
             maxtok=4096, # Maximum tokens
             prefill='', # Optional prefill to pass to Claude as start of its response
             stream:bool=False, # Stream response?
             stop=None, # Stop sequence
             **kwargs):
    "Make an async call to Claude."
    msgs = self._precall(msgs, prefill, stop, kwargs)
    if stream: return self._stream(msgs, prefill=prefill, max_tokens=maxtok, system=sp, temperature=temp, **kwargs)
    res = await self.c.messages.create(
        model=self.model, messages=msgs, max_tokens=maxtok, system=sp, temperature=temp, **kwargs)
    return self._log(res, prefill, msgs, maxtok, sp, temp, stream=stream, stop=stop, **kwargs)

# %% ../02_async.ipynb
@delegates()
class AsyncChat(Chat):
    def __init__(self,
                 model:Optional[str]=None, # Model to use (leave empty if passing `cli`)
                 cli:Optional[Client]=None, # Client to use (leave empty if passing `model`)
                 **kwargs):
        "Anthropic async chat client."
        super().__init__(model, cli, **kwargs)
        if not cli: self.c = AsyncClient(model)

# %% ../02_async.ipynb
@patch
async def _stream(self:AsyncChat, res):
    async for o in res: yield o
    self.h += mk_toolres(self.c.result, ns=self.tools, obj=self)

# %% ../02_async.ipynb
@patch
async def _append_pr(self:AsyncChat, pr=None):
    prev_role = nested_idx(self.h, -1, 'role') if self.h else 'assistant' # First message should be 'user' if no history
    if pr and prev_role == 'user': await self()
    self._post_pr(pr, prev_role)