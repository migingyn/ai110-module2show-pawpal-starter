from pawpal_system import Task, Pet


def test_mark_complete_changes_status():
    task = Task("Morning walk", 420, "daily", "high")
    assert not task.completed
    task.mark_complete()
    assert task.completed


def test_add_task_increases_pet_task_count():
    pet = Pet("Buddy", "Dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task("Morning walk", 420, "daily", "high"))
    assert len(pet.get_tasks()) == 1
