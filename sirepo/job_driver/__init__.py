# -*- coding: utf-8 -*-
"""Base for drivers

:copyright: Copyright (c) 2019 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
from __future__ import absolute_import, division, print_function
from pykern import pkconfig, pkio, pkinspect, pkcollections, pkconfig, pkjson
from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdp, pkdlog, pkdc, pkdexc
from sirepo import job
import collections
import importlib
import tornado.gen
import tornado.ioloop
import tornado.locks

cfg = None

KILL_TIMEOUT_SECS = 3

#: map of driver names to class
_CLASSES = None

#: default class when not determined by request
_DEFAULT_CLASS = None

class AgentMsg(PKDict):

    async def receive(self):
        # Agent messages do not block the supervisor
        DriverBase.receive(self)


class DriverBase(PKDict):
    agents = PKDict()

    def __init__(self, req):
        super().__init__(
            has_slot=False,
            ops_pending_done=PKDict(),
            ops_pending_send=[],
            uid=req.content.uid,
            websocket=None,
            _agentId=job.unique_key(),
            _kind=req.kind,
            _supervisor_uri=cfg.supervisor_uri,
        )
        self.agents[self._agentId] = self

    def cancel_op(self, op):
        for o in self.ops_pending_send:
            if o == op:
                self.ops_pending_send.remove(o)
        for o in self.ops_pending_done.copy().values():
            if o == op:
                del self.ops_pending_done[o.opId]

    def destroy_op(self, op):
        assert op not in self.ops_pending_send
        # canceled ops are removed in self.cancel_op()
        if not op.canceled and not op.errored:
            del self.ops_pending_done[op.opId]
        self.run_scheduler(self._kind)

    @classmethod
    def free_slots(cls, kind):
        for d in cls.instances[kind]:
            if d.has_slot and not d.ops_pending_done:
                cls.slots[kind].in_use -= 1
                d.has_slot = False
        assert cls.slots[kind].in_use > -1

    def get_ops_pending_done_types(self):
            d = collections.defaultdict(int)
            for v in self.ops_pending_done.values():
                d[v.msg.opName] += 1
            return d

    def get_ops_with_send_allocation(self):
        """Get ops that could be sent assuming outside requirements are met.

        Outside requirements are an alive websocket connection and the driver
        having a slot.
        """
        r = []
        t = self.get_ops_pending_done_types()
        for o in self.ops_pending_send:
            if (o.msg.opName in t
                and t[o.msg.opName] > 0
            ):
                continue
            assert o.opId not in self.ops_pending_done
            t[o.msg.opName] += 1
            r.append(o)
        return r

    @classmethod
    def init_class(cls, cfg):
        for k in job.KINDS:
            cls.slots[k] = PKDict(
                in_use=0,
                total=cfg[k + '_slots'],
            )
            cls.instances[k] = []
        return cls

    @classmethod
    def receive(cls, msg):
        try:
            cls.agents[msg.content.agentId]._receive(msg)
        except KeyError as e:
            pkdc('unknown agent msg={}', msg)
            try:
                msg.handler.write_message(PKDict(opName=job.OP_KILL))
            except Exception as e:
                pkdlog('error={} stack={}', e, pkdexc())


# TODO(e-carlin): Take in a arg of driver and start the loop from the index
# of that driver. Doing so enables fair scheduling. Otherwise user at start of
# list always has priority
    @classmethod
    def run_scheduler(cls, kind):
        cls.free_slots(kind)
        for d in cls.instances[kind]:
            ops_with_send_alloc = d.get_ops_with_send_allocation()
            if not ops_with_send_alloc:
                continue
            if ((not d.has_slot and cls.slots[kind].in_use >= cls.slots[kind].total)
                or not d.websocket
            ):
                continue
            if not d.has_slot:
                assert cls.slots[kind].in_use < cls.slots[kind].total
                d.has_slot = True
                cls.slots[kind].in_use += 1
            for o in ops_with_send_alloc:
                assert o.opId not in d.ops_pending_done
                d.ops_pending_send.remove(o)
                d.ops_pending_done[o.opId] = o
                o.send_ready.set()

    async def send(self, op):
#TODO(robnagler) need to send a retry to the ops, which should requeue
#  themselves at an outer level(?).
#  If a job is still running, but we just lost the websocket, want to
#  pickup where we left off. If the op already was written, then you
#  have to ask the agent. If ops are idempotent, we can simply
#  resend the request. If it is in process, then it will be reconnected
#  to the job. If it was already completed (and reply on the way), then
#  we can cache that state in the agent(?) and have it send the response
#  twice(?).
        self.ops_pending_send.append(op)
        self.run_scheduler(self._kind)
        await op.send_ready.wait()
        if op.opId in self.ops_pending_done:
            self.websocket.write_message(pkjson.dump_bytes(op.msg))
        else:
            pkdlog('canceled op={}', job.LogFormatter(op))
        assert op not in self.ops_pending_send

    @classmethod
    def terminate(cls):
        for d in DriverBase.agents.values():
            d.kill()

    def websocket_on_close(self):
       self._websocket_free()

    def _free(self):
        self._websocket_free()

    def _receive(self, msg):
        c = msg.content
        i = c.get('opId')
        if i:
            self.ops_pending_done[i].reply_put(c.reply)
        else:
            getattr(self, '_receive_' + c.opName)(msg)

    def _receive_alive(self, msg):
        """Receive an ALIVE message from our agent

        Save the websocket and register self with the websocket
        """
        if self.websocket:
            if self.websocket == msg.handler:
                return
            self._websocket_free()
        self.websocket = msg.handler
        self.websocket.sr_driver_set(self)
        self.run_scheduler(self._kind)

    def _websocket_free(self):
        """Remove holds on all resources and remove self from data structures"""
        del self.agents[self._agentId]
        for d in self.instances[self._kind]:
            if d.uid == self.uid:
                self.instances[self._kind].remove(d)
                break
        else:
            raise AssertionError(
                'kind={}  uid={} not in instances={}'.format(
                    self._kind,
                    self.uid,
                    self.instances
                )
            )
        if self.has_slot:
            self.slots[self._kind].in_use -= 1
            self.has_slot = False
        w = self.websocket
        self.websockt = None
        if w:
            # Will not call websocket_on_close()
            w.sr_close()
        t = list(
            self.ops_pending_done.values()
            )
        t.extend(self.ops_pending_send)
        self.ops_pending_done.clear()
        self.ops_pending_send = []
        for o in t:
            o.set_errored('websocket closed')
        self.run_scheduler(self._kind)


async def get_instance(req):
    # TODO(e-carlin): parse req to get class
    return await _DEFAULT_CLASS.get_instance(req)


def init():
    global cfg
    cfg = pkconfig.init(
        modules=(None, _cfg_parse_modules, 'driver modules'),
        supervisor_uri=(
            'ws://{}:{}{}'.format(job.DEFAULT_IP, job.DEFAULT_PORT, job.AGENT_URI),
            str,
            'uri for agent ws connection with supervisor',
        ),
    )


@pkconfig.parse_none
def _cfg_parse_modules(value):
    global _CLASSES, _DEFAULT_CLASS
    assert not _CLASSES

    s = pkconfig.parse_set(value)
    if not s:
        s = frozenset(('docker',))
        if pkconfig.channel_in('dev'):
            s = frozenset(('local',))
    assert not {'local', 'docker'}.issubset(s), \
        'modules={} can only contain one of "docker" or "local"'.format(s)
    assert 'docker' in s or 'local' in s, \
        'modules={} must contain  "docker" or "local"'.format(s)
    p = pkinspect.this_module().__name__
    _CLASSES = PKDict()
    for n in s:
        m = importlib.import_module(pkinspect.module_name_join((p, n)))
        _CLASSES[n] = m.init_class()
    if 'docker' in s:
        _DEFAULT_CLASS = _CLASSES['docker']
    else:
        _DEFAULT_CLASS = _CLASSES['local']
    return s

def terminate():
    DriverBase.terminate()