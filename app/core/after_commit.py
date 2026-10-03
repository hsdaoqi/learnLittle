"""Dispatch side effects only after the owning SQL transaction commits."""

from sqlalchemy import event
from sqlalchemy.orm import Session

from app.core.task_runner import spawn_background_task


def defer_after_commit(session, key, factory):
    session.info.setdefault("after_commit_jobs", {})[key] = factory


@event.listens_for(Session, "after_commit")
def _committed(session):
    for key, factory in session.info.pop("after_commit_jobs", {}).items():
        spawn_background_task(factory, key=key)


@event.listens_for(Session, "after_rollback")
def _rolled_back(session):
    session.info.pop("after_commit_jobs", None)
