from collections import defaultdict
import json
from name_generator import get_name
import log

log.configure_logging()
logger = log.get_logger(__name__)


class Task:
    name: str
    dependencies: frozenset

    def __init__(self, name=None, dependencies=None):
        self.name = name or get_name()
        self.dependencies = frozenset(dependencies or ())

    def serialize(self):
        return json.dumps({"name": self.name, "dependencies": self.dependencies})

    def run(self):
        return f"{self.name} ran"

    def __repr__(self):
        return f"Task(name='{self.name}')"


def task_tuple_by_name(task_set):
    return tuple(t.name for t in task_set)


def task_tree_for_logging(task_tree):
    return {
        ",".join(task_tuple_by_name(k)): ",".join(task_tuple_by_name(v))
        for k, v in task_tree.items()
    }


class Workflow:
    name: str
    tasks: dict

    def __init__(self, name=None, tasks=None):
        self.name = name or get_name()
        self.tasks = tasks or {}

    def add_task(self, name=None, dependencies=None):
        name = name or get_name()
        self.tasks[name] = Task(name=name, dependencies=dependencies)
        return self.tasks[name]

    def get_execution_tree(self):
        # exec_tree = defaultdict(lambda : set(()))
        exec_tree = {}
        for task_name in self.tasks:
            task = self.tasks[task_name]
            dependency_set = task.dependencies
            # with exec_tree as dict
            exec_tree[dependency_set] = exec_tree.get(dependency_set, set(())).union(
                {task}
            )
            # exec_tree[dependency_set].add({task})
        return exec_tree

    def empty_state(self):
        return {task_name: None for task_name in self.tasks}

    def serialize(self):
        json.dumps(
            {
                "name": self.name,
                "tasks": {k: v.serialize() for k, v in self.tasks.items()},
            }
        )


class Execution:
    workflow: Workflow

    def __init__(self, workflow, state=None):
        self.workflow = workflow
        self.state = state or workflow.empty_state()

    def get_complete_tasks(self):
        return {self.workflow.tasks[k] for k in self.state if self.state[k] is not None}

    def is_complete(self):
        return len(self.get_complete_tasks()) == len(self.workflow.tasks)

    def get_runnable(self):
        complete = self.get_complete_tasks()
        exec_tree = self.workflow.get_execution_tree()
        logger.debug(
            "complete tasks",
            extra={
                "complete": task_tuple_by_name(complete),
                "exec_tree": task_tree_for_logging(exec_tree),
            },
        )
        runnable = set(())
        for dependency_set in exec_tree:
            if dependency_set.issubset(complete) and not exec_tree[
                dependency_set
            ].issubset(complete):
                # logger.debug(f"{exec_tree[dependency_set]} is runnable")
                runnable.update(exec_tree[dependency_set])
        logger.debug("runnable", extra={"runnable": task_tuple_by_name(runnable)})
        return runnable

    def schedule_runnable(self):
        runnable = self.get_runnable()
        logger.info("Running tasks", extra={"runnable": task_tuple_by_name(runnable)})
        for task in runnable:
            output = task.run()
            self.state[task.name] = output


if __name__ == "__main__":
    w = Workflow(name="test_workflow")
    root = w.add_task(name="root")
    two = w.add_task(name="two", dependencies=[root])
    three = w.add_task(name="three", dependencies=[root])
    four = w.add_task(name="four", dependencies=[root])
    five = w.add_task(name="five", dependencies=[two])
    w.add_task(name="six", dependencies=[two, three])
    w.add_task(name="seven", dependencies=[two, three])
    eight = w.add_task(name="eight", dependencies=[four])
    nine = w.add_task(name="nine", dependencies=[four])
    w.add_task(name="ten", dependencies=[five, eight, nine])

    e = Execution(w)

    while not e.is_complete():
        e.schedule_runnable()
