# Define the InventoryItem model
from datetime import datetime
from typing import List
import pandas as pd
from sqlmodel import Field, SQLModel, Session, desc, select
from enum import StrEnum


class ItemType(StrEnum):
    milch = "Milch"
    apfelsaft = "Apfelsaft"
    salami = "Salami"
    schnaps = "Schnaps"
    sonstiges = "Sonstiges"


class InventoryItem(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    date: datetime
    item: ItemType
    quantity: float


def add_item(session: Session, item: InventoryItem):
    session.add(item)
    session.commit()


def get_last_n_items_of_inventory(session: Session, n: int = 10) -> List[InventoryItem]:
    # Query the database to get all items in the inventory
    statement = (
        select(InventoryItem)
        .order_by(desc(InventoryItem.date), desc(InventoryItem.id))
        .limit(n)
    )
    inventory = session.exec(statement)
    return list(inventory.all())


def sqlmodel_to_df(objs: List[SQLModel]) -> pd.DataFrame:
    """Convert a SQLModel objects into a pandas DataFrame."""
    records = [i.model_dump() for i in objs]
    df = pd.DataFrame.from_records(records)
    return df


def get_item_by_id(session: Session, id: int) -> InventoryItem:
    statement = select(InventoryItem).where(InventoryItem.id == id)
    results = session.exec(statement)
    return results.one()


def get_items_by_date(session: Session, date: datetime) -> List[InventoryItem]:
    statement = select(InventoryItem).where(InventoryItem.date == date)
    results = session.exec(statement)
    return list(results.all())


def get_last_n_items_starting_from_id(
    session: Session, id: int, n: int = 10
) -> List[InventoryItem]:
    statement = (
        select(InventoryItem)
        .where(InventoryItem.id >= id)
        .order_by(desc(InventoryItem.date), desc(InventoryItem.id))
        .limit(n)
    )
    results = session.exec(statement)
    return list(results.all())


def delete_item(session: Session, id: int) -> None:
    item = get_item_by_id(session, id)
    session.delete(item)
    session.commit()
