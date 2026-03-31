import streamlit as st
from pawpal_system import Owner, Pet, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# --- Session State Setup ---
# Check if owner already exists in the session vault before creating a new one
if "owner" not in st.session_state:
    st.session_state.owner = None

if "tasks" not in st.session_state:
    st.session_state.tasks = []

st.divider()

st.subheader("Owner & Pet Setup")

owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Create Owner & Pet"):
    pet = Pet(pet_name, species)
    owner = Owner(owner_name, [(360, 540), (1080, 1260)], {"prefers_morning": True})
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.tasks = []
    st.success(f"Created owner '{owner_name}' with pet '{pet_name}'!")

st.divider()

st.subheader("Add Tasks")
st.caption("Tasks are added to the first pet. Create an owner first.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    task_time = st.number_input("Time (minutes since midnight)", min_value=0, max_value=1439, value=420)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

frequency = st.selectbox("Frequency", ["daily", "twice_daily", "weekly"])

if st.button("Add task"):
    if st.session_state.owner is None:
        st.error("Create an owner first before adding tasks.")
    else:
        task = Task(task_title, int(task_time), frequency, priority)
        st.session_state.owner.pets[0].add_task(task)
        st.session_state.tasks.append({
            "title": task_title,
            "time": task_time,
            "priority": priority,
            "frequency": frequency,
        })
        st.success(f"Added task '{task_title}'")

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    st.warning("Not implemented yet. Next step: connect your Scheduler here and display results.")
