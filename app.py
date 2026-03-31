import streamlit as st
from datetime import time as dt_time
from pathlib import Path
from pawpal_system import Owner, Pet, Task, Scheduler

DATA_FILE = "data.json"


def _to_minutes(t: dt_time) -> int:
    return t.hour * 60 + t.minute


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# --- Session State Setup ---
if "owner" not in st.session_state:
    if Path(DATA_FILE).exists():
        try:
            st.session_state.owner = Owner.load_from_json(DATA_FILE)
        except Exception:
            st.session_state.owner = None
    else:
        st.session_state.owner = None

st.divider()

# --- Section 1: Create Owner ---
st.subheader("1. Create Owner")

owner_name = st.text_input("Owner name")

st.caption("Set the time window when you are available to care for your pets.")
col_a, col_b = st.columns(2)
with col_a:
    avail_start_time = st.time_input("Available from", value=dt_time(8, 0))
with col_b:
    avail_end_time = st.time_input("Available until", value=dt_time(10, 0))

prefers_morning = st.checkbox("I prefer morning tasks")

if st.button("Create Owner"):
    if not owner_name:
        st.error("Please enter an owner name.")
    elif avail_start_time >= avail_end_time:
        st.error("'Available until' must be later than 'Available from'.")
    else:
        st.session_state.owner = Owner(
            owner_name,
            [(_to_minutes(avail_start_time), _to_minutes(avail_end_time))],
            {"prefers_morning": prefers_morning},
        )
        st.success(f"Owner '{owner_name}' created!")

if st.session_state.owner:
    st.caption(f"Current owner: **{st.session_state.owner.name}**")

st.divider()

# --- Section 2: Add a Pet ---
st.subheader("2. Add a Pet")
st.caption("Calls Owner.add_pet() to attach a Pet to your owner.")

pet_name = st.text_input("Pet name")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add Pet"):
    if st.session_state.owner is None:
        st.error("Create an owner first.")
    elif not pet_name:
        st.error("Please enter a pet name.")
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
        task_title = st.text_input("Task title")
    with col2:
        task_time_input = st.time_input("Task time", value=dt_time(8, 0))
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    frequency = st.selectbox("Frequency", ["daily", "twice_daily", "weekly"])

    if st.button("Add Task"):
        if not task_title:
            st.error("Please enter a task title.")
        else:
            selected_pet = next(p for p in st.session_state.owner.pets if p.name == selected_pet_name)
            task = Task(task_title, _to_minutes(task_time_input), frequency, priority)
            selected_pet.add_task(task)
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

# --- Save / Load ---
if st.session_state.owner:
    if st.button("Save data"):
        try:
            st.session_state.owner.save_to_json(DATA_FILE)
            st.success(f"Saved to {DATA_FILE} — your pets and tasks will reload automatically next time.")
        except Exception as e:
            st.error(f"Save failed: {e}")

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
            schedule = scheduler.build_schedule()
            st.session_state.scheduler = scheduler
            st.success(f"Schedule built — {len(schedule)} task(s) ready for today.")
        except ValueError as e:
            st.error(str(e))

if "scheduler" in st.session_state and st.session_state.scheduler.schedule:
    scheduler = st.session_state.scheduler

    # --- Conflict warnings ---
    warnings = scheduler.get_conflict_warnings()
    if warnings:
        st.error(f"⚠️ {len(warnings)} scheduling conflict(s) detected — review before your day starts:")
        for w in warnings:
            st.warning(w)
    else:
        st.success("No scheduling conflicts.")

    st.divider()

    # --- View toggle ---
    view = st.radio("View schedule by:", ["Priority (recommended)", "Time (chronological)"], horizontal=True)

    if view == "Time (chronological)":
        tasks_to_show = scheduler.sort_by_time()
    else:
        tasks_to_show = scheduler.schedule

    # --- Schedule table ---
    PRIORITY_BADGE = {"high": "🔴 high", "medium": "🟡 medium", "low": "🟢 low"}
    rows = []
    for t in tasks_to_show:
        rows.append({
            "Pet": next(
                (p.name for p in scheduler.owner.pets
                 if t in [task for task in p.get_tasks()] or t in scheduler.schedule),
                "—",
            ),
            "Task": t.description,
            "Time": t.format_time(),
            "Priority": PRIORITY_BADGE.get(t.priority, t.priority),
            "Frequency": t.frequency,
            "Status": "✅ done" if t.completed else "⏳ pending",
        })

    # Resolve actual pet name via _task_pet_map
    for i, t in enumerate(tasks_to_show):
        pet_obj = scheduler._task_pet_map.get(id(t))
        rows[i]["Pet"] = pet_obj.name if pet_obj else "—"

    st.dataframe(rows, use_container_width=True)

    # --- Per-pet breakdown ---
    st.subheader("Tasks by pet")
    for pet in scheduler.owner.pets:
        pet_tasks = scheduler.get_tasks_for_pet(pet.name)
        if not pet_tasks:
            st.caption(f"{pet.name} — no tasks in today's schedule")
            continue
        pending = [t for t in pet_tasks if not t.completed]
        done = [t for t in pet_tasks if t.completed]
        with st.expander(f"{pet.name} ({pet.species}) — {len(pending)} pending, {len(done)} done"):
            st.dataframe(
                [{"Task": t.description, "Time": t.format_time(),
                  "Priority": t.priority, "Status": "✅ done" if t.completed else "⏳ pending"}
                 for t in scheduler.sort_by_time() if t in pet_tasks],
                use_container_width=True,
            )
