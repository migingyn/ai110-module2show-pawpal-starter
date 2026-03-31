import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# --- Session State Setup ---
# Check if owner already exists in the session vault before creating a new one
if "owner" not in st.session_state:
    st.session_state.owner = None

st.divider()

# --- Section 1: Create Owner ---
st.subheader("1. Create Owner")

owner_name = st.text_input("Owner name", value="Jordan")

if st.button("Create Owner"):
    st.session_state.owner = Owner(owner_name, [(360, 540), (1080, 1260)], {"prefers_morning": True})
    st.success(f"Owner '{owner_name}' created!")

if st.session_state.owner:
    st.caption(f"Current owner: **{st.session_state.owner.name}**")

st.divider()

# --- Section 2: Add a Pet ---
st.subheader("2. Add a Pet")
st.caption("Calls Owner.add_pet() to attach a Pet to your owner.")

pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add Pet"):
    if st.session_state.owner is None:
        st.error("Create an owner first.")
    else:
        pet = Pet(pet_name, species)
        st.session_state.owner.add_pet(pet)  # Owner.add_pet() handles this
        st.success(f"Added pet '{pet_name}' ({species}) to {st.session_state.owner.name}!")

if st.session_state.owner and st.session_state.owner.pets:
    st.write("Pets:")
    st.table([{"name": p.name, "species": p.species} for p in st.session_state.owner.pets])

st.divider()

# --- Section 3: Add a Task to a Pet ---
st.subheader("3. Schedule a Task")
st.caption("Calls Pet.add_task() to attach a Task to a specific pet.")

if st.session_state.owner and st.session_state.owner.pets:
    pet_names = [p.name for p in st.session_state.owner.pets]
    selected_pet_name = st.selectbox("Select pet", pet_names)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        task_time = st.number_input("Time (minutes since midnight)", min_value=0, max_value=1439, value=420)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    frequency = st.selectbox("Frequency", ["daily", "twice_daily", "weekly"])

    if st.button("Add Task"):
        selected_pet = next(p for p in st.session_state.owner.pets if p.name == selected_pet_name)
        task = Task(task_title, int(task_time), frequency, priority)
        selected_pet.add_task(task)  # Pet.add_task() handles this
        st.success(f"Added task '{task_title}' to {selected_pet_name}!")

    # Show all tasks across all pets
    all_tasks = []
    for pet in st.session_state.owner.pets:
        for t in pet.get_tasks():
            all_tasks.append({
                "pet": pet.name,
                "task": t.description,
                "time": t.format_time(),
                "priority": t.priority,
                "frequency": t.frequency,
                "completed": t.completed,
            })

    if all_tasks:
        st.write("All scheduled tasks:")
        st.table(all_tasks)
    else:
        st.info("No tasks yet. Add one above.")
else:
    st.info("Add a pet first before scheduling tasks.")

st.divider()

# --- Section 4: Generate Schedule ---
st.subheader("4. Generate Today's Schedule")

if st.button("Generate Schedule"):
    if st.session_state.owner is None:
        st.error("Create an owner first.")
    elif not st.session_state.owner.pets:
        st.error("Add at least one pet first.")
    else:
        try:
            scheduler = Scheduler(st.session_state.owner)
            scheduler.build_schedule()
            st.success("Schedule built!")
            st.text(scheduler.explain())
        except ValueError as e:
            st.error(str(e))
