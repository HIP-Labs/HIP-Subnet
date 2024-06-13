import os
import peewee as pw
import uuid
import base64
import time


# Define Task model
class Task(pw.Model):
    id = pw.UUIDField(primary_key=True, default=uuid.uuid4)
    label = pw.CharField(null=False)
    type = pw.CharField(null=False)
    options = pw.TextField(default="[]")
    value = pw.CharField(default="")
    image = pw.TextField(default="")
    answer = pw.CharField(default="")
    expiry = pw.IntegerField(default=0)

    class Meta:
        database = None  # Will be set later


# Define SQLiteClient class
class SQLiteClient:
    def __init__(self, db_file):
        self.db_file = db_file
        self.db = pw.SqliteDatabase(db_file)
        Task._meta.database = self.db  # type: ignore

    def connect(self):
        self.db.connect(reuse_if_open=True)

    def close(self):
        self.db.close()

    def create_tables(self):
        """
        Create tables in the database. If the tables already exist, do nothing.
        """
        with self.db:
            self.db.create_tables([Task])

    def get_all_unanswered_tasks(self) -> list[dict]:
        """
        Get all tasks from the database where the answer is empty string.
        """
        tasks = Task.select().where(
            Task.answer == ""
            or Task.answer == "null"
            or Task.answer == "undefined"
            or Task.answer == None
        )
        return [
            {
                "id": task.id,
                "label": task.label,
                "type": task.type,
                "options": task.options,
                "value": task.value,
                "image": task.image,
                "expiry": task.expiry,
            }
            for task in tasks
        ]

    def get_task(self, task_id) -> Task | None:
        """
        Get a task with the given task_id. If the task does not exist, return None.
        """
        try:
            task = Task.get(Task.id == task_id)
            return task
        except pw.DoesNotExist:
            print("Task not found.")
            return None

    def insert_task(
        self,
        task_id: str,
        label: str,
        type: str,
        options=None,
        value: str = "",
        image: str = "",
        answer: str = "",
        expiry=time.time() + 180,
    ):
        """
        Insert a new task into the database.
        """
        with self.db.atomic():
            Task.create(
                id=task_id,
                label=label,
                type=type,
                options=options or [],
                value=value,
                image=image,
                answer=answer,
                expiry=expiry,
            )

    def remove_task(self, task_id):
        """
        Remove a task with the given task_id.
        """
        try:
            with self.db.atomic():
                task = Task.get(Task.id == task_id)
                task.delete_instance()
        except pw.DoesNotExist:
            print("Task not found.")

    def update_answer(self, task_id, new_answer):
        """
        Update the answer of a task with the given task_id.
        """
        try:
            with self.db.atomic():
                task = Task.get(Task.id == task_id)
                task.answer = new_answer
                task.save()
        except pw.DoesNotExist:
            print("Task not found.")

    def remove_all_tasks(self):
        """
        Remove all tasks from the database.
        """
        with self.db.atomic():
            Task.delete().execute()

    def remove_expired_tasks(self):
        """
        Remove all tasks that have expired.
        """
        current_time = int(time.time())
        expired_tasks = Task.select().where(Task.expiry <= current_time)
        with self.db.atomic():
            for task in expired_tasks:
                task.delete_instance()

    def check_schema(self):
        """
        Check if the database schema matches the current model.
        If not, remove the database file.
        """
        if os.path.exists(self.db_file):
            try:
                self.db.connect()
                if (
                    not self.db.table_exists("task")
                    or not self.db.get_columns("task") == Task._meta.fields  # type: ignore
                ):
                    os.remove(self.db_file)
            except pw.OperationalError:
                pass
            finally:
                self.db.close()


# Example usage
if __name__ == "__main__":
    current_time = time.time()

    db_file = "tasks.db"
    client = SQLiteClient(db_file)
    client.check_schema()
    client.connect()
    client.create_tables()

    client.insert_task(
        task_id="UUID_OF_TASK_TO_BE_REMOVED",
        label="Task 1",
        type="type1",
        options=["option1", "option2"],
        value="value1",
        image="base64image",
        answer="answer1",
        expiry=int(current_time) + 180,
    )
    client.insert_task(
        task_id="UUID_OF_TASK_TO_BE_UPDATED",
        label="Task 2",
        type="type2",
        value="value2",
        expiry=int(current_time) + 360,
    )

    client.remove_expired_tasks()

    print("Tasks:")
    for task in Task.select():
        print(
            task.id,
            task.label,
            task.type,
            task.options,
            task.value,
            task.image,
            task.answer,
            task.expiry,
        )

    client.remove_task(task_id="UUID_OF_TASK_TO_BE_REMOVED")
    client.update_answer(
        task_id="UUID_OF_TASK_TO_BE_UPDATED", new_answer="updated_answer"
    )

    print("Tasks after removal and update:")
    for task in Task.select():
        print(
            task.id,
            task.label,
            task.type,
            task.options,
            task.value,
            task.image,
            task.answer,
            task.expiry,
        )

    client.close()
