import pytest
from sqlmodel import SQLModel, Session, create_engine
from datetime import datetime
from naturalien.inventory import (
    InventoryItem,
    get_last_n_items_of_inventory,
    sqlmodel_to_df,
)


@pytest.fixture
def session():
    # Create an in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    session = Session(engine)

    # Create some sample inventory items
    items = [
        InventoryItem(item="Milch", quantity=1.5),
        InventoryItem(item="Apfelsaft", quantity=2.0),
        InventoryItem(item="Salami", quantity=0.5),
        InventoryItem(item="Schnaps", quantity=0.2),
    ]
    session.add_all(items)
    session.commit()

    yield session

    # Clean up the database after testing
    InventoryItem.__table__.drop(engine)


def test_get_last_n_items_of_inventory(session):
    # Test with n=2
    items = get_last_n_items_of_inventory(session, n=2)
    assert len(items) == 2
    assert items[0].item == "Schnaps"
    assert items[0].quantity == 0.2
    assert items[1].item == "Salami"
    assert items[1].quantity == 0.5

    # Test with n=3
    items = get_last_n_items_of_inventory(session, n=3)
    assert len(items) == 3
    assert items[0].item == "Schnaps"
    assert items[0].quantity == 0.2
    assert items[1].item == "Salami"
    assert items[1].quantity == 0.5
    assert items[2].item == "Apfelsaft"
    assert items[2].quantity == 2.0


def test_sqlmodel_to_df():
    # Create some sample inventory items
    date = datetime.now()
    items = [
        InventoryItem(item="Milch", quantity=1.5, date=date),
        InventoryItem(item="Apfelsaft", quantity=2.0, date=date),
        InventoryItem(item="Salami", quantity=0.5, date=date),
        InventoryItem(item="Schnaps", quantity=0.2, date=date),
    ]

    # Convert the items to a pandas DataFrame
    df = sqlmodel_to_df(items)

    # Check the DataFrame
    assert df.shape == (4, 4)
    assert set(df.columns.tolist()) == set(["item", "quantity", "id", "date"])
    assert df["item"].tolist() == ["Milch", "Apfelsaft", "Salami", "Schnaps"]
    assert df["quantity"].tolist() == [
        1.5,
        2.0,
        0.5,
        0.2,
    ]
    assert df["id"].tolist() == [None, None, None, None]
    assert df["date"].tolist() == [date, date, date, date]
