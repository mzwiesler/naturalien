from datetime import datetime
from sqlmodel import SQLModel, Session, create_engine
from naturalien.inventory import (
    InventoryItem,
    add_item,
    delete_item,
    ItemType,
    get_last_n_items_of_inventory,
    sqlmodel_to_df,
)
from naturalien.auth import check_password
import streamlit as st
from sqlalchemy.engine import URL
from sqlalchemy import event
import os
import struct
from azure import identity


SQL_COPT_SS_ACCESS_TOKEN = (
    1256  # Connection option for access tokens, as defined in msodbcsql.h
)
TOKEN_URL = "https://database.windows.net/"  # The token URL for any Azure SQL database

connection_string = os.environ["AZURE_SQL_CONNECTIONSTRING"]


# The provide token function is wrapped to enable local development in docker.
def get_func():
    @event.listens_for(engine, "do_connect")
    def provide_token(dialect, conn_rec, cargs, cparams):
        # remove the "Trusted_Connection" parameter that SQLAlchemy adds
        cargs[0] = cargs[0].replace(";Trusted_Connection=Yes", "")

        # create token credential
        raw_token = azure_credentials.get_token(TOKEN_URL).token.encode("utf-16-le")
        token_struct = struct.pack(f"<I{len(raw_token)}s", len(raw_token), raw_token)

        # apply it to keyword arguments
        cparams["attrs_before"] = {SQL_COPT_SS_ACCESS_TOKEN: token_struct}

    return provide_token


if "UID" in connection_string.upper():
    connection_string = URL.create(
        "mssql+pyodbc", query={"odbc_connect": connection_string}
    )
    engine = create_engine(connection_string, pool_timeout=120)
elif "sqlite:///" in connection_string:
    engine = create_engine(connection_string)
else:
    engine = create_engine(connection_string, pool_timeout=120)
    get_func()


azure_credentials = identity.DefaultAzureCredential()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()

    # Streamlit UI
    st.title("Inventory Management System")

    if not check_password():
        st.stop()  # Do not continue if check_password is not True.

    # Form to add a new item
    with st.form("add_item_form"):
        st.write("Add a new item to the inventory")
        item_name = st.selectbox(
            label="Item Name", options=ItemType.__members__.values()
        )
        item_quantity = st.number_input("Quantity", value=2.5, min_value=0.0, step=0.1)
        submitted = st.form_submit_button("Add Item")
        if submitted:
            with Session(engine) as session:
                inventoryItem = InventoryItem(
                    item=ItemType(item_name),
                    quantity=round(item_quantity, 2),
                    date=datetime.now(),
                )
                add_item(
                    session,
                    inventoryItem,
                )
                st.success(
                    f"Added {item_quantity:.2f} of {item_name} to the inventory."
                )

    # Delete item from the inventory
    with st.form("delete_item_form"):
        st.write("Delete an item from the inventory")
        item_id = int(st.number_input("Item ID", min_value=1, step=1))
        submitted = st.form_submit_button("Delete Item")
        if submitted:
            with Session(engine) as session:
                delete_item(session, item_id)
                st.success(f"Deleted item with ID {item_id} from the inventory.")

    # Display the inventory
    st.write("Current Inventory")
    with Session(engine) as session:
        items = get_last_n_items_of_inventory(session, n=100)
        pd_items = sqlmodel_to_df(items)
        st.dataframe(pd_items, hide_index=True, height=300)

    # To run the Streamlit app, save this script as `inventory_streamlit.py` and run:
    # streamlit run inventory_streamlit.py
