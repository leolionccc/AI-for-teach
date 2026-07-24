from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.schemas.agent import AgentCreateRequest, AgentUpdateRequest


def list_agents(db: Session) -> List[Agent]:
    return db.query(Agent).order_by(Agent.id.desc()).all()


def get_agent_by_id(db: Session, agent_id: int) -> Optional[Agent]:
    return db.query(Agent).filter(Agent.id == agent_id).first()


def create_agent(
    db: Session,
    request: AgentCreateRequest,
    user_id: int,
) -> Agent:
    agent = Agent(
        name=request.name,
        description=request.description,
        system_prompt=request.system_prompt,
        welcome_message=request.welcome_message,
        avatar=request.avatar,
        is_enabled=request.is_enabled,
        created_by=user_id,
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return agent


def update_agent(
    db: Session,
    agent: Agent,
    request: AgentUpdateRequest,
) -> Agent:
    update_data = request.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(agent, key, value)

    db.commit()
    db.refresh(agent)

    return agent


def delete_agent(db: Session, agent: Agent) -> None:
    db.delete(agent)
    db.commit()